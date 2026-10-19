@echo off
REM PixelIQ Result Generator - desktop build (Windows)
REM Produces: dist\PixelIQResultGenerator.exe
setlocal
cd /d "%~dp0\.."

set PYTHON=python
where py >nul 2>nul && set PYTHON=py -3

echo [build] using %PYTHON%
%PYTHON% -m pip install -q --upgrade pyinstaller pywebview

%PYTHON% -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name PixelIQResultGenerator ^
  --paths . ^
  --collect-all school_result_generator ^
  --collect-all result_app ^
  --collect-all django ^
  --collect-all crispy_forms ^
  --collect-all crispy_bootstrap5 ^
  --collect-all reportlab ^
  --collect-submodules openpyxl ^
  --collect-submodules xlrd ^
  --collect-data reportlab ^
  --hidden-import webview ^
  desktop\launch.py

if errorlevel 1 (
  echo [build] FAILED
  exit /b 1
)
echo [build] done -^> dist\PixelIQResultGenerator.exe
endlocal
