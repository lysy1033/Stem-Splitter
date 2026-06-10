@echo off
rem StemSplitter — aktualizacja / update (Windows)
rem cmd doczytuje .bat z dysku W TRAKCIE dzialania — nadpisanie wlasnego pliku
rem w polowie psuje skrypt. Dlatego kopiujemy sie do %TEMP% i uruchamiamy
rem stamtad, przekazujac katalog aplikacji jako argument.
if "%~1"=="" (
  copy /y "%~f0" "%TEMP%\stemsplitter-update.bat" >nul
  "%TEMP%\stemsplitter-update.bat" "%~dp0.."
  exit /b
)
setlocal
set "APP_DIR=%~f1"
cd /d "%APP_DIR%"

echo.
echo ==================================================
echo    StemSplitter - aktualizacja / update
echo ==================================================
echo.
timeout /t 2 /nobreak >nul

set "VENV=%USERPROFILE%\StemSplitter\venv"
if not exist "%VENV%\Scripts\python.exe" (
  echo Najpierw uruchom install-windows.bat / Run install-windows.bat first.
  pause
  exit /b 1
)

set "TMPDIR=%TEMP%\stemsplitter-update-files"
rmdir /s /q "%TMPDIR%" 2>nul
mkdir "%TMPDIR%"

echo [1/3] Pobieram nowa wersje... / Downloading the new version...
curl.exe -L -o "%TMPDIR%\app.zip" "https://github.com/lysy1033/Stem-Splitter/archive/refs/heads/main.zip"
if errorlevel 1 goto :fail
tar -xf "%TMPDIR%\app.zip" -C "%TMPDIR%"
if errorlevel 1 goto :fail

echo [2/3] Podmieniam pliki aplikacji... / Replacing app files...
robocopy "%TMPDIR%\Stem-Splitter-main" "%APP_DIR%" /E /NFL /NDL /NJH /NJS >nul
rem robocopy: kody 0-7 = sukces, dopiero 8+ to blad
if errorlevel 8 goto :fail

echo [3/3] Aktualizuje zaleznosci... / Updating dependencies...
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
rem ta sama logika CPU/GPU co w install-windows.bat (torch CUDA przez uv)
where nvidia-smi >/dev/null 2>nul
if errorlevel 1 (
  set "TORCH_BACKEND="
  uv pip install --python "%VENV%" "audio-separator[cpu]"
) else (
  set "TORCH_BACKEND=--torch-backend=auto"
  uv pip install --python "%VENV%" --torch-backend=auto "audio-separator[gpu]"
)
uv pip install --python "%VENV%" %TORCH_BACKEND% -e .

rmdir /s /q "%TMPDIR%" 2>nul
echo.
echo Gotowe! Uruchamiam StemSplitter... / Done! Starting StemSplitter...
set "PYTHONPATH=src"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8:replace"
"%VENV%\Scripts\python.exe" -m stemsplitter.app
pause
exit /b

:fail
echo.
echo Aktualizacja nie powiodla sie. / Update failed.
pause
exit /b 1
