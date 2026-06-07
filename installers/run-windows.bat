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
rem UTF-8: konsola PL ma cp1250 i wywala sie na paskach tqdm (znaki blokowe Unicode)
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8:replace"
"%VENV%\Scripts\python.exe" -m stemsplitter.app
pause
