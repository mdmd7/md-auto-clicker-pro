MD Auto Clicker Pro - GitHub build package

Upload/replace these files in the root of your GitHub repository, preserving:
- MD_Auto_Clicker_Pro.py
- requirements.txt
- MD_Auto_Clicker_Pro_Setup.iss
- .github/workflows/build.yml

The workflow installs arabic-reshaper and python-bidi, then builds the EXE and installer.
After committing the files, open Actions and check the latest run. Download the installer from the Artifacts section of a successful run.
