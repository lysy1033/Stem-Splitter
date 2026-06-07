@echo off
setlocal
cd /d "%~dp0\.."
set "VENV=%USERPROFILE%\.stem-splitter\venv"
set "PYTHONPATH=src"
"%VENV%\Scripts\python.exe" -m stemsplitter.app
