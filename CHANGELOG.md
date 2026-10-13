# Changelog

All notable changes to Command Hub are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-13

First release with a Windows installer. The app itself keeps every Part 1 feature and gains the fixes below.

### Added

- **Windows installer** (Inno Setup): install for just you (no admin prompt) or for all users
- Start menu entry, optional desktop shortcut, uninstall from Apps & Features
- **About box** (the **i** button): version, and a button that opens the data folder
- **Single-instance lock**, using the same name the installer checks, so Setup asks you to close the app before updating
- **Clear error dialog** and `error.log` instead of a window that silently disappears
- Proper taskbar identity and full version info in Properties → Details
- `build-installer.bat`: builds the `.exe` and the installer, and writes a SHA-256 checksum, in one step
- `app_info.py`: name, version and publisher in one file, read by the app, the `.spec` and the installer

### Changed

- **Your commands now live in `%APPDATA%\EFury Labs\Command Hub`**, not next to the program. This fixes the "PermissionError" when the app is installed in Program Files, and your data now survives updates and uninstalls
- Saving writes to a temporary file and swaps it in, so a crash mid-save cannot corrupt `commands.json`
- A damaged `commands.json` is backed up as `commands.broken-<date>.json` and reported, instead of being overwritten on the next save
- Sample commands are copied to the data folder on the first start

### Notes

- The installer is **not code-signed**, so Windows SmartScreen warns on first run (*More info → Run anyway*). Each release includes a `.sha256.txt` file so the download can be verified
- Windows 10/11 64-bit for the installer; the app still runs from source on Linux and macOS
