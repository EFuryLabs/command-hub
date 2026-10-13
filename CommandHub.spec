# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller build file for Command Hub.
#   pyinstaller --noconfirm --clean CommandHub.spec
# Output: dist\CommandHub\CommandHub.exe  (+ an _internal folder it needs)
#
# A .spec file is plain Python. It reads the name and version from
# app_info.py, so the version is typed in ONE place only.

import os
import sys

sys.path.insert(0, SPECPATH)            # SPECPATH = the folder of this file
import app_info as info

# ---- 1. Windows "Properties > Details" information for CommandHub.exe ----
nums = [int(n) for n in info.VERSION.split(".")]
nums = tuple((nums + [0, 0, 0, 0])[:4])                  # 1.0.0 -> (1, 0, 0, 0)

os.makedirs("build", exist_ok=True)
version_file = os.path.join("build", "version_info.txt")
with open(version_file, "w", encoding="utf-8") as f:
    f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', {info.PUBLISHER!r}),
      StringStruct('FileDescription', {info.APP_NAME!r}),
      StringStruct('FileVersion', {info.VERSION!r}),
      StringStruct('InternalName', {info.EXE_NAME!r}),
      StringStruct('LegalCopyright', {info.COPYRIGHT!r}),
      StringStruct('OriginalFilename', {info.EXE_NAME + '.exe'!r}),
      StringStruct('ProductName', {info.APP_NAME!r}),
      StringStruct('ProductVersion', {info.VERSION!r})])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")

# ---- 2. What goes into the app ----
a = Analysis(
    ["main.py"],
    pathex=[SPECPATH],
    datas=[
        ("assets/app.ico", "assets"),         # window + taskbar icon
        ("commands.json", "defaults"),        # sample commands, copied on first run
    ],
    hiddenimports=[],
    excludes=["tkinter", "unittest", "pydoc", "test"],   # not used: smaller app
    noarchive=False,
)

pyz = PYZ(a.pure)

# ---- 3. The .exe ----
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,       # one-folder build (faster start, fewer antivirus flags)
    name=info.EXE_NAME,
    console=False,               # GUI app: no black console window
    icon="assets/app.ico",       # icon of the .exe file itself
    version=version_file,        # Properties > Details
    upx=False,                   # UPX-compressed exes are flagged more by antivirus
)

# ---- 4. The folder: dist\CommandHub\ ----
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name=info.EXE_NAME,
    upx=False,
)
