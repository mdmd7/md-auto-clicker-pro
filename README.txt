MD Auto Clicker Pro — GitHub Actions build package

Files to add to the root of your GitHub repository:
- MD_Auto_Clicker_Pro.py
- requirements.txt
- MD_Auto_Clicker_Pro_Setup.iss

Also add the workflow file at:
- .github/workflows/build.yml

If your GitHub repository is named md-auto-clicker-pro, the workflow runs automatically on a push to main, or manually from Actions > Build MD Auto Clicker Pro Installer > Run workflow.

After a successful build, open the workflow run and download the artifact:
MD-Auto-Clicker-Pro-Setup

The artifact contains MD_Auto_Clicker_Pro_Setup.exe. This package has not been run through a Windows build here, so the first workflow run must be checked for errors.
