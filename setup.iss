; ============================================================
;  Update Alarm - Inno Setup Installer Script
;  Derleme: ISCC.exe setup.iss   (veya build.bat ile otomatik)
; ============================================================

#define MyAppName      "OYYA1UPDATE ALARM"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "Your Company"
#define MyAppURL       "https://github.com/berk103458/update-alarm"
#define MyAppExeName   "UpdateAlarm.exe"
#define MyAppID        "{{A7B3C2D1-E4F5-6789-ABCD-EF0123456789}"

[Setup]
AppId={#MyAppID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=dist\installer
OutputBaseFilename=UpdateAlarm_Setup_{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
PrivilegesRequiredOverridesAllowed=dialog
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=yes
VersionInfoVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Kurulum
WizardImageFile=wizard_main.bmp
WizardSmallImageFile=wizard_small.bmp

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon";   Description: "Masaustu kisayolu olustur";              GroupDescription: "Ek ikonlar:";     Flags: unchecked
Name: "startuprun";    Description: "Windows baslangicindan otomatik calistir"; GroupDescription: "Diger secenek:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}";                   Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} Kaldir";             Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}";            Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Windows baslangicindan calistir
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "UpdateAlarm"; \
  ValueData: """{app}\{#MyAppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startuprun

; Uygulama ayar klasoru (varsa temizleme)
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekeyifempty

[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "{#MyAppName}'i Baslatma"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/f /im {#MyAppExeName}"; Flags: runhidden; RunOnceId: "KillApp"

[Code]
// Kurulum oncesi calisan ornegi kapat
procedure InitializeWizard();
begin
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Exec('taskkill.exe', '/f /im {#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(1000);
  Result := '';
end;
