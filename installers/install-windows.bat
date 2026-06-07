@echo off
rem StemSplitter — instalator Windows / Windows installer
setlocal
cd /d "%~dp0\.."

echo.
echo ==================================================
echo    StemSplitter - instalacja / installation
echo ==================================================
echo.
echo Potrwa kilka minut. Nie zamykaj tego okna.
echo This takes a few minutes. Do not close this window.
echo.

rem [1/3] narzedzia / tools (uv — pobierane jako binarka, bez winget)
where uv >nul 2>nul
if errorlevel 1 (
  echo [1/3] Instaluje narzedzia... / Installing tools...
  powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
) else (
  echo [1/3] Narzedzia juz sa / tools already present.
)

rem [2/3] srodowisko + WSZYSTKIE zaleznosci (w tym ffmpeg przez pakiet pip 'static-ffmpeg')
rem w widocznym folderze %USERPROFILE%\StemSplitter. Brak winget.
echo [2/3] Pobieram aplikacje (najdluzszy krok)... / Downloading the app (longest step)...
set "VENV=%USERPROFILE%\StemSplitter\venv"
rem --clear: bezobslugowo (nie pyta, gdy venv juz istnieje)
uv venv "%VENV%" --python 3.11 --clear

rem Na Windows torch z PyPI jest ZAWSZE CPU-only; audio-separator[gpu] daje tylko
rem onnxruntime-gpu, a modele Roformer licza przez torcha -> bez tego szloby na CPU.
rem --torch-backend=auto: uv sam wykrywa sterownik NVIDIA i bierze torcha z wlasciwego
rem indeksu CUDA (uniwersalnie, bez wpisywania wersji CUDA na sztywno).
where nvidia-smi >nul 2>nul
if errorlevel 1 (
  echo      Brak karty NVIDIA - wariant CPU. / No NVIDIA - CPU build.
  set "TORCH_BACKEND="
  uv pip install --python "%VENV%" "audio-separator[cpu]"
) else (
  echo      Wykryto NVIDIA - wariant GPU/CUDA. / NVIDIA detected - GPU/CUDA build.
  set "TORCH_BACKEND=--torch-backend=auto"
  uv pip install --python "%VENV%" --torch-backend=auto "audio-separator[gpu]"
)
rem reszta zaleznosci z pyproject.toml (gradio, pyyaml, yt-dlp, static-ffmpeg).
rem %TORCH_BACKEND% pilnuje, by ten krok nie podmienil torcha na CPU (torch jest
rem zaleznoscia tranzytywna audio-separator, nie ma go w pyproject); na CPU jest pusty.
uv pip install --python "%VENV%" %TORCH_BACKEND% -e .

echo [3/3] Gotowe. / Done.
echo.
echo ==================================================
echo    GOTOWE! / DONE!
echo    Wyniki znajdziesz w: %USERPROFILE%\StemSplitter\output
echo    Your results will be in: %USERPROFILE%\StemSplitter\output
echo    Aby uruchomic ponownie kliknij: run-windows.bat
echo    To run again, double-click: run-windows.bat
echo ==================================================
echo.
echo Uruchamiam StemSplitter... / Starting StemSplitter...
set "PYTHONPATH=src"
"%VENV%\Scripts\python.exe" -m stemsplitter.app
pause
