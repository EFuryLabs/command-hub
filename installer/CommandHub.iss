; =====================================================================
;  Command Hub - Windows installer (Inno Setup 7, also works with 6.3+)
;
;  Build the app first:   pyinstaller --noconfirm --clean CommandHub.spec
;  Then either open this file in Inno Setup and press Compile (Ctrl+F9),
;  or run build-installer.bat, which does everything.
;
;  Output: installer\Output\CommandHub-Setup-<version>.exe
; =====================================================================

#define AppName      "Command Hub"
#define AppPublisher "EFury Labs"
#define AppExeName   "CommandHub.exe"
#define AppWebsite   "https://efurylabs.com/projects/python-command-hub.html"
#define AppRepo      "https://github.com/EFuryLabs/command-hub"
#define AppMutexName "EFuryLabs.CommandHub"
#define BuiltApp     AddBackslash(SourcePath) + "..\dist\CommandHub\" + AppExeName

#if !FileExists(BuiltApp)
  #error "dist\CommandHub\CommandHub.exe not found - build the app with PyInstaller first."
#endif

; Version: build-installer.bat passes /DAppVersion=x.y.z (from app_info.py).
; Pressing Compile in the Inno Setup window instead reads it from the .exe.
#ifndef AppVersion
  #define AppVersion GetStringFileInfo(BuiltApp, "ProductVersion")
#endif

[Setup]
; NEVER change AppId after the first release: Windows uses it to recognise
; Command Hub for upgrades and uninstall. (The double {{ is intentional.)
AppId={{D00081B1-CA36-4DA8-BCC5-83744AB8BECD}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppWebsite}
AppSupportURL={#AppRepo}/issues
AppUpdatesURL={#AppRepo}/releases
AppCopyright=Copyright (C) 2026 Vijay Bari
AppComments=Organize your frequently used commands and copy them with one click.

; Version details of Setup.exe itself (Properties > Details)
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

; Where it installs. {autopf} = C:\Program Files (all users)
; or %LOCALAPPDATA%\Programs (just me) - chosen on the first page.
DefaultDirName={autopf}\{#AppPublisher}\{#AppName}
DisableProgramGroupPage=yes
UsePreviousAppDir=yes

; "Install for all users (admin)" or "Only for me (no admin)"
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 64-bit Windows 10 or newer
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

; Wizard
WizardStyle=modern
LicenseFile=..\LICENSE
SetupIconFile=..\assets\app.ico

; Apps & Features entry
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}

; If Command Hub is running, ask to close it before installing/uninstalling
AppMutex={#AppMutexName}
CloseApplications=yes
RestartApplications=no

; Output file
OutputDir=Output
OutputBaseFilename=CommandHub-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Everything PyInstaller produced in dist\CommandHub
Source: "..\dist\CommandHub\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "Organize and copy your commands"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// After uninstalling: ask whether to delete the user's saved commands too.
// (They live in %APPDATA%\EFury Labs\Command Hub, not in the program folder.)
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\{#AppPublisher}\{#AppName}');
    if DirExists(DataDir) then
    begin
      if SuppressibleMsgBox('Do you also want to delete your saved commands?' + #13#10#13#10 +
                            DataDir + #13#10#13#10 +
                            'Choose No to keep them for a future install.',
                            mbConfirmation, MB_YESNO or MB_DEFBUTTON2, IDNO) = IDYES then
        DelTree(DataDir, True, True, True);
    end;
  end;
end;
