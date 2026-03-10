#!/usr/bin/env powershell
# SafeBuild Monitor - Launcher para Windows PowerShell
# Este script instala las dependencias y ejecuta la aplicación

$ErrorActionPreference = "Stop"

# Función para mostrar títulos
function Write-Title {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $args[0] -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

# Verificar si Python está instalado
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Title "ERROR"
    Write-Host "Python 3.9+ no está instalado" -ForegroundColor Red
    Write-Host "`nPor favor instala Python desde:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "`nAsegúrate de marcar 'Add Python to PATH' durante la instalación`n" -ForegroundColor Yellow
    Read-Host "Presiona Enter para cerrar..."
    exit 1
}

Write-Title "SafeBuild Monitor - Iniciando"

# Crear carpeta de capturas
if (!(Test-Path "captures")) {
    New-Item -ItemType Directory -Path "captures" -Force | Out-Null
    Write-Host "✓ Carpeta 'captures' creada" -ForegroundColor Green
}

# Instalar dependencias
Write-Host "Instalando dependencias requeridas..." -ForegroundColor Yellow
& python -m pip install --upgrade pip --quiet
$requirements = @(
    "streamlit>=1.28.0"
    "streamlit-webrtc>=0.50.0"
    "ultralytics>=8.3.200"
    "opencv-python-headless>=4.10.0"
    "numpy>=1.26.4"
    "Pillow>=10.4.0"
    "pyzbar>=0.1.9"
    "openpyxl>=3.1.2"
    "reportlab>=4.0"
    "qrcode"
)

foreach ($package in $requirements) {
    & python -m pip install $package --quiet
}

Write-Host "✓ Dependencias instaladas correctamente" -ForegroundColor Green

Write-Title "Iniciando SafeBuild Monitor"
Write-Host "La aplicación se abrirá en tu navegador:" -ForegroundColor Yellow
Write-Host "http://localhost:8501`n" -ForegroundColor Green

# Ejecutar la aplicación
& python -m streamlit run app.py

Read-Host "`nPresiona Enter para cerrar..."

if (Test-Path $RequirementsFile) {
    Write-Host "Instalando dependencias desde $RequirementsFile..."
    pip install -r $RequirementsFile
} else {
    Write-Host "No se encontró $RequirementsFile"
}

Write-Host "Iniciando main.py..."
python main.py
