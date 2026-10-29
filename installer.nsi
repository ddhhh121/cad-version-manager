; CAD Version Manager NSIS Installer Script

!include "MUI2.nsh"

; Installer attributes
Name "CAD Version Manager"
OutFile "CAD_Version_Manager_Setup.exe"
InstallDir "$PROGRAMFILES\CAD Version Manager"
InstallDirRegKey HKLM "Software\CADVersionManager" "InstallDir"
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "SimpChinese"

; Install section
Section "Install CAD Version Manager" SecMain
  SetOutPath "$INSTDIR"

  ; Add files
  File "backend\dist\cad-backend.exe"

  ; Create frontend directory
  SetOutPath "$INSTDIR\frontend\dist"
  File /r "frontend\dist\*.*"

  ; Create uninstaller
  SetOutPath "$INSTDIR"
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\CAD Version Manager"
  CreateShortCut "$SMPROGRAMS\CAD Version Manager\CAD Version Manager.lnk" "$INSTDIR\cad-backend.exe"
  CreateShortCut "$SMPROGRAMS\CAD Version Manager\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\CAD Version Manager.lnk" "$INSTDIR\cad-backend.exe"

  ; Write registry
  WriteRegStr HKLM "Software\CADVersionManager" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CADVersionManager" "DisplayName" "CAD Version Manager"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CADVersionManager" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CADVersionManager" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CADVersionManager" "NoRepair" 1
SectionEnd

; Uninstall section
Section "Uninstall"
  ; Delete files
  Delete "$INSTDIR\cad-backend.exe"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR\frontend"

  ; Delete shortcuts
  Delete "$SMPROGRAMS\CAD Version Manager\CAD Version Manager.lnk"
  Delete "$SMPROGRAMS\CAD Version Manager\Uninstall.lnk"
  RMDir "$SMPROGRAMS\CAD Version Manager"
  Delete "$DESKTOP\CAD Version Manager.lnk"

  ; Delete registry
  DeleteRegKey HKLM "Software\CADVersionManager"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CADVersionManager"

  ; Delete install directory
  RMDir "$INSTDIR"
SectionEnd
