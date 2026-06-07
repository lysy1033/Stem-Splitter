@echo off
rem StemSplitter — uruchomienie / launch (Windows)
setlocal
cd /d "%~dp0\.."
set "VENV=%USERPROFILE%\StemSplitter\venv"
if not exist "%VENV%\Scripts\python.exe" (
  echo Najpierw uruchom install-windows.bat / Run install-windows.bat first.
  pause
  exit /b 1
)
echo Uruchamiam StemSplitter... / Starting StemSplitter...
set "PYTHONPATH=src"
"%VENV%\Scripts\python.exe" -m stemsplitter.app
pause
