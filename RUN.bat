@echo off
REM SafeBuild Monitor - Launcher para Windows
REM Este script instala las dependencias y ejecuta la aplicación

setlocal enabledelayedexpansion

REM Detectar si Python está instalado
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ========================================
    echo ERROR: Python 3.9+ no está instalado
    echo ========================================
    echo.
    echo Por favor instala Python desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrate de marcar "Add Python to PATH"
    echo durante la instalación
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SafeBuild Monitor - Iniciando aplicación
echo ========================================
echo.

REM Crear carpeta de capturas si no existe
if not exist "captures" mkdir captures

REM Instalar dependencias
echo Instalando dependencias requeridas...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirement.txt --quiet

if !errorlevel! neq 0 (
    echo.
    echo Error al instalar dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo Iniciando aplicación Streamlit...
echo ========================================
echo.
echo La aplicación se abrirá en tu navegador en:
echo http://localhost:8501
echo.

REM Ejecutar la aplicación
python -m streamlit run app.py

pause
