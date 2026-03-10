#!/usr/bin/env python
"""
SafeBuild Monitor - Launcher
Punto de entrada para ejecutar la aplicación Streamlit
"""
import os
import sys
import subprocess

def main():
    """Inicia la aplicación Streamlit"""
    # Obtener la ruta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, 'app.py')
    
    # Ejecutar streamlit
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path], cwd=current_dir)

if __name__ == '__main__':
    main()
