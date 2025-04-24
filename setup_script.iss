; -- setup_script.iss --
; Inno Setup Script for TikTok-YouTube视频下载器

[Setup]
; NOTE: The value of AppName is used in folders, AppVerName is shown to user.
AppName=TikTok-YouTube视频下载器
AppVersion=1.0 
; AppPublisher=PhiloKun ; (Optional: Your name/company)
; AppPublisherURL=https://github.com/PhiloKun ; (Optional: Your website)
; AppSupportURL=https://github.com/PhiloKun/.../issues ; (Optional: Support URL) 
DefaultDirName={autopf}\TikTok-YouTube视频下载器
; DefaultGroupName=TikTok-YouTube视频下载器 ; (Optional: Start Menu folder name)
;DisableDirPage=yes
; DisableProgramGroupPage=yes ; (Optional: Uncomment if you don't want Start Menu folder selection)
; Uncomment the following line to run in non administrative install mode (Install for current user only)
PrivilegesRequired=lowest
SetupIconFile=tiktok-youtube_downloader.ico
OutputBaseFilename=TikTok-YouTube视频下载器_Setup 
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Source: "Path\To\Your\Compiled\App\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Make sure the Source path points correctly to your PyInstaller output!
Source: "dist\TikTok-YouTube视频下载器.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "tiktok-youtube_downloader.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion 
; NOTE: Don't forget to add any other files your application needs here.

[Icons]
Name: "{autoprograms}\TikTok-YouTube视频下载器"; Filename: "{app}\TikTok-YouTube视频下载器.exe"
Name: "{autodesktop}\TikTok-YouTube视频下载器"; Filename: "{app}\TikTok-YouTube视频下载器.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TikTok-YouTube视频下载器.exe"; Description: "{cm:LaunchProgram,TikTok-YouTube视频下载器}"; Flags: nowait postinstall skipifsilent

; Optional: Define files/folders to remove during uninstall if needed beyond what's in [Files]
; [UninstallDelete]
; Type: files; Name: "{app}\some_temp_file.log" 