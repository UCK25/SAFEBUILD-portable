@echo off
REM SafeBuild Monitor - Launcher
cd /d "%~dp0"

REM Portable-friendly environment:
REM - Install dependencies into a local venv under the project folder
REM - Run server using the venv's python.exe
set "VENV_DIR=%~dp0venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "REQ_FILE=%~dp0requirements.txt"
set "WHEELS_DIR=%~dp0wheels"
set "DEPS_DONE_FILE=%VENV_DIR%\safebuild_deps_installed.flag"

REM If wheels are provided, prefer offline install (no network).
if exist "%WHEELS_DIR%" (
  set "SAFEBUILD_OFFLINE=1"
)

REM Si se lanza de forma oculta, salta a la ejecucion real
if "%~1"=="hidden_run" goto do_run

REM === PARTE VISIBLE ===
REM 1. Comprobar si Python esta instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
  echo.
  echo =====================================================
  echo [ERROR] Python no esta instalado o no esta en el PATH.
  echo.
  echo Instale Python 3.9 a 3.12 desde:
  echo https://www.python.org/downloads/release/python-31210/
  echo.
  echo Marque "Add Python to PATH" durante la instalacion.
  echo =====================================================
  echo.
  echo Esta ventana se cerrara en 10 segundos...
  timeout /t 10 /nobreak > nul
  exit /b 1
)

REM 2. Obtener version de Python
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i

REM Extraer major y minor (ej: 3.12.9 -> MAJOR=3, MINOR=12)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
  set MAJOR=%%a
  set MINOR=%%b
)

REM --- Caso incompatible: menor que 3.9 ---
if %MAJOR% lss 3 goto version_error
if %MAJOR% equ 3 if %MINOR% lss 9 goto version_error

REM --- Caso incompatible: 3.13 o superior ---
if %MAJOR% gtr 3 goto version_error
if %MAJOR% equ 3 if %MINOR% geq 13 goto version_error

REM --- Version compatible (3.9 a 3.12): ocultar directamente sin ningun mensaje ---
goto hide_console

:version_error
echo.
echo =====================================================
echo [ERROR] Version de Python no compatible: %PYTHON_VERSION%
echo.
echo SafeBuild Monitor requiere Python 3.9 a 3.12.
echo Descargue desde:
echo https://www.python.org/downloads/release/python-31210/
echo =====================================================
echo.
echo Esta ventana se cerrara en 10 segundos...
timeout /t 10 /nobreak > nul
exit /b 1

:hide_console
REM Relanzar este script de forma oculta (sin ventana de consola)
> "%temp%\hidden_launch.vbs" echo Set WshShell = CreateObject("WScript.Shell")
>> "%temp%\hidden_launch.vbs" echo WshShell.Run chr(34) ^& WScript.Arguments(0) ^& chr(34) ^& " hidden_run", 0, False
cscript //nologo "%temp%\hidden_launch.vbs" "%~f0"
del "%temp%\hidden_launch.vbs"
exit /b 0

:do_run
REM === PARTE OCULTA ===
REM Create venv if missing, then install deps once.
if not exist "%VENV_PY%" (
  python -m venv "%VENV_DIR%"
)

REM Use venv pip/python from here.
if not exist "%WHEELS_DIR%" (
  REM Online mode: upgrade pip (may require network).
  "%VENV_PY%" -m pip install -q --upgrade pip
)

if not exist "%DEPS_DONE_FILE%" (
  if exist "%WHEELS_DIR%" (
    REM Offline mode: install from local wheel cache.
    "%VENV_PY%" -m pip install -q --no-index --find-links "%WHEELS_DIR%" -r "%REQ_FILE%"
  ) else (
    REM Online mode (fallback): install normally.
    "%VENV_PY%" -m pip install -q -r "%REQ_FILE%"
  )
  echo.>"%DEPS_DONE_FILE%"
)

"%VENV_PY%" flask_server.py
exit /b 0
