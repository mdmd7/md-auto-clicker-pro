import ctypes
import os
import json
import threading
import time
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import pyautogui
from pynput import keyboard

# Correct Persian/Arabic shaping and right-to-left display in Tk/CustomTkinter.
# The launcher installs these two small dependencies if they are missing.
import arabic_reshaper
from bidi.algorithm import get_display

# ---------- Appearance ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

app = ctk.CTk()
app.title("MD Auto Clicker Pro")
app.geometry("1120x700")
app.minsize(900, 580)
app.resizable(True, True)

# Plain dark application background; decorative cursor wallpaper removed.

# ---------- State ----------
running = False
stop_event = threading.Event()
click_count = 0
start_key = "f6"
stop_key = "f7"
spam_key = "a"
target_mode = None
capture_target = None
capture_position = False
target_position = None
target_positions = []
capture_point_index = None
point_rows = []
language = "en"
listener = None

TEXT = {
    "fa": {
        "title": "MD Auto Clicker Pro",
        "language": "زبان",
        "click_pattern": "حالت کلیک",
        "single_point": "یک نقطه",
        "multiple_points": "چند نقطه",
        "add_position": "افزودن نقطه",
        "add_point_row": "+", "remove_point_row": "−", "point_limit": "حداقل ۲ و حداکثر ۱۵ نقطه",
        "clear_points": "پاک‌کردن نقاط",
        "points_saved": "تعداد نقاط ثبت‌شده: {}",
        "point_a": "نقطه A", "point_b": "نقطه B", "point_c": "نقطه C", "point_d": "نقطه D", "point_e": "نقطه E",
        "point_set": "ثبت موقعیت", "point_right": "کلیک راست", "point_left": "کلیک چپ", "point_key": "کلید کیبورد", "point_choose_key": "{}", "multi_title": "تنظیم مستقل نقاط (A تا O)", "point_unset": "ثبت نشده",
        "speed": "فاصله بین کلیک‌ها (صدم ثانیه)",
        "speed_hint": "مثال: 5 یعنی هر 0.05 ثانیه یک کلیک",
        "hold": "مدت نگه‌داشتن کلیک",
        "hold_unit": "واحد زمان نگه‌داشتن",
        "hundredths": "صدم ثانیه",
        "seconds": "ثانیه",
        "hold_hint": "پس از رها شدن دکمه، تأخیر سرعت کلیک اعمال می‌شود.",
        "duration": "مدت اجرا (ثانیه)",
        "unlimited": "اجرای نامحدود",
        "left": "کلیک چپ",
        "right": "کلیک راست",
        "start": "شروع",
        "stop": "توقف",
        "start_key": "انتخاب کلید شروع",
        "stop_key": "انتخاب کلید توقف",
        "spam_key": "انتخاب کلید برای تکرار",
        "mouse_mode": "تکرار کلیک ماوس",
        "keyboard_mode": "تکرار کلید کیبورد",
        "mouse_choice": "کلیک راست",
        "left_choice": "کلیک چپ",
        "keyboard_choice": "کلید کیبورد",
        "text_to_type": "متن برای تایپ",
        "text_empty": "لطفاً متنی برای تایپ وارد کن.",
        "spam_key_label": "{}",
        "ready": "آماده",
        "clicking": "در حال کلیک...",
        "stopping": "در حال توقف...",
        "capture": "یک کلید فشار بده (ESC برای لغو)",
        "count": "تعداد کلیک: {}",
        "hotkeys": "کلید شروع: {} | کلید توقف: {}",
        "hotkey_note": "برای لغو انتخاب کلید، ESC را بزن",
        "bad_speed": "سرعت باید عدد صحیح بین 1 تا 1000 باشد.",
        "bad_duration": "مدت اجرا باید عدد صحیح مثبت باشد.",
        "bad_hold": "مدت نگه‌داشتن باید عدد صحیح مثبت باشد.",
        "same_key": "کلید شروع و توقف باید متفاوت باشند.",
        "bad_key": "یک کلید غیر از کلیدهای Shift/Ctrl/Alt انتخاب کن.",
        "failsafe": "توقف ایمنی فعال شد",
        "set_position": "ثبت موقعیت کلیک",
        "lock_position": "قفل موقعیت کلیک",
        "position_unset": "موقعیت ثبت نشده",
        "position_saved": "موقعیت ثبت شد: ({}, {})",
        "position_prompt": "نشانگر را روی نقطه دلخواه ببر و Enter را بزن",
    },
    "en": {
        "title": "MD Auto Clicker Pro",
        "language": "Language",
        "click_pattern": "Click pattern",
        "single_point": "Single point",
        "multiple_points": "Multiple points",
        "add_position": "Add point",
        "add_point_row": "+", "remove_point_row": "−", "point_limit": "Minimum 2, maximum 15 points",
        "clear_points": "Clear points",
        "points_saved": "Saved points: {}",
        "point_a": "Point A", "point_b": "Point B", "point_c": "Point C", "point_d": "Point D", "point_e": "Point E",
        "point_set": "Set position", "point_right": "Right click", "point_left": "Left click", "point_key": "Keyboard key", "point_choose_key": "{}", "multi_title": "Independent point settings (A to O)", "point_unset": "Not set",
        "speed": "Interval between clicks (hundredths of a second)",
        "speed_hint": "Example: 5 means one click every 0.05 seconds",
        "hold": "Mouse button hold duration",
        "hold_unit": "Hold duration unit",
        "hundredths": "Hundredths of a second",
        "seconds": "Seconds",
        "hold_hint": "Click-speed delay starts after the button is released.",
        "duration": "Duration (seconds)",
        "unlimited": "Unlimited duration",
        "left": "Left click",
        "right": "Right click",
        "start": "START",
        "stop": "STOP",
        "start_key": "Choose start key",
        "stop_key": "Choose stop key",
        "spam_key": "Choose key to repeat",
        "mouse_mode": "Repeat mouse click",
        "keyboard_mode": "Repeat keyboard key",
        "mouse_choice": "Right click",
        "left_choice": "Left click",
        "keyboard_choice": "Keyboard key",
        "text_to_type": "Text to type (supports Persian and English)",
        "text_empty": "Please enter text to type.",
        "spam_key_label": "{}",
        "ready": "Ready",
        "clicking": "Clicking...",
        "stopping": "Stopping...",
        "capture": "Press a key (ESC to cancel)",
        "count": "Clicks: {}",
        "hotkeys": "Start key: {} | Stop key: {}",
        "hotkey_note": "Press ESC to cancel key selection",
        "bad_speed": "Speed must be an integer from 1 to 1000.",
        "bad_duration": "Duration must be a positive integer.",
        "bad_hold": "Hold duration must be a positive integer.",
        "same_key": "Start and stop keys must be different.",
        "bad_key": "Choose a key other than Shift/Ctrl/Alt.",
        "failsafe": "Safety stop activated",
        "set_position": "Set click position",
        "lock_position": "Lock click position",
        "position_unset": "Position not set",
        "position_saved": "Position saved: ({}, {})",
        "position_prompt": "Move the pointer to the target and press Enter",
    },
}

def rtl_text(value):
    """Shape Persian letters and apply bidirectional ordering for Tk widgets."""
    if language != "fa" or not value:
        return value
    try:
        return get_display(arabic_reshaper.reshape(value))
    except Exception:
        return value

def tr(key, *args):
    value = TEXT[language][key]
    value = value.format(*args) if args else value
    return rtl_text(value)

def validate_integer(value):
    # Allow an empty field while the user is editing; otherwise digits only.
    return value.isdigit() or value == ""

integer_validator = app.register(validate_integer)

def key_name(key):
    try:
        if key.char is not None:
            return key.char.lower()
    except AttributeError:
        pass
    return getattr(key, "name", str(key).replace("Key.", "")).lower()

# Use pynput's keyboard controller for key output as well as listening. This
# handles special keys (Space, Enter, arrows, F-keys) consistently on Windows.
key_controller = keyboard.Controller()

def key_display_name(name):
    """Readable label for a saved key, including layout-independent VK keys."""
    value = str(name or "")
    if value.startswith("vk:") and "|" in value:
        return value.split("|", 1)[1]
    return value


def key_label_for_active_layout(name):
    """Return the selected virtual key's character in the current Windows layout."""
    value = str(name or "")
    if not value.lower().startswith("vk:") or os.name != "nt" or not hasattr(ctypes, "windll"):
        return key_display_name(value).upper()
    try:
        vk = int(value.split(":", 1)[1].split("|", 1)[0])
        user32 = ctypes.windll.user32
        user32.GetKeyboardLayout.restype = ctypes.c_void_p
        user32.GetKeyboardLayout.argtypes = [ctypes.c_ulong]
        user32.MapVirtualKeyExW.restype = ctypes.c_uint
        user32.MapVirtualKeyExW.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
        user32.ToUnicodeEx.restype = ctypes.c_int
        user32.ToUnicodeEx.argtypes = [
            ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_wchar_p, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p
        ]
        hkl = user32.GetKeyboardLayout(0)
        scan = user32.MapVirtualKeyExW(vk, 0, hkl)
        state = (ctypes.c_ubyte * 256)()
        buffer = ctypes.create_unicode_buffer(8)
        count = user32.ToUnicodeEx(vk, scan, state, buffer, len(buffer), 0, hkl)
        if count > 0 and buffer.value:
            return buffer.value.upper()
    except Exception:
        pass
    return key_display_name(value).upper()


def refresh_key_button_labels():
    """Refresh only the selected-key buttons when the Windows layout changes."""
    try:
        for row in point_rows:
            row["key_button"].configure(
                text=tr("point_choose_key", key_label_for_active_layout(row["key_value"]))
            )
        spam_key_button.configure(
            text=tr("spam_key_label", key_label_for_active_layout(spam_key))
        )
    except (NameError, AttributeError):
        pass
    if app.winfo_exists():
        app.after(500, refresh_key_button_labels)

def resolve_output_key(name):
    """Resolve special keys by name and printable keys by Windows virtual key.

    A virtual key is interpreted by Windows using the *currently active* input
    layout, so the same selected physical key produces Persian or English as
    the user switches the Windows keyboard language.
    """
    if not name:
        raise ValueError("No keyboard key selected")
    normalized = str(name).strip().lower()
    if normalized.startswith("vk:"):
        try:
            vk = int(normalized.split(":", 1)[1].split("|", 1)[0])
            return keyboard.KeyCode.from_vk(vk)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid virtual key: {name}")
    special = getattr(keyboard.Key, normalized, None)
    if special is not None:
        return special
    if len(normalized) == 1:
        return keyboard.KeyCode.from_char(normalized)
    raise ValueError(f"Unsupported keyboard key: {name}")


def capture_output_key(key, fallback_name):
    """Store a printable key's virtual-key code, not its current-layout letter."""
    try:
        if key.char is not None and getattr(key, "vk", None) is not None:
            return f"vk:{int(key.vk)}|{fallback_name}"
    except AttributeError:
        pass
    return fallback_name

def _send_unicode_character(char):
    """Type the exact captured character, independent of the active layout."""
    # Windows' Unicode keyboard input makes a captured Persian character stay
    # Persian even if the current input language changes to English (and vice versa).
    if os.name != "nt" or not hasattr(ctypes, "windll"):
        return False

    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ULONG_PTR)]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", ctypes.c_ulong), ("u", INPUT_UNION)]

    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    events = []
    # Encode as UTF-16 so this also works for characters represented by surrogate pairs.
    encoded = char.encode("utf-16-le")
    units = [encoded[i] | (encoded[i + 1] << 8) for i in range(0, len(encoded), 2)]
    for unit in units:
        events.append(INPUT(type=1, ki=KEYBDINPUT(0, unit, KEYEVENTF_UNICODE, 0, 0)))
    for unit in reversed(units):
        events.append(INPUT(type=1, ki=KEYBDINPUT(0, unit, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0)))
    array_type = INPUT * len(events)
    input_array = array_type(*events)
    sent = ctypes.windll.user32.SendInput(len(events), input_array, ctypes.sizeof(INPUT))
    return sent == len(events)


def press_output_key(name, hold_seconds=0):
    """Press/repeat the exact selected character or a special keyboard key."""
    if not name:
        raise ValueError("No keyboard key selected")

    # A captured printable character should be emitted as that character, not
    # as a physical key interpreted through whatever Windows layout is active now.
    if len(str(name)) == 1 and _send_unicode_character(str(name)):
        if hold_seconds > 0:
            stop_event.wait(hold_seconds)
        return

    output_key = resolve_output_key(name)
    key_controller.press(output_key)
    try:
        if hold_seconds > 0:
            stop_event.wait(hold_seconds)
    finally:
        key_controller.release(output_key)

def set_status(message, color="#86EFAC"):
    status_label.configure(text=message, text_color=color)

def set_settings_locked(locked):
    """Prevent changing run settings while the click worker is active."""
    state = "disabled" if locked else "normal"
    widgets = [
        speed_entry, hold_entry, hold_unit_menu, duration_entry,
        unlimited_check, language_menu, click_pattern_menu,
        start_key_button, stop_key_button, spam_key_button, mode_menu,
        set_position_button, clear_points_button, lock_position_check, text_entry,
        add_point_button, remove_point_button,
    ]
    for row in point_rows:
        widgets.extend([row["position_button"], row["action_menu"], row["key_button"]])
    for widget in widgets:
        try:
            widget.configure(state=state)
        except (tk.TclError, AttributeError):
            pass

def start_clicking():
    global running, click_count

    if running:
        return

    speed_text = speed_entry.get().strip()
    duration_text = duration_entry.get().strip()
    hold_text = hold_entry.get().strip()

    try:
        if not speed_text:
            raise ValueError("speed")
        speed_hundredths = int(speed_text)
        if not 1 <= speed_hundredths <= 1000:
            raise ValueError("speed")

        if not hold_text:
            raise ValueError("hold")
        hold_value = int(hold_text)
        if hold_value <= 0:
            raise ValueError("hold")
        hold_duration = hold_value / 100.0 if hold_unit_var.get() == "hundredths" else float(hold_value)

        if unlimited_var.get():
            duration = None
        else:
            if not duration_text:
                raise ValueError("duration")
            duration = int(duration_text)
            if duration <= 0:
                raise ValueError("duration")
    except ValueError as error:
        if str(error) == "duration":
            messagebox.showerror(tr("title"), tr("bad_duration"))
        elif str(error) == "hold":
            messagebox.showerror(tr("title"), tr("bad_hold"))
        else:
            messagebox.showerror(tr("title"), tr("bad_speed"))
        return

    # Entered number is in hundredths of a second: 5 -> 0.05 seconds.
    interval = speed_hundredths / 100.0
    mode = target_mode_var.get()
    click_pattern = click_pattern_var.get()
    multi_plan = []
    if click_pattern == "multiple":
        for idx, row in enumerate(point_rows):
            pos = row["position"]
            action = row["action_var"].get()
            key_value = row["key_value"]
            # Mouse points need a saved coordinate; keyboard-action rows do not.
            if action in ("left", "right") and pos is None:
                continue
            if action == "key" and not key_value:
                messagebox.showerror(tr("title"), tr("bad_key"))
                return
            multi_plan.append({"position": pos, "action": action, "key": key_value})
        if not multi_plan:
            messagebox.showerror(tr("title"), tr("position_unset"))
            return
    elif mode == "mouse" and lock_position_var.get() and target_position is None:
        messagebox.showerror(tr("title"), tr("position_unset"))
        return
    button = mouse_button.get()
    key_to_spam = spam_key

    click_count = 0
    count_label.configure(text=tr("count", 0))
    stop_event.clear()
    running = True
    start_button.configure(state="disabled")
    set_settings_locked(True)
    stop_button_widget.configure(state="normal")
    set_status(tr("clicking"))

    click_worker.multi_remaining = None
    threading.Thread(
        target=click_worker,
        args=(interval, duration, button, hold_duration, mode, key_to_spam,
              (target_position if mode == "mouse" and lock_position_var.get() else None), multi_plan),
        daemon=True,
    ).start()

def click_worker(interval, duration, button, hold_duration, mode, key_to_spam, locked_position, multi_plan):
    global running, click_count
    started = time.monotonic()

    try:
        while not stop_event.is_set():
            if duration is not None and time.monotonic() - started >= duration:
                break

            # Multi-point mode: visit configured points in A-to-E order, then
            # start again at A. Continue until the global duration expires or
            # the stop key is pressed.
            if click_pattern_var.get() == "multiple":
                did_action = False
                for item in multi_plan:
                    if stop_event.is_set() or (duration is not None and time.monotonic() - started >= duration):
                        break

                    # Only mouse-click actions use the saved screen position.
                    # Keyboard actions press their key without moving the pointer.
                    if item["action"] == "key":
                        press_output_key(item["key"])
                    else:
                        pyautogui.moveTo(item["position"][0], item["position"][1])
                        point_button = "left" if item["action"] == "left" else "right"
                        pyautogui.mouseDown(button=point_button)
                        try:
                            stop_event.wait(hold_duration)
                        finally:
                            pyautogui.mouseUp(button=point_button)

                    did_action = True
                    click_count += 1
                    current_count = click_count
                    app.after(0, lambda n=current_count: count_label.configure(text=tr("count", n)))
                    if stop_event.wait(interval):
                        break

                if stop_event.is_set() or (duration is not None and time.monotonic() - started >= duration):
                    break
                if not did_action:
                    break
                # Finished the pass (including E if configured); begin again at A.
                continue

            # Hold the mouse button for the configured duration, then release it.
            # The speed interval is waited AFTER release, not during the hold.
            if mode == "text":
                # Paste Unicode text from the clipboard so Persian characters are preserved.
                pyautogui.hotkey("ctrl", "v")
                stop_event.wait(hold_duration)
            elif mode == "keyboard":
                press_output_key(key_to_spam, hold_duration)
            else:
                if locked_position is not None:
                    if (isinstance(locked_position, list) and locked_position):
                        point = locked_position[click_count % len(locked_position)]
                    else:
                        point = locked_position
                    pyautogui.moveTo(point[0], point[1])
                pyautogui.mouseDown(button=button)
                try:
                    stop_event.wait(hold_duration)
                finally:
                    pyautogui.mouseUp(button=button)

            if stop_event.is_set():
                break

            click_count += 1
            current_count = click_count
            app.after(
                0,
                lambda n=current_count: count_label.configure(
                    text=tr("count", n)
                ),
            )

            if stop_event.wait(interval):
                break

    except pyautogui.FailSafeException:
        app.after(0, lambda: set_status(tr("failsafe"), "#F87171"))
    finally:
        running = False
        stop_event.set()
        try:
            app.after(0, finish_run)
        except tk.TclError:
            pass

def finish_run():
    set_settings_locked(False)
    start_button.configure(state="normal")
    stop_button_widget.configure(state="disabled")
    if status_label.cget("text") not in (tr("failsafe"),):
        set_status(tr("ready"))

def stop_clicking():
    if running:
        stop_event.set()
        set_status(tr("stopping"), "#FBBF24")

def capture_key(target):
    global capture_target
    capture_target = target
    set_status(tr("capture"), "#FBBF24")

def update_hotkey_text():
    hotkey_label.configure(text=tr("hotkeys", start_key.upper(), stop_key.upper()))
    start_key_button.configure(text=tr("start_key"))
    stop_key_button.configure(text=tr("stop_key"))
    spam_key_button.configure(text=tr("spam_key_label", key_label_for_active_layout(spam_key)))

def on_key_press(key):
    global capture_target, capture_position, target_position, start_key, stop_key, spam_key, capture_point_index

    name = key_name(key)

    if capture_position:
        if name == "enter":
            capture_position = False
            x, y = pyautogui.position()
            if click_pattern_var.get() == "multiple" and capture_point_index is not None:
                point_rows[capture_point_index]["position"] = (x, y)
                idx = capture_point_index
                capture_point_index = None
                app.after(0, lambda i=idx, xx=x, yy=y: point_rows[i]["position_label"].configure(text=f"({xx}, {yy})"))
                app.after(0, save_settings)
            elif click_pattern_var.get() == "multiple":
                target_positions.append((x, y))
                app.after(0, update_position_label)
                app.after(0, save_settings)
            else:
                target_position = (x, y)
                app.after(0, update_position_label)
                app.after(0, save_settings)
            app.after(0, lambda: set_status(tr("ready")))
        return

    if capture_target:
        target = capture_target
        capture_target = None

        if name == "esc":
            app.after(0, update_hotkey_text)
            app.after(0, lambda: set_status(tr("ready")))
            return

        if name in ("shift", "shift_l", "shift_r", "ctrl", "ctrl_l", "ctrl_r",
                    "alt", "alt_l", "alt_r", "cmd", "cmd_l", "cmd_r"):
            app.after(0, lambda: set_status(tr("bad_key"), "#F87171"))
            return

        if isinstance(target, str) and target.startswith("point_key:"):
            try:
                idx = int(target.split(":", 1)[1])
                stored_key = capture_output_key(key, name)
                point_rows[idx]["key_value"] = stored_key
                app.after(0, lambda i=idx, k=key_label_for_active_layout(stored_key): point_rows[i]["key_button"].configure(text=tr("point_choose_key", k)))
                app.after(0, save_settings)
                app.after(0, lambda: set_status(tr("ready")))
            except (ValueError, IndexError):
                app.after(0, lambda: set_status(tr("ready")))
            return

        if target == "spam":
            spam_key = capture_output_key(key, name)
            shown_key = key_label_for_active_layout(spam_key)
            app.after(0, lambda k=shown_key: spam_key_button.configure(text=tr("spam_key_label", k)))
            app.after(0, lambda: set_status(tr("ready")))
            return

        if (target == "start" and name == stop_key) or (
            target == "stop" and name == start_key
        ):
            app.after(0, lambda: set_status(tr("same_key"), "#F87171"))
            return

        if target == "start":
            start_key = name
        else:
            stop_key = name

        app.after(0, update_hotkey_text)
        app.after(0, lambda: set_status(tr("ready")))
        return

    if name == start_key:
        app.after(0, start_clicking)
    elif name == stop_key:
        app.after(0, stop_clicking)
    elif name == "esc":
        app.after(0, close_app)

def change_language(choice):
    global language
    language = "fa" if choice == "فارسی" else "en"

    app.title(tr("title"))
    title_label.configure(text=tr("title"))
    language_label.configure(text=tr("language"))
    click_pattern_label.configure(text=tr("click_pattern"))
    click_pattern_menu.configure(values=[tr("single_point"), tr("multiple_points")])
    click_pattern_menu.set(tr("single_point") if click_pattern_var.get() == "single" else tr("multiple_points"))
    speed_label.configure(text=tr("speed"))
    speed_hint_label.configure(text=tr("speed_hint"))
    hold_label.configure(text=tr("hold"))
    hold_hint_label.configure(text=tr("hold_hint"))
    hold_unit_menu.configure(values=[tr("hundredths"), tr("seconds")])
    hold_unit_menu.set(tr("hundredths") if hold_unit_var.get() == "hundredths" else tr("seconds"))
    duration_label.configure(text=tr("duration"))
    unlimited_check.configure(text=tr("unlimited"))
    set_position_button.configure(text=tr("set_position"))
    lock_position_check.configure(text=tr("lock_position"))
    update_position_label()
    set_position_button.configure(text=tr("add_position") if click_pattern_var.get() == "multiple" else tr("set_position"))
    clear_points_button.configure(text=tr("clear_points"))
    multi_title_label.configure(text=tr("multi_title"))
    add_point_button.configure(text=tr("add_point_row"))
    remove_point_button.configure(text=tr("remove_point_row"))
    point_limit_label.configure(text=tr("point_limit"))
    for row in point_rows:
        row["position_button"].configure(text=tr("point_set"))
        row["action_menu"].configure(values=[tr("point_right"), tr("point_left"), tr("point_key")])
        action_labels = {"right": tr("point_right"), "left": tr("point_left"), "key": tr("point_key")}
        row["action_menu"].set(action_labels.get(row["action_var"].get(), tr("point_right")))
        row["key_button"].configure(text=tr("point_choose_key", key_label_for_active_layout(row["key_value"])))
        toggle_point_key_button(row)
    mode_menu.configure(values=[tr("mouse_choice"), tr("left_choice"), tr("keyboard_choice")])
    if single_action_var.get() == "left":
        mode_menu.set(tr("left_choice"))
    elif single_action_var.get() == "keyboard":
        mode_menu.set(tr("keyboard_choice"))
    else:
        mode_menu.set(tr("mouse_choice"))
    spam_key_button.configure(text=tr("spam_key_label", key_label_for_active_layout(spam_key)))
    toggle_spam_key_button()
    start_button.configure(text=tr("start"))
    stop_button_widget.configure(text=tr("stop"))
    count_label.configure(text=tr("count", click_count))
    update_hotkey_text()
    set_status(tr("ready"))

def close_app():
    # Save preferences automatically before closing.
    try:
        save_settings()
    except Exception as exc:
        try:
            messagebox.showwarning("MD Auto Clicker Pro", f"Could not save settings: {exc}")
        except Exception:
            pass
    stop_event.set()
    if listener:
        listener.stop()
    app.destroy()

# ---------- UI ----------
# Header stays across the top. Main content uses three columns:
# hotkeys on the left, general click settings in the middle, and the
# independent multi-point settings panel on the far right.
title_label = ctk.CTkLabel(
    app, text=tr("title"), font=("Segoe UI", 25, "bold")
)
title_label.pack(pady=(12, 8))

main_layout = ctk.CTkScrollableFrame(app, fg_color="transparent", corner_radius=0)
main_layout.pack(fill="both", expand=True, padx=16, pady=(2, 8))
main_layout.grid_columnconfigure(0, weight=1, uniform="panels")
main_layout.grid_columnconfigure(1, weight=2, uniform="panels")
main_layout.grid_columnconfigure(2, weight=2, uniform="panels")
main_layout.grid_rowconfigure(0, weight=0)

# LEFT COLUMN: hotkey controls
hotkey_card = ctk.CTkFrame(
    main_layout, corner_radius=16, border_width=1, border_color="#26334D"
)
hotkey_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=2)

hotkey_heading = ctk.CTkLabel(
    hotkey_card, text=tr("hotkeys", start_key.upper(), stop_key.upper()),
    font=("Segoe UI", 13, "bold"), wraplength=210
)
hotkey_heading.pack(padx=10, pady=(18, 14))

start_key_button = ctk.CTkButton(
    hotkey_card, text=tr("start_key"),
    command=lambda: capture_key("start"), height=38
)
start_key_button.pack(fill="x", padx=12, pady=6)

stop_key_button = ctk.CTkButton(
    hotkey_card, text=tr("stop_key"),
    command=lambda: capture_key("stop"), height=38
)
stop_key_button.pack(fill="x", padx=12, pady=6)

hotkey_hint = ctk.CTkLabel(
    hotkey_card,
    text="F6 / F7",
    font=("Segoe UI", 12),
    text_color="#A3A3A3"
)
hotkey_hint.pack(pady=(8, 4))

hotkey_note = ctk.CTkLabel(
    hotkey_card,
    text="ESC: cancel key selection",
    font=("Segoe UI", 10),
    text_color="#A3A3A3",
    wraplength=190
)
hotkey_note.pack(padx=8, pady=(0, 12))

# RIGHT COLUMN: settings and click controls
settings_panel = ctk.CTkFrame(main_layout, fg_color="transparent")
settings_panel.grid(row=0, column=1, sticky="nsew", padx=8, pady=2)

# Dedicated right-hand column for independent point settings.
point_panel_container = ctk.CTkFrame(main_layout, fg_color="transparent")
point_panel_container.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=2)

language_row = ctk.CTkFrame(settings_panel, fg_color="transparent")
language_row.pack(fill="x", pady=(0, 5))
language_label = ctk.CTkLabel(language_row, text=tr("language"))
language_label.pack(side="left", padx=(2, 8))
language_menu = ctk.CTkOptionMenu(
    language_row, values=["فارسی", "English"], command=change_language, width=130
)
language_menu.set("English")
language_menu.configure(width=105)
language_menu.pack(side="right", padx=2)
click_pattern_var = tk.StringVar(value="single")
click_pattern_menu = ctk.CTkOptionMenu(
    language_row,
    values=[tr("single_point"), tr("multiple_points")],
    command=lambda choice: change_click_pattern(choice),
    width=125,
)
click_pattern_menu.set(tr("single_point"))
click_pattern_menu.pack(side="right", padx=2)
click_pattern_label = ctk.CTkLabel(language_row, text=tr("click_pattern"))
click_pattern_label.pack(side="left", padx=(2, 4))

speed_label = ctk.CTkLabel(settings_panel, text=tr("speed"))
speed_label.pack(anchor="w", padx=2)
speed_entry = ctk.CTkEntry(
    settings_panel, validate="key", validatecommand=(integer_validator, "%P")
)
speed_entry.insert(0, "1")
speed_entry.pack(fill="x", padx=2, pady=(3, 2))

speed_hint_label = ctk.CTkLabel(
    settings_panel, text=tr("speed_hint"),
    font=("Segoe UI", 10), text_color="#A3A3A3", wraplength=420
)
speed_hint_label.pack(anchor="w", padx=2, pady=(0, 4))

hold_label = ctk.CTkLabel(settings_panel, text=tr("hold"))
hold_label.pack(anchor="w", padx=2)
hold_row = ctk.CTkFrame(settings_panel, fg_color="transparent")
hold_row.pack(fill="x", padx=2, pady=(3, 1))
hold_entry = ctk.CTkEntry(
    hold_row, validate="key", validatecommand=(integer_validator, "%P"), width=100
)
hold_entry.insert(0, "1")
hold_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
hold_unit_var = tk.StringVar(value="hundredths")
hold_unit_menu = ctk.CTkOptionMenu(
    hold_row, values=[tr("hundredths"), tr("seconds")], width=150,
    command=lambda choice: hold_unit_var.set("hundredths" if choice == tr("hundredths") else "seconds")
)
hold_unit_menu.set(tr("hundredths"))
hold_unit_menu.pack(side="right")
hold_hint_label = ctk.CTkLabel(
    settings_panel, text=tr("hold_hint"), font=("Segoe UI", 10),
    text_color="#A3A3A3", wraplength=420
)
hold_hint_label.pack(anchor="w", padx=2, pady=(0, 4))

duration_row = ctk.CTkFrame(settings_panel, fg_color="transparent")
duration_row.pack(fill="x", padx=2, pady=(2, 1))
duration_label = ctk.CTkLabel(duration_row, text=tr("duration"))
duration_label.pack(side="left", padx=(0, 8))

unlimited_var = tk.BooleanVar(value=True)
duration_entry = ctk.CTkEntry(
    settings_panel, validate="key", validatecommand=(integer_validator, "%P")
)
duration_entry.insert(0, "∞")
duration_entry.configure(state="disabled")
duration_entry.pack(fill="x", padx=2, pady=(3, 3))

def toggle_unlimited():
    global duration_before_unlimited
    if unlimited_var.get():
        current = duration_entry.get().strip()
        if current and current != "∞":
            duration_before_unlimited = current
        duration_entry.configure(state="normal", validate="none")
        duration_entry.delete(0, "end")
        duration_entry.insert(0, "∞")
        duration_entry.configure(state="disabled")
    else:
        duration_entry.configure(state="normal", validate="key")
        duration_entry.delete(0, "end")
        duration_entry.insert(0, duration_before_unlimited)

duration_before_unlimited = "60"
unlimited_check = ctk.CTkCheckBox(
    duration_row, text=tr("unlimited"), variable=unlimited_var,
    command=toggle_unlimited
)
unlimited_check.pack(side="right", padx=(4, 0))

mouse_button = tk.StringVar(value="right")
target_mode_var = tk.StringVar(value="mouse")
single_action_var = tk.StringVar(value="right")
mode_row = ctk.CTkFrame(settings_panel, fg_color="transparent")
mode_row.pack(fill="x", pady=(2, 5))
def change_mode(choice):
    if choice in (tr("left_choice"), "Left click"):
        single_action_var.set("left")
        target_mode_var.set("mouse")
        mouse_button.set("left")
    elif choice in (tr("keyboard_choice"), "Keyboard key"):
        single_action_var.set("keyboard")
        target_mode_var.set("keyboard")
        # Keyboard-only mode must never keep a mouse-position lock from a
        # previously selected mouse action.
        lock_position_var.set(False)
    else:
        single_action_var.set("right")
        target_mode_var.set("mouse")
        mouse_button.set("right")
    toggle_spam_key_button()
    if "position_row" in globals():
        toggle_position_controls()

def toggle_spam_key_button():
    if single_action_var.get() == "keyboard" and click_pattern_var.get() == "single":
        spam_key_button.pack(side="left", padx=(6, 2), fill="x", expand=True)
    else:
        spam_key_button.pack_forget()

mode_menu = ctk.CTkOptionMenu(
    mode_row, values=[tr("mouse_choice"), tr("left_choice"), tr("keyboard_choice")],
    width=170, command=change_mode
)
mode_menu.set(tr("mouse_choice"))
mode_menu.pack(side="left", padx=2)
spam_key_button = ctk.CTkButton(
    mode_row, text=tr("spam_key_label", key_label_for_active_layout(spam_key)),
    command=lambda: capture_key("spam"), height=32
)
# Only shown when the keyboard-key action is selected in single-point mode.
toggle_spam_key_button()

# Keep the previous text widgets defined for compatibility with existing callbacks,
# but do not show a text-typing mode in the single-point action selector.
text_label = ctk.CTkLabel(settings_panel, text=tr("text_to_type"))
text_entry = ctk.CTkEntry(settings_panel, placeholder_text=rtl_text("مثلاً: سلام دنیا"))

# Capture one fixed point or add several points to click through in order.
def begin_position_capture(point_index=None):
    global capture_position, capture_point_index
    if running:
        return
    # In single-point mode, choosing a position is available only for mouse clicks
    # and automatically enables the fixed-position option.
    if click_pattern_var.get() == "single":
        if single_action_var.get() == "keyboard":
            return
        lock_position_var.set(True)
        toggle_position_controls()
    elif point_index is not None:
        # In multi-point mode, only left/right-click rows can capture a mouse location.
        if point_rows[point_index]["action_var"].get() not in ("left", "right"):
            return
    capture_position = True
    capture_point_index = point_index
    set_status(tr("position_prompt"), "#FBBF24")

def update_position_label():
    if click_pattern_var.get() == "multiple":
        position_label.configure(text=tr("points_saved", len(target_positions)))
    elif target_position is None:
        position_label.configure(text=tr("position_unset"))
    else:
        position_label.configure(text=tr("position_saved", *target_position))

def clear_saved_points():
    target_positions.clear()
    update_position_label()
    save_settings()

def change_click_pattern(choice):
    if choice == tr("multiple_points") or choice == "Multiple points":
        click_pattern_var.set("multiple")
        lock_position_var.set(True)
    else:
        click_pattern_var.set("single")
    set_position_button.configure(text=tr("add_position") if click_pattern_var.get() == "multiple" else tr("set_position"))
    # The single-point action selector (right click / left click / keyboard key)
    # must be hidden in multiple-point mode; each A-E row has its own action selector.
    if "mode_row" in globals() and "position_row" in globals():
        if click_pattern_var.get() == "multiple":
            mode_row.pack_forget()
        else:
            mode_row.pack(fill="x", pady=(2, 5), before=position_row)
    toggle_position_controls()
    if "multi_panel" in globals():
        if click_pattern_var.get() == "multiple":
            multi_panel.pack(fill="both", expand=True, padx=2, pady=(4, 6))
        else:
            multi_panel.pack_forget()
    update_position_label()
    if "spam_key_button" in globals():
        toggle_spam_key_button()

position_row = ctk.CTkFrame(settings_panel, fg_color="transparent")
position_row.pack(fill="x", pady=(2, 1))
lock_position_var = tk.BooleanVar(value=False)
set_position_button = ctk.CTkButton(
    position_row, text=tr("set_position"), command=begin_position_capture,
    height=34, width=130
)
lock_position_check = ctk.CTkCheckBox(
    position_row, text=tr("lock_position"), variable=lock_position_var,
    command=lambda: toggle_position_controls()
)
lock_position_check.pack(side="left", padx=2)
clear_points_button = ctk.CTkButton(
    position_row, text=tr("clear_points"), command=clear_saved_points,
    height=34, width=105
)
position_label = ctk.CTkLabel(
    settings_panel, text=tr("position_unset"), font=("Segoe UI", 10),
    text_color="#A3A3A3"
)

def toggle_position_controls():
    # Single-point location selection is relevant only to left/right mouse clicks.
    # Multiple-point mode uses each A-E row's own position control.
    if click_pattern_var.get() == "multiple" or single_action_var.get() == "keyboard":
        set_position_button.pack_forget()
        clear_points_button.pack_forget()
        position_label.pack_forget()
        lock_position_check.pack_forget()
        return
    if not lock_position_check.winfo_manager():
        lock_position_check.pack(side="left", padx=2)
    # Keep the position picker visible for either left or right click. Clicking
    # it automatically enables locking; the checkbox can disable fixed positioning.
    set_position_button.pack(side="left", padx=(2, 5), before=lock_position_check)
    clear_points_button.pack_forget()
    position_label.pack(anchor="w", padx=4, pady=(0, 3))

toggle_position_controls()

def toggle_point_key_button(row):
    """Show only controls relevant to the selected action for this point."""
    if row["action_var"].get() == "key":
        row["key_button"].pack(side="left", padx=2)
        row["position_button"].pack_forget()
    else:
        row["key_button"].pack_forget()
        if not row["position_button"].winfo_manager():
            row["position_button"].pack(side="left", padx=2, before=row["action_menu"])

# Dynamic multi-point panel: 2-15 points, defaulting to 5.
# The row list is scrollable so all 15 points remain accessible in the compact window.
POINT_MIN = 2
POINT_MAX = 15
multi_panel = ctk.CTkFrame(point_panel_container, corner_radius=10, border_width=1, border_color="#26334D")
multi_panel.pack(fill="both", expand=True, padx=2, pady=(4, 6))
multi_title_label = ctk.CTkLabel(multi_panel, text=tr("multi_title"), font=("Segoe UI", 12, "bold"))
multi_title_label.pack(anchor="w", padx=8, pady=(6, 4))
point_rows_container = ctk.CTkScrollableFrame(multi_panel, height=205, fg_color="transparent")
point_rows_container.pack(fill="x", padx=3, pady=(0, 2))

point_count_controls = ctk.CTkFrame(multi_panel, fg_color="transparent")
point_count_controls.pack(fill="x", padx=6, pady=(2, 6))
add_point_button = ctk.CTkButton(point_count_controls, text=tr("add_point_row"), width=38, height=30,
                                 command=lambda: add_point_row())
add_point_button.pack(side="left", padx=(0, 5))
remove_point_button = ctk.CTkButton(point_count_controls, text=tr("remove_point_row"), width=38, height=30,
                                    command=lambda: remove_point_row())
remove_point_button.pack(side="left", padx=(0, 8))
point_limit_label = ctk.CTkLabel(point_count_controls, text=tr("point_limit"), text_color="#A3A3A3")
point_limit_label.pack(side="left", padx=2)

def create_point_row(index):
    letter = chr(ord("A") + index)
    row_frame = ctk.CTkFrame(point_rows_container, fg_color="transparent")
    row_frame.pack(fill="x", padx=2, pady=2)
    ctk.CTkLabel(row_frame, text=letter, width=18).pack(side="left", padx=(0, 3))
    pos_label = ctk.CTkLabel(row_frame, text=tr("point_unset"), width=72, text_color="#A3A3A3")
    pos_label.pack(side="left", padx=2)
    pos_button = ctk.CTkButton(row_frame, text=tr("point_set"), width=78, height=28,
                               command=lambda idx=index: begin_position_capture(idx))
    pos_button.pack(side="left", padx=2)
    action_var = tk.StringVar(value="right")

    def on_point_action(choice, var=action_var, idx=index):
        if choice in (tr("point_left"), "Left click"):
            var.set("left")
        elif choice in (tr("point_key"), "Keyboard key"):
            var.set("key")
        else:
            var.set("right")
        toggle_point_key_button(point_rows[idx])
        save_settings()

    action_menu = ctk.CTkOptionMenu(
        row_frame, values=[tr("point_right"), tr("point_left"), tr("point_key")],
        width=100, height=28, command=on_point_action
    )
    action_menu.set(tr("point_right"))
    action_menu.pack(side="left", padx=2)
    key_value = "a"
    key_button = ctk.CTkButton(
        row_frame, text=tr("point_choose_key", key_label_for_active_layout(key_value)), width=72, height=28,
        command=lambda idx=index: capture_key(f"point_key:{idx}")
    )
    row = {"position": None, "position_label": pos_label, "action_var": action_var,
           "action_menu": action_menu, "key_value": key_value, "key_button": key_button,
           "position_button": pos_button, "letter": letter, "row_frame": row_frame}
    point_rows.append(row)
    toggle_point_key_button(row)
    return row

def update_point_count_controls():
    add_point_button.configure(state="normal" if len(point_rows) < POINT_MAX else "disabled")
    remove_point_button.configure(state="normal" if len(point_rows) > POINT_MIN else "disabled")

def add_point_row():
    if running or len(point_rows) >= POINT_MAX:
        return
    create_point_row(len(point_rows))
    update_point_count_controls()
    save_settings()


def remove_point_row():
    if running or len(point_rows) <= POINT_MIN:
        return
    row = point_rows.pop()
    try:
        row["row_frame"].destroy()
    except tk.TclError:
        pass
    update_point_count_controls()
    save_settings()

for _ in range(5):
    create_point_row(len(point_rows))
update_point_count_controls()

if click_pattern_var.get() != "multiple":
    multi_panel.pack_forget()

controls = ctk.CTkFrame(settings_panel, fg_color="transparent")
controls.pack(fill="x", pady=(5, 7))

start_button = ctk.CTkButton(
    controls, text=tr("start"), command=start_clicking, height=38
)
start_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

stop_button_widget = ctk.CTkButton(
    controls, text=tr("stop"), command=stop_clicking,
    state="disabled", fg_color="#991B1B", height=38
)
stop_button_widget.pack(side="left", expand=True, fill="x", padx=(5, 0))

count_label = ctk.CTkLabel(settings_panel, text=tr("count", 0))
count_label.pack(pady=(3, 2))

status_label = ctk.CTkLabel(
    settings_panel, text=tr("ready"), text_color="#86EFAC"
)
status_label.pack(pady=(2, 5))

footer_label = ctk.CTkLabel(
    app, text="MD Auto Clicker Pro",
    font=("Segoe UI", 10), text_color="#777777"
)
footer_label.pack(pady=(0, 6))

def update_hotkey_text():
    hotkey_heading.configure(
        text=tr("hotkeys", start_key.upper(), stop_key.upper())
    )
    start_key_button.configure(text=tr("start_key"))
    stop_key_button.configure(text=tr("stop_key"))
    spam_key_button.configure(text=tr("spam_key_label", key_label_for_active_layout(spam_key)))

# Update language-dependent labels, including the left hotkey panel.
_original_change_language = change_language
def change_language(choice):
    global language
    language = "fa" if choice == "فارسی" else "en"
    app.title(tr("title"))
    title_label.configure(text=tr("title"))
    language_label.configure(text=tr("language"))
    click_pattern_label.configure(text=tr("click_pattern"))
    click_pattern_menu.configure(values=[tr("single_point"), tr("multiple_points")])
    click_pattern_menu.set(tr("single_point") if click_pattern_var.get() == "single" else tr("multiple_points"))
    speed_label.configure(text=tr("speed"))
    speed_hint_label.configure(text=tr("speed_hint"))
    hold_label.configure(text=tr("hold"))
    hold_hint_label.configure(text=tr("hold_hint"))
    hold_unit_menu.configure(values=[tr("hundredths"), tr("seconds")])
    hold_unit_menu.set(tr("hundredths") if hold_unit_var.get() == "hundredths" else tr("seconds"))
    duration_label.configure(text=tr("duration"))
    unlimited_check.configure(text=tr("unlimited"))
    set_position_button.configure(text=tr("set_position"))
    lock_position_check.configure(text=tr("lock_position"))
    update_position_label()
    set_position_button.configure(text=tr("add_position") if click_pattern_var.get() == "multiple" else tr("set_position"))
    clear_points_button.configure(text=tr("clear_points"))
    multi_title_label.configure(text=tr("multi_title"))
    add_point_button.configure(text=tr("add_point_row"))
    remove_point_button.configure(text=tr("remove_point_row"))
    point_limit_label.configure(text=tr("point_limit"))
    for row in point_rows:
        row["position_button"].configure(text=tr("point_set"))
        row["action_menu"].configure(values=[tr("point_right"), tr("point_left"), tr("point_key")])
        action_labels = {"right": tr("point_right"), "left": tr("point_left"), "key": tr("point_key")}
        row["action_menu"].set(action_labels.get(row["action_var"].get(), tr("point_right")))
        row["key_button"].configure(text=tr("point_choose_key", key_label_for_active_layout(row["key_value"])))
        toggle_point_key_button(row)
    mode_menu.configure(values=[tr("mouse_choice"), tr("left_choice"), tr("keyboard_choice")])
    if single_action_var.get() == "left":
        mode_menu.set(tr("left_choice"))
    elif single_action_var.get() == "keyboard":
        mode_menu.set(tr("keyboard_choice"))
    else:
        mode_menu.set(tr("mouse_choice"))
    spam_key_button.configure(text=tr("spam_key_label", key_label_for_active_layout(spam_key)))
    toggle_spam_key_button()
    start_button.configure(text=tr("start"))
    stop_button_widget.configure(text=tr("stop"))
    count_label.configure(text=tr("count", click_count))
    hotkey_note.configure(text=tr("hotkey_note"))
    update_hotkey_text()
    set_status(tr("ready"))

# ---------- Automatic settings persistence ----------
_SETTINGS_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "MD Auto Clicker Pro")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")

def save_settings():
    data = {
        "language": language,
        "geometry": app.geometry(),
        "start_key": start_key,
        "stop_key": stop_key,
        "spam_key": spam_key,
        "click_pattern": click_pattern_var.get(),
        "speed": speed_entry.get(),
        "hold": hold_entry.get(),
        "hold_unit": hold_unit_var.get(),
        "unlimited": unlimited_var.get(),
        "duration": duration_entry.get() if not unlimited_var.get() else "",
        "single_action": single_action_var.get(),
        "mode": mode_menu.get(),
        "target_position": target_position,
        "target_positions": target_positions,
        "points": [{"position": row["position"], "action": row["action_var"].get(), "key": row["key_value"]} for row in point_rows],
    }
    os.makedirs(_SETTINGS_DIR, exist_ok=True)
    temp_file = _SETTINGS_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_file, _SETTINGS_FILE)

def load_settings():
    global language, start_key, stop_key, spam_key, target_position, target_positions
    try:
        with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError, TypeError):
        return
    try:
        language = data.get("language", "en") if data.get("language") in ("en", "fa") else "en"
        start_key = str(data.get("start_key", start_key))
        stop_key = str(data.get("stop_key", stop_key))
        spam_key = str(data.get("spam_key", spam_key))
        click_pattern_var.set(data.get("click_pattern", "single"))
        speed_entry.delete(0, "end"); speed_entry.insert(0, str(data.get("speed", "1")))
        hold_entry.delete(0, "end"); hold_entry.insert(0, str(data.get("hold", "1")))
        hold_unit_var.set(data.get("hold_unit", "hundredths"))
        hold_unit_menu.set(tr("hundredths") if hold_unit_var.get() == "hundredths" else tr("seconds"))
        unlimited_var.set(bool(data.get("unlimited", True)))
        if not unlimited_var.get():
            duration_entry.configure(state="normal")
            duration_entry.delete(0, "end"); duration_entry.insert(0, str(data.get("duration", "60")))
        else:
            duration_entry.configure(state="disabled")
            duration_entry.delete(0, "end"); duration_entry.insert(0, "∞")
        single_action_var.set(data.get("single_action", "right"))
        action_labels = {"right": tr("mouse_choice"), "left": tr("left_choice"), "keyboard": tr("keyboard_choice")}
        mode_menu.set(action_labels.get(single_action_var.get(), tr("mouse_choice")))
        target_position = data.get("target_position")
        target_positions = data.get("target_positions", [])
        saved_points = data.get("points", [])
        while len(point_rows) < min(max(len(saved_points), POINT_MIN), POINT_MAX):
            create_point_row(len(point_rows))
        while len(point_rows) > min(max(len(saved_points), POINT_MIN), POINT_MAX):
            row = point_rows.pop(); row["row_frame"].destroy()
        for row, saved in zip(point_rows, saved_points):
            row["position"] = saved.get("position")
            row["action_var"].set(saved.get("action", "right"))
            row["key_value"] = saved.get("key", "a")
            row["action_menu"].set({"right": tr("point_right"), "left": tr("point_left"), "key": tr("point_key")}.get(row["action_var"].get(), tr("point_right")))
            row["key_button"].configure(text=tr("point_choose_key", key_label_for_active_layout(row["key_value"])))
            toggle_point_key_button(row)
            if row["position"]:
                row["position_label"].configure(text=f"{row['position'][0]}, {row['position'][1]}")
        update_point_count_controls()
        change_click_pattern(tr("multiple_points") if click_pattern_var.get() == "multiple" else tr("single_point"))
        language_menu.set("فارسی" if language == "fa" else "English")
        change_language("فارسی" if language == "fa" else "English")
        saved_geometry = data.get("geometry")
        if saved_geometry:
            app.geometry(saved_geometry)
    except (tk.TclError, ValueError, TypeError, KeyError):
        # Ignore invalid or outdated individual settings and keep safe defaults.
        pass

load_settings()
update_hotkey_text()

# Periodic autosave catches changes in fields that do not have dedicated callbacks.
def periodic_settings_autosave():
    try:
        save_settings()
    except (OSError, tk.TclError, ValueError, TypeError):
        pass
    try:
        app.after(1000, periodic_settings_autosave)
    except tk.TclError:
        pass

app.after(1000, periodic_settings_autosave)
listener = keyboard.Listener(on_press=on_key_press)
listener.start()

app.protocol("WM_DELETE_WINDOW", close_app)
app.after(500, refresh_key_button_labels)
app.mainloop()
