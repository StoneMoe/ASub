;--------------------------------
;Include Modern UI

!include "MUI2.nsh"

;--------------------------------
;General

;Name and file
Name "ASub"
OutFile "ASubInstaller.exe"
SetCompress auto
SetCompressor lzma

;Default installation folder
InstallDir "$PROGRAMFILES\ASub"

;--------------------------------
;Interface Settings

!define MUI_ABORTWARNING

;--------------------------------
;Pages

!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES

;--------------------------------
;Languages

!insertmacro MUI_LANGUAGE "Chinese (Simplified)"

;--------------------------------
;Installer Sections

Section "ASub (required)"

  SetOutPath "$INSTDIR"
  File /r ".\dist\asub\*.*"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  CreateDirectory "$SMPROGRAMS\ASub"
  CreateShortCut "$SMPROGRAMS\ASub\ASub.lnk" "$INSTDIR\asub.exe" "" "" ""
  CreateShortCut "$DESKTOP\ASub.lnk" "$INSTDIR\asub.exe" "" "" ""

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;Remove installed files and folder
  Delete "$INSTDIR\*.*"
  RMDir "$INSTDIR"

  ;Remove shortcuts
  Delete "$SMPROGRAMS\ASub\ASub.lnk"
  Delete "$DESKTOP\ASub.lnk"

SectionEnd
