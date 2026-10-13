# How the build files were written and how to make them for your own project

Covers the three files that turn `main.py` into an installer:

| File | Tool | Job |
|---|---|---|
| `CommandHub.spec` | PyInstaller | Python script → `CommandHub.exe` (+ its folder) |
| `installer\CommandHub.iss` | Inno Setup | that folder → `CommandHub-Setup-1.0.0.exe` |
| `build-installer.bat` | Windows batch | runs both, in the right order, every time the same |

**The order they were written in, and why:** do it by hand first, then write it down. Every one of these files started as a command typed by hand. Once it worked, it was saved into a file so it can be repeated. You can explain it the same way: *"First I ran PyInstaller by hand. Then I put the options into a .spec file. Then I made an installer with the Inno wizard and cleaned up the script. Last, a .bat file runs everything."*

---

## 1. `CommandHub.spec`: the PyInstaller recipe

### Where a .spec comes from
When you run PyInstaller with options, for example
```bat
pyinstaller --windowed --icon assets\app.ico --name CommandHub main.py
```
it **writes a `CommandHub.spec` file** with those options and then builds from it. You can also create one without building:
```bat
pyi-makespec --windowed --icon assets\app.ico --name CommandHub main.py
```
So the starting point is always generated. Then you edit it, because a .spec is **plain Python** and can do things command-line options can't (like reading the version from `app_info.py`). From then on you only run:
```bat
pyinstaller --noconfirm --clean CommandHub.spec
```

### Walkthrough (top to bottom)
| Part | What it does | Why it's written this way |
|---|---|---|
| `sys.path.insert(0, SPECPATH)` + `import app_info as info` | Lets the spec read the name and version | `SPECPATH` is a variable PyInstaller provides: the folder of the .spec. The version is then typed only once. |
| **1. Version info** (writes `build\version_info.txt`) | The text Windows shows in *Properties → Details* | PyInstaller expects this in a special format (`VSVersionInfo`). We generate it from `app_info.py`, so it's never out of date. `1.0.0` becomes `(1, 0, 0, 0)` because Windows wants 4 numbers. |
| **2. `Analysis([...])`** | Finds your code and everything it imports | `["main.py"]` = entry point. **`datas=`** = extra non-Python files to include: `(source, folder inside the app)`. The icon goes to `assets`, sample commands to `defaults`. `main.py` finds them through `resource_path()`. `excludes=` drops modules we don't use, so the app is smaller. |
| `PYZ(a.pure)` | Packs all Python modules into one archive | Standard line, never needs changing. |
| **3. `EXE(...)`** | Makes `CommandHub.exe` | `exclude_binaries=True` = one-folder build. `console=False` = no black console window (GUI app). `icon=` = the .exe file's icon. `version=` = the details from step 1. `upx=False` = no extra compression (antivirus dislikes UPX). |
| **4. `COLLECT(...)`** | Puts the .exe + DLLs + data into `dist\CommandHub\` | This is what makes it a one-folder build. Without `COLLECT` (and with `exclude_binaries=False`) you get `--onefile`. |

### Adapting it to your project
1. In `app_info.py`: change `APP_NAME`, `EXE_NAME`, `VERSION`, `PUBLISHER`, `COPYRIGHT`. (Or, if you don't use `app_info.py`, type the values straight into the spec.)
2. `Analysis(["main.py"])` → your entry script.
3. `datas=` → every non-Python file your app opens: images, JSON, sounds, templates.
   - Format: `("path/in/project", "folder/in/app")`. A whole folder: `("images", "images")`.
   - In your code, open them with a `resource_path()` helper like the one in `main.py`, **not** with a plain relative path.
4. `icon=` → your `.ico` file. (It must be `.ico`. PNG works only if `Pillow` is installed.)
5. Console app (no GUI)? Set `console=True`.
6. Missing module at runtime (`ModuleNotFoundError` only in the .exe)? Add it to `hiddenimports=["module_name"]`. This happens with modules imported dynamically.

**Test:** run `dist\YourApp\YourApp.exe` **from a different folder** (e.g. double-click it in Explorer). If it only works from the project folder, a file is opened with a relative path somewhere. Fix it with `resource_path()` (for bundled files) or AppData (for user data).

---

## 2. `installer\CommandHub.iss`: the Inno Setup script

### Where an .iss comes from
Inno Setup has a **Script Wizard**: *File → New* → answer the questions (app name, version, publisher, the .exe, other files, licence, icons, languages) → it writes a complete `.iss`. That's how you should start for a new project.

This one started from the wizard's output, then was cleaned up:
- names moved into `#define` lines at the top,
- the version read from the .exe instead of typed,
- the "just me / all users" choice, the "close the app first" check and the "delete my data?" question added,
- comments added.

### How the file is organised
An .iss has **two kinds of lines**:
- `#define`, `#if`, `#error`: the **preprocessor**. It runs *before* compiling, like find-and-replace. `{#AppName}` gets replaced with `Command Hub`.
- `[Sections]` with `Key=Value` or `Name: ...; Parameter: ...` lines: what the installer does.

And **constants** in `{curly braces}` that Inno replaces **on the user's PC** at install time:

| Constant | Becomes |
|---|---|
| `{app}` | the folder the user installs into |
| `{autopf}` | `C:\Program Files` (all users) or `%LOCALAPPDATA%\Programs` (just me) |
| `{autoprograms}` | Start menu → Programs (for all users or just you) |
| `{autodesktop}` | the desktop (all users or just you) |
| `{userappdata}` | `%APPDATA%` of the user: where Command Hub keeps its data |

### Walkthrough
| Part | What it does | Notes |
|---|---|---|
| `#define AppName … AppMutexName` | Names in one place | Change these for your project. |
| `#define BuiltApp` + `#if !FileExists … #error` | Stops compiling with a clear message if `dist\…\CommandHub.exe` doesn't exist | Otherwise you'd get a confusing "file not found" later. |
| `#ifndef AppVersion` → `GetStringFileInfo(...)` | Version: from `/DAppVersion=` (passed by the .bat) or read from the .exe's details | Version is never typed in the .iss. |
| `[Setup] AppId={{GUID}` | The app's permanent identity | The double `{{` is needed because `{` normally starts a constant. **New project = new GUID, then never change it.** |
| `AppName`, `AppVersion`, `AppPublisher`, URLs, `AppCopyright` | What Apps & Features shows | |
| `VersionInfo…` | Details of `Setup.exe` itself | |
| `DefaultDirName={autopf}\{#AppPublisher}\{#AppName}` | Default install folder | `UsePreviousAppDir=yes` = upgrades reuse the old folder. |
| `PrivilegesRequired=lowest` + `PrivilegesRequiredOverridesAllowed=dialog` | Shows "Install for all users / for me only" | `lowest` = default needs no admin. Remove the second line to always install just for the user. Use `PrivilegesRequired=admin` to always install for all users. |
| `ArchitecturesAllowed=x64compatible`, `…InstallIn64BitMode`, `MinVersion=10.0` | 64-bit Windows 10+ only | Matches a 64-bit Python build. |
| `WizardStyle=modern`, `LicenseFile`, `SetupIconFile` | Look of the wizard | Paths are relative to the .iss: `..\LICENSE` = one folder up. |
| `UninstallDisplayIcon` | Icon in Apps & Features | |
| `AppMutex` + `CloseApplications=yes` | If the app is running, ask to close it | The name must equal the mutex the app creates (`APP_ID` in `app_info.py`). |
| `OutputDir`, `OutputBaseFilename`, `Compression` | Output file name and compression | |
| `[Languages]` | Wizard language | Add more lines for other languages. |
| `[Tasks]` | Optional checkboxes on the wizard | `Flags: unchecked` = off by default. |
| `[Files]` | What gets copied | `dist\CommandHub\*` with `recursesubdirs createallsubdirs` = the whole folder. `ignoreversion` = always overwrite on upgrade. |
| `[Icons]` | Shortcuts | `Tasks: desktopicon` = only if that box was ticked. |
| `[Run]` | "Launch Command Hub" on the last page | `postinstall` = a checkbox on the Finish page. `skipifsilent` = not during silent installs. |
| `[Code]` | Pascal code for special behaviour | `CurUninstallStepChanged` runs during uninstall. At `usPostUninstall` it asks about the data folder. `MB_DEFBUTTON2` = **No** is the default, and `IDNO` is the answer for silent uninstalls: never delete user data by accident. |

### Adapting it to your project
1. **Start with the wizard** (*File → New*), or copy this file and change:
   - the `#define` lines (name, publisher, exe name, URLs, mutex name),
   - the `BuiltApp` path (`dist\YourApp\YourApp.exe`),
   - the `[Files]` source folder.
2. **New `AppId`**: in the Inno Setup IDE choose *Tools → Generate GUID* (or PowerShell `[guid]::NewGuid()`). Paste it as `AppId={{YOUR-GUID}`. **Never reuse Command Hub's GUID**: Windows would think it's the same app.
3. Your app doesn't use a mutex? Delete the `AppMutex` line.
4. Your app keeps data in a different folder? Change the path in `[Code]`, or delete the whole `[Code]` section if it keeps no data.
5. Need a desktop shortcut always? Remove `Tasks: desktopicon` from the `[Icons]` line and delete `[Tasks]`.
6. Compile: *Build → Compile* (Ctrl+F9), or `ISCC.exe installer\YourApp.iss`.

Full reference for every key: https://jrsoftware.org/ishelp/

---

## 3. `build-installer.bat`: the one-click build

### How it was written
It's the same commands you type by hand, in order, with checks after each one:
```bat
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt -r requirements-build.txt
venv\Scripts\python -m PyInstaller --noconfirm --clean CommandHub.spec
"C:\Program Files\Inno Setup 7\ISCC.exe" installer\CommandHub.iss
certutil -hashfile installer\Output\CommandHub-Setup-1.0.0.exe SHA256
```
Then the questions: *what if Python is missing? What if a step fails? Where is Inno installed? Where does the version come from?* Each answer became a few lines.

### Batch-file basics used in it (explain these on camera)
| Line | Meaning |
|---|---|
| `@echo off` | Don't print every command, only our messages |
| `setlocal EnableExtensions` | Variables we set disappear when the script ends (doesn't pollute your terminal) |
| `cd /d "%~dp0"` | Go to **the folder this .bat is in**. `%~dp0` = drive + path of the script. Works even when double-clicked from anywhere. |
| `if errorlevel 1 goto :fail` | Every program returns an exit code; non-zero = failed. Stop immediately instead of continuing with a broken build. |
| `if not exist "…" (…)` | Only create the venv the first time |
| `py -3 … \|\| python …` | Finds Python: the `py` launcher first (python.org installs it), then `python` |
| `call %%PY%% -m venv venv` | `%PY%` inside `( … )` would be read *before* the block runs (still empty). `call` + `%%PY%%` reads it at run time. A classic batch trap. |
| `for /f … in (\`call "%VPY%" -c "import app_info; print(app_info.VERSION)"\`) do set "VERSION=%%V"` | Runs Python, captures its output into a variable. This is how the version gets from `app_info.py` into the batch file. (`call` stops `for /f` from mangling the quotes.) |
| `for %%P in ("…7\ISCC.exe" "…") do if exist %%P …` | Tries the usual Inno Setup install folders, then `where ISCC.exe` (PATH) |
| `"%ISCC%" /Q "/DAppVersion=%VERSION%" …` | `/D` = defines `AppVersion` for the .iss preprocessor; `/Q` = quiet |
| `certutil -hashfile … SHA256` | Built into Windows: computes the checksum |
| `explorer "installer\Output"` | Opens the folder at the end |
| `pause` | Keeps the window open so you can read the result |

**`%%V` vs `%V`:** inside a .bat, loop variables need two `%`. Typed directly in a terminal, one.

### Adapting it to your project
1. Search-replace `CommandHub` with your exe name (spec file name, `dist\…` paths, output file name).
2. If you don't use `app_info.py`, replace the `for /f` line with `set "VERSION=1.0.0"`.
3. Change the `.iss` path in the `ISCC` line.
4. Keep the structure: **one numbered step = one echo + the command + `if errorlevel 1 goto :fail`.**

---

## 4. Checklist: making an installer for any Python GUI app

1. **Make the app installer-ready**
   - [ ] Bundled files opened via `resource_path()` (`sys._MEIPASS`)
   - [ ] User data written to `%APPDATA%\Publisher\App`, never next to the .exe
   - [ ] No `print()`/`input()` needs (no console in a windowed app); errors shown in a dialog or written to a log
   - [ ] An `.ico` icon (16, 32, 48, 256 px inside)
   - [ ] Version in one place
2. **PyInstaller:** `pyi-makespec --windowed --icon … --name … main.py` → add `datas`, version info → build → test the .exe from another folder.
3. **Inno Setup:** *File → New* (wizard) → new GUID → point `[Files]` at `dist\YourApp\*` → compile → test in Windows Sandbox.
4. **Automate:** a .bat (or PowerShell) that does steps 2–3 with error checks.
5. **Release:** GitHub Release with the Setup.exe + SHA-256; mention the SmartScreen warning if it isn't signed.

## Further reading
- PyInstaller spec files: https://pyinstaller.org/en/stable/spec-files.html
- PyInstaller "run-time information" (`sys._MEIPASS`, `sys.frozen`): https://pyinstaller.org/en/stable/runtime-information.html
- Inno Setup help (every section and constant): https://jrsoftware.org/ishelp/
- Inno Setup example scripts: in the Inno install folder → `Examples\`
