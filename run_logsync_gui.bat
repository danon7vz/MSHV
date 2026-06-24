@echo off
chcp 65001 >nul
cd /d "%~dp0"
python logsync_gui.py
if errorlevel 1 (
  echo.
  echo Erreur au lancement. Verifie que Python est installe, ou lance :
  echo    python logsync_gui.py
  echo dans une invite de commande pour voir le message.
  pause
)
