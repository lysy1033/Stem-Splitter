@echo off
setlocal
cd /d "%~dp0\.."
echo == Instalacja StemSplitter (Windows) ==

where uv >nul 2>nul
if errorlevel 1 (
  echo Instaluje uv...
  powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

set "VENV=%USERPROFILE%\.stem-splitter\venv"
uv venv "%VENV%" --python 3.11

rem Wykryj karte NVIDIA
where nvidia-smi >nul 2>nul
if errorlevel 1 (
  echo Brak NVIDIA — instaluje wariant CPU.
  uv pip install --python "%VENV%" "audio-separator[cpu]" gradio pyyaml yt-dlp
) else (
  echo Wykryto NVIDIA — instaluje wariant GPU (CUDA).
  uv pip install --python "%VENV%" "audio-separator[gpu]" gradio pyyaml yt-dlp
)

echo Instaluje ffmpeg (winget)...
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
echo Gotowe. Uruchom przez run-windows.bat
pause
