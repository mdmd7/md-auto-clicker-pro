# Inno Setup script for MD Auto Clicker Pro
#define MyAppName "MD Auto Clicker Pro"
#define MyAppVersion "1.0.0"
#define MyAppExeName "MD Auto Clicker Pro.exe"

[Setup]
AppId={{C0F9C14E-25D2-4AA7-A2E6-7A87B4ECA15D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\MD Auto Clicker Pro
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=MD_Auto_Clicker_Pro_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
