; Lausch Installer Script for Inno Setup 6+

[Setup]
AppId={{B8F3A2D1-4E5C-4A1B-9D3F-7C8E2A1B4D5F}
AppName=Lausch
AppVersion=1.0.0
AppPublisher=TimD-dev
AppPublisherURL=https://github.com/TimD-dev/lausch
DefaultDirName={autopf}\Lausch
DefaultGroupName=Lausch
OutputBaseFilename=LauschSetup
SetupIconFile=..\assets\lausch.ico
UninstallDisplayIcon={app}\Lausch.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Lausch beim Windows-Start automatisch starten"; GroupDescription: "Weitere Optionen:"

[Files]
Source: "..\dist\Lausch\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lausch"; Filename: "{app}\Lausch.exe"
Name: "{group}\Lausch deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Lausch"; Filename: "{app}\Lausch.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Lausch"; ValueData: """{app}\Lausch.exe"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\Lausch.exe"; Description: "Lausch jetzt starten"; Flags: nowait postinstall skipifsilent
