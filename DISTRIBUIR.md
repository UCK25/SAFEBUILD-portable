# 📦 SafeBuild Monitor - Guía de Distribución

## Opción 1: Archivo Batch (RECOMENDADO - Más simple)

### Para distribuir la aplicación:

1. **Copia el archivo `RUN.bat`** desde la carpeta del proyecto
2. **Comprime toda la carpeta del proyecto** (ZIP)
3. **Distribuyelo a otros usuarios**

### Para ejecutar en otra computadora:

1. **Extrae el ZIP** en cualquier carpeta
2. **Doble-clic en `RUN.bat`**
3. **Espera a que se instale automaticamente**
4. **Se abrirá el navegador automáticamente**

---

## Opción 2: PowerShell (Más moderno)

### Requisito previo:
- Ejecutar en PowerShell como Administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Para ejecutar:
1. Doble-clic en `RUN.ps1`
2. O desde PowerShell:
```powershell
.\RUN.ps1
```

---

## ⚙️ Requisitos del Sistema

- **Windows 7, 10, 11** (o superior)
- **Python 3.9 o superior** (se instala automáticamente en la mayoría de casos)
- **Conexión a Internet** (solo para instalar dependencias la primera vez)

### Instalar Python manualmente (si es necesario):

Si el script reporta que Python no está instalado:

1. Descarga Python desde: https://www.python.org/downloads/
2. **IMPORTANTE**: Marca la opción **"Add Python to PATH"** durante la instalación
3. Reinicia la computadora
4. Ejecuta `RUN.bat` nuevamente

---

## 📱 URL de la Aplicación

Una vez ejecutada, accede a la aplicación en:
- **Localmente**: `http://localhost:8501`
- **Desde otra computadora en la red**: `http://IP_DE_LA_COMPUTADORA:8501`
  - Ejemplo: `http://192.168.1.107:8501`

---

## 📂 Estructura de Carpetas

```
SAFEBUILD29/
├── RUN.bat                 (Ejecutar en Windows)
├── run.ps1                 (Ejecutar en PowerShell)
├── app.py                  (Aplicación principal)
├── config.py               (Configuración)
├── database.py             (Base de datos)
├── observer.py             (Observadores)
├── camera_widget.py        (Widget de cámara)
├── main_window.py          (Ventana principal)
├── requirement.txt         (Dependencias)
├── runs/                   (Modelos YOLO entrenados)
├── Safety-vest---v4-1/     (Dataset)
└── captures/               (Capturas (se crea automáticamente))
```

---

## 🆘 Solución de Problemas

### Problema: "Python no está en PATH"
**Solución**: 
1. Desinstala Python
2. Instálalo nuevamente desde https://www.python.org/downloads/
3. **Asegúrate de marcar "Add Python to PATH"**
4. Reinicia la computadora

### Problema: Puerto 8501 en uso
**Solución**: 
1. Cierra otras instancias de Streamlit
2. O ejecuta con un puerto diferente:
```bash
streamlit run app.py --server.port 8502
```

### Problema: Errores de dependencias
**Solución**: 
1. Ejecuta desde una terminal (no como archivo .bat):
```bash
python -m pip install -r requirement.txt
python -m streamlit run app.py
```

---

## 📋 Para Desarrolladores

Si deseas crear un ejecutable de una sola pieza (.exe):

```bash
pyinstaller --onedir --windowed launcher.py -n SafeBuildMonitor
```

---

## 💬 Notas

- La aplicación requiere acceso a la cámara web
- Todos los datos se guardan localmente en la carpeta del proyecto
- Se crea una base de datos SQLite automaticamente
- Los modelos YOLO se cargan desde la carpeta `runs/`

---

**¿Preguntas?** Revisa el archivo `README.md` principal del proyecto.
