@echo off
rem ==================================================================
rem  Command Hub - build CommandHub.exe and the Windows installer.
rem  Double-click this file in the command-hub folder.
rem
rem  Needs (one time): Python 3.10+ and Inno Setup 7 (jrsoftware.org).
rem  Output: installer\Output\CommandHub-Setup-<version>.exe (+ .sha256.txt)
rem ==================================================================
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo  Command Hub - installer build
echo  =============================

rem ---------- 1. Python + build virtual environment ----------
echo.
echo  [1/5] Python environment (venv)
if not exist "venv\Scripts\python.exe" (
    set "PY="
    py -3 --version >nul 2>&1 && set "PY=py -3"
    if not defined PY python --version >nul 2>&1 && set "PY=python"
    if not defined PY (
        echo  [X] Python 3 not found. Install it from https://www.python.org/downloads/
        goto :fail
    )
    call %%PY%% -m venv venv
    if errorlevel 1 goto :fail
)
set "VPY=%~dp0venv\Scripts\python.exe"
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements.txt -r requirements-build.txt
if errorlevel 1 goto :fail

rem ---------- 2. version from app_info.py ----------
for /f "usebackq delims=" %%V in (`call "%VPY%" -c "import app_info; print(app_info.VERSION)"`) do set "VERSION=%%V"
if not defined VERSION goto :fail
echo  Version: %VERSION%

rem ---------- 3. PyInstaller ----------
echo.
echo  [2/5] Building CommandHub.exe with PyInstaller
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
"%VPY%" -m PyInstaller --noconfirm --clean CommandHub.spec
if errorlevel 1 goto :fail
if not exist "dist\CommandHub\CommandHub.exe" (
    echo  [X] dist\CommandHub\CommandHub.exe was not created.
    goto :fail
)

rem ---------- 4. Inno Setup ----------
echo.
echo  [3/5] Looking for Inno Setup
set "ISCC="
for %%P in (
    "%ProgramFiles%\Inno Setup 7\ISCC.exe"
    "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
    "%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe"
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) do if not defined ISCC if exist %%P set "ISCC=%%~P"
if not defined ISCC for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not defined ISCC set "ISCC=%%I"
if not defined ISCC (
    echo  [X] Inno Setup not found. Install it from https://jrsoftware.org/isdl.php
    echo      The app itself is ready in dist\CommandHub\
    goto :fail
)
echo  Using: %ISCC%

echo.
echo  [4/5] Building the installer
if exist "installer\Output" rmdir /s /q "installer\Output"
"%ISCC%" /Q "/DAppVersion=%VERSION%" "installer\CommandHub.iss"
if errorlevel 1 goto :fail

set "SETUP=installer\Output\CommandHub-Setup-%VERSION%.exe"
if not exist "%SETUP%" (
    echo  [X] %SETUP% was not created.
    goto :fail
)

rem ---------- 5. checksum ----------
echo.
echo  [5/5] SHA-256 checksum
for /f "skip=1 delims=" %%H in ('certutil -hashfile "%SETUP%" SHA256 ^| findstr /v /c:"CertUtil"') do if not defined HASH set "HASH=%%H"
set "HASH=%HASH: =%"
> "%SETUP%.sha256.txt" echo %HASH%  CommandHub-Setup-%VERSION%.exe
echo  %HASH%

echo.
echo  ==========================================
echo    Done: %SETUP%
echo  ==========================================
explorer "installer\Output"
echo.
pause
exit /b 0

:fail
echo.
echo  ==========================================
echo    BUILD FAILED - read the message above.
echo  ==========================================
echo.
pause
exit /b 1
