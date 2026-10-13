"""Command Hub - app identity.

The ONE place for the name and version. Everything else reads from here:
  * main.py           window title, About box, data folder
  * CommandHub.spec   Windows version info of CommandHub.exe
  * build-installer   passes VERSION to Inno Setup (installer + Apps & Features)

To release a new version: change VERSION, then run build-installer.bat.
"""

APP_NAME = "Command Hub"
APP_ID = "EFuryLabs.CommandHub"          # used for the single-instance lock and the taskbar
EXE_NAME = "CommandHub"                  # CommandHub.exe
VERSION = "1.0.0"                        # MAJOR.MINOR.PATCH - numbers only
PUBLISHER = "EFury Labs"
AUTHOR = "Vijay Bari"
COPYRIGHT = "Copyright (c) 2026 Vijay Bari. MIT License."
DESCRIPTION = "Organize your frequently used commands and copy them with one click."
WEBSITE = "https://efurylabs.com/projects/python-command-hub.html"
REPO = "https://github.com/EFuryLabs/command-hub"
