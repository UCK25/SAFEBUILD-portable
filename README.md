# SafeBuild Monitor - Sistema de Monitoreo de Seguridad en Obras


SafeBuild Monitor es un sistema web de monitoreo en tiempo real para el Sector de Construcción. Utiliza el modelo de IA YOLOv8n para la detección automatizada de cascos y chalecos, contribuyendo con la prevención de incidentes. Realiza con servidor Flask (python) integrado para computadora Windows, acceso por navegador y cierre automatico.

Entrenado con datasets de Roboflow "helmet-vest-detection-9esst" en total de 314 imagenes.

[helmet-vest-detection-9esst](https://universe.roboflow.com/helmet-and-vest-detection/helmet-vest-detection-9esst)


---

## Contenido

1. [Caracteristicas Principales](#caracteristicas-principales)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalacion y Ejecucion](#instalacion-y-ejecucion)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Modelo de Inteligencia Artificial](#modelo-de-inteligencia-artificial)
6. [Funcionalidades Detalladas](#funcionalidades-detalladas)
7. [Base de Datos](#base-de-datos)
8. [Modulos del Sistema](#modulos-del-sistema)
9. [Guia de Uso](#guia-de-uso)
10. [Configuracion Avanzada](#configuracion-avanzada)
11. [Solucion de Problemas](#solucion-de-problemas)
12. [Seguridad](#seguridad)

---
## Riesgos
- William Fine integrado en observer.py para severidad.
- Pruebas: Simula con videos; precisión >90%.
---

## Caracteristicas Principales

### Detección de Equipos de Protección Personal (EPP)

- **Detección en Tiempo Real**: Identifica automáticamente a personas sin arnés de seguridad o chaleco de seguridad
- **Clases detectadas**: helmet (casco), not_helmet (sin casco), reflective (chaleco), not_reflective (sin chaleco)
- Detección continua desde la cámara del navegador, sin interrupciones
- Bounding boxes con dimensiones exactas del objeto detectado (ajuste automático por distancia y proporción)
- Score de confianza visible junto a cada detección (ej. "Falta Casco 87%")
- **Modelo YOLOv8 Entrenado**: Precisión superior al 90% en detección de casco de seguridad
- **Alertas Automáticas**: Notifica inmediatamente cuando se detecta ausencia de (Equipos de protección personal) EPP


### Visualización Dinámica por Nivel de Confianza

Para alertas de incumplimiento, el color del recuadro varia según la confianza del modelo:
- Rojo (>80% confianza): violación con alta certeza
- Naranja (60-80% confianza): violación con confianza media
- Amarillo (<60% confianza): violación con confianza baja

Para EPP correcto presente:
- Cyan: casco o chaleco detectado correctamente

Texto con fondo semitransparente para legibilidad siempre garantizada.

### Dashboard en Tiempo Real
- Interfaz web accesible en http://localhost:8000
- Cámara del navegador con overlay de detecciones sin parpadeos
- Bucle de captura sin retardo mediante requestAnimationFrame
- Historial de escaneos QR con timestamp
- Lista de últimos incidentes con descripción y estado

### Identificación de Usuarios mediante QR
- **Lectura de Códigos QR**: Identifica automáticamente trabajadores mediante códigos QR integrados
- **Mapeo por Proximidad**: Asocia códigos QR detectados con la persona más cercana en la cámara
- **Fallback para Identidades Desconocidas**: Si no hay QR, registra como "usuario desconocido"

### Gestión de Usuarios y Permisos
- Roles: admin, supervisor, guest
- Asignación de código QR único por usuario
- Generación de QR imprimible desde la interfaz de administración

### Gestión de Base de Datos
- **SQLite Local**: Base de datos integrada con seguridad mediante PBKDF2-HMAC-SHA256
- **Registro de Incidentes**: Almacena todos los eventos con evidencia y contexto
- **Logs de Auditoría**: Registra todas las acciones administrativas
- **Historial de Descargas de QR**: Tracking de QR descargados por administradores

### Análisis de Riesgos (Matriz William Fine)
- **Evaluación de Severidad**: Calcula el nivel de riesgo de cada incidente
- **Fórmula William Fine**: Severidad = Probabilidad × Exposición × Consecuencia
- **Clasificación de Riesgos**: Categoriza incidentes en Trivial, Tolerable, Moderado, Sustancial o Intolerable

### Registro de Incidentes
- Registro automatico en SQLite al detectar una infraccion de EPP
- Imagen de evidencia guardada en la carpeta captures/ en formato JPEG
- Deduplicacion: si el mismo incidente ocurre en ventana de 5 segundos, se actualiza el registro existente
- Exportacion de reportes en CSV y Excel (.xlsx) con imagenes de evidencia incrustadas

### Cierre Automatico del Servidor
- El navegador envia un "heartbeat" (latido) al servidor cada segundo
- Si la pestana se cierra, el servidor detecta la ausencia de latido en 15 segundos y se apaga automaticamente
- Elimina procesos residuales de Python en segundo plano

---

## Requisitos del Sistema

Sistema Operativo: Windows 10 o Windows 11 (64 bits)
Python: 3.9 o superior (3.12 compatible y probado)
Navegador: Firefox, Chrome o Edge (recomendado para acceso a camara WebRTC)
Camara: Webcam integrada o USB con resolucion minima 720p
RAM: 4 GB minimo, 8 GB recomendado
Espacio en disco: aproximadamente 3 GB (modelo YOLO incluido)
Red: Solo red local. No requiere conexion a Internet para operar.

### Dependencias (requirement.txt)
```
flask
itsdangerous
ultralytics
opencv-python-headless
numpy
Pillow
pyzbar
openpyxl
reportlab
```

---

## Instalacion y Ejecucion

### Metodo unico para Windows: EJECUTAR.bat

Hacer doble clic en el archivo EJECUTAR.bat incluido en la carpeta del proyecto.

Secuencia de ejecucion del script:
1. Verifica que Python este instalado.
   - Si no esta instalado: muestra un mensaje en espanol con instrucciones para descargar Python
     desde https://www.python.org/downloads/ y NO continua hasta que el usuario lo instale.
2. Instala todas las dependencias de requirement.txt de forma silenciosa (sin ventana visible).
3. Reinicia el proceso en modo oculto mediante un VBScript temporal.
4. Abre el navegador predeterminado en http://localhost:8000 automaticamente.
5. Al cerrar la pestana del navegador, el servidor se apaga solo gracias al watchdog de heartbeat.

Nota: La ventana de comandos es completamente invisible durante la operacion normal.
Solo aparece si Python no esta instalado, para mostrar el mensaje de error en espanol.

---

## Arquitectura del Sistema

SafeBuild Monitor sigue una arquitectura cliente-servidor local (localhost):

```
[EJECUTAR.bat]
    |
    |-- Verifica Python -> Error en espanol si falta
    |
    |-- VBScript -> Relanza como proceso oculto
                        |
                [python flask_server.py]  <-- Servidor en http://0.0.0.0:8000
                        |
              __________|__________
             |          |          |
        [Modelo]   [SQLite DB]  [Capturas]
        best.pt   safety_.db   captures/
             |
         YOLOv8n
         (Inferencia CPU)

[Navegador Web - Chrome/Edge]
    |
    |-- GET /dashboard  -> dashboard.html
    |-- GET /manage     -> manage.html
    |
    |-- Camera (getUserMedia)
    |       |
    |       |-- canvas.toBlob() -> POST /detect_json -> JSON con boxes + QR
    |       |
    |       |-- renderOverlayLocal() -> strokeRect escalado sobre video
    |
    |-- POST /api/heartbeat (cada 1 segundo)
            |
            |-- watchdog: si no hay latido en 15s -> os._exit(0)
```

El diagrama completo en formato Mermaid se encuentra en el archivo arquitectura_mermaid.txt.
Puede renderizarse en https://mermaid.live/ o en cualquier editor compatible (VS Code, GitHub, Notion, etc.)

### Descripcion de capas

Capa de inicio (Windows):
- EJECUTAR.bat verifica Python y lanza el proceso oculto
- El VBScript temporal redirige la ejecucion sin ventana

Capa de servidor (Backend Flask):
- flask_server.py maneja todas las rutas HTTP
- POST /detect_json ejecuta inferencia YOLO y devuelve boxes + confianza + QR
- Watchdog en hilo separado cierra el proceso si el navegador desaparece

Capa de inteligencia artificial:
- YOLOv8n base, afinado con dataset propio (Safety Vest v4)
- Inferencia en CPU a 320px internamente, coordenadas relativas al frame original
- Mapeo de clases: helmet/not_helmet/reflective/not_reflective -> espanol

Capa de presentacion (Frontend):
- dashboard.html captura frames con requestAnimationFrame y los envia al servidor
- El overlay de canvas escala exactamente las coordenadas YOLO al tamano del elemento video

Capa de datos:
- SQLite local sin servidor externo
- Archivos de evidencia JPEG en captures/

---

## Modelo de Inteligencia Artificial

### Especificaciones del entrenamiento

| Parametro | Valor |
|---|---|
| Arquitectura base | YOLOv8n (nano, 3.2M parametros) |
| Dataset | Safety Vest v4 (Roboflow) |
| Tamano de imagen de entrada | 416 x 416 px |
| Epocas de entrenamiento | 40 |
| Batch size | 16 |
| Tiempo total de entrenamiento | 1,649 segundos (~27.5 minutos) |
| Optimizador | Auto (SGD con warmup 3 epocas) |
| Learning rate inicial | 0.01 |
| Data augmentation | Mosaic, flipLR 50%, HSV, RandAugment |
| Hardware | CPU (sin GPU) |

### Metricas finales (epoca 40)

| Metrica | Valor |
|---|---|
| Precision (B) | 0.830 (83.0%) |
| Recall (B) | 0.819 (81.9%) |
| mAP@0.5 | 0.850 (85.0%) |
| mAP@0.5-0.95 | 0.592 (59.2%) |
| Box loss (val) | 1.032 |
| Cls loss (val) | 0.769 |

### Clases detectadas

| ID | Clase del modelo | Etiqueta mostrada | Accion |
|----|------------------|-------------------|--------|
| 0 | helmet | Casco | EPP correcto (cyan) |
| 1 | not_helmet | Falta Casco | Incumplimiento (rojo/naranja) |
| 2 | not_reflective | Falta Chaleco | Incumplimiento (rojo/naranja) |
| 3 | reflective | Chaleco | EPP correcto (cyan) |

### Umbral de confianza
Configurable en config.py mediante DEFAULT_CONF (valor actual: 0.9).
Rango recomendado segun condiciones:
- Iluminacion optima: 0.7 - 0.9
- Iluminacion normal: 0.45 - 0.7
- Condiciones adversas: 0.3 - 0.45

### Ubicacion del modelo
```
runs/detect/train9/weights/best.pt
```

---

## Funcionalidades Detalladas

### Monitor en Vivo
- Transmisión WebRTC: Acceso en tiempo real a la cámara web
- Análisis en Vivo: Procesamiento de frames a velocidad de video
- Visualización Dinamica: Dibuja bounding boxes adaptativos basados en tamaño y confianza
- Precision Visible: Cada detección muestra su score de confianza (0.00 a 1.00)
- Indicador de Confianza por Color
- Grosor Adaptativo: El grosor del box varía según el tamaño del objeto detectado
- Modelo Utilizado: YOLOv8 entrenado con train9 (precision > 90%)

Funcion Principal: `draw_dynamic_box(frame, x1, y1, x2, y2, label, confidence, class_name)`
```python
# Caracteristicas:
# - Color dinamico: Basado en score de confianza (0.0 a 1.0)
# - Grosor dinamico: Basado en area del objeto (1-5 pixeles)
# - Label: Muestra clase + precision (ej: "person 0.95")
# - Fondo de contraste: Rectangulo de color para mejor legibilidad
```

Funcion Principal: `process_frame_with_model(frame, model)`
```python
# Retorna:
# - annotated_frame: Imagen con boxes dinamicos y precision
# - payload: Diccionario con clases detectadas y QRs identificados
# - Calcula: Confianza, tamaño, distancia al centro del frame
```

### Detección de PPE (Equipo de Protección Personal)
- Clases Detectadas:
  - person_N: Persona detectada (N = ID de persona)
  - riding_helmet_N: Casco detectado
  - safety_vest_N: Chaleco de seguridad detectado
  - safety_harness_N: Arnés de seguridad detectado
  - qr_N: Código QR asociado a persona N

- Agrupacion por Proximidad: Agrupa detecciones cercanas (< 120 pixeles) como la misma persona
- Mapeo QR Automatico: Asigna QRs a personas dentro de 200 pixeles
- Distancia Dinamica: Rastrea distancia de cada objeto al centro del frame
- Confianza Individual: Cada detección registra su score de confianza from model

Indicador Visual de Confianza:
- Rojo intenso (RGB 200,0,0): Confianza < 50% (requiere verificación)
- Amarillo (RGB 255,255,0): Confianza 50-75% (acceptable)
- Verde (RGB 0,255,0): Confianza > 75% (high confidence)

El grosor del bounding box varia de 1-5 pixeles segun el tamaño del objeto:
- Objetos pequeños: linea mas fina (1-2 px)
- Objetos grandes: linea mas gruesa (3-5 px)

### **Sistema de Alertas Multinivel**

#### Tipos de Alertas:
1. **MISSING_SAFETY_VEST**: Persona sin chaleco de seguridad
2. **MISSING_HARNESS**: Persona sin arnés de seguridad
3. **MULTIPLE_HAZARDS**: Persona con múltiples incumplimientos
4. **INTRUDER_ALERT**: Persona desconocida detectada

#### Gestión de Alertas:
```python
# Deduplicación: 3 segundos entre alerts del mismo tipo/cámara
# Cooldown: Configurable en config.py (DEFAULT_CONF = 0.4)
# Evento de Información: Se registra cuando se identifica un QR
```

### **Sistema de Observadores (Observer Pattern)**

#### A. AlertLogger
```python
class AlertLogger:
    - update(subject, event_data): Registra alertas en log
    - Almacena en: st.session_state.alert_messages
    - Formato: "[TIMESTAMP] CÁMARA: ALERTA - Usuario: IDENTIFICADO"
```

#### B. IncidentRegistrar
```python
class IncidentRegistrar:
    - update(subject, event_data): Guarda incidente en BD
    - Llama a: register_incident()
    - Almacena: timestamp, descripción, usuario, cámara
```

#### C. RankingUpdater
```python
class RankingUpdater:
    - update(subject, event_data): Actualiza ranking de incidentes
    - Mantiene diccionario: {usuario -> conteo de incidentes}
    - Disponible en: st.session_state.ranking_updater
```

### **Identificación de Usuarios**

#### Flujo de Identificación:
```
1. Se detecta QR en frame
2. Se extrae código QR (texto)
3. Se busca usuario en BD: get_user_by_qr(qr_code)
4. Si existe → user_identified = username
5. Si no existe → user_identified = "unknown"
6. Se mapea QR a persona más cercana (distancia < 200px)
```

#### Evento en Cuarentena (PENDING_WINDOW = 4 segundos):
```
- Si se detecta evento de EPP pero sin QR cercano
- Se guarda en _pending_events esperando un QR
- Si aparece QR en los próximos 4 segundos → se actualiza
- Si tiempo expira → se notifica como "unknown"
```

### **Análisis de Riesgos (Matriz William Fine)**

#### Fórmula:
```
Nivel de Riesgo = Probabilidad × Exposición × Consecuencias
                = P × E × C
```

#### Valores de Entrada:
- **Probabilidad (P)**: 1-10 (1=improbable, 10=cierto)
- **Exposición (E)**: 1-10 (1=raramente, 10=continuamente)
- **Consecuencias (C)**: 1-100 (1=leve, 100=catastrófico)

#### Niveles de Riesgo Resultantes:
| Rango | Clasificación | Acción |
|-------|---------------|--------|
| < 20 | **Trivial** | Aceptable |
| 20-70 | **Tolerable** | Mejorar |
| 70-200 | **Moderado** | Intervenir |
| 200-400 | **Sustancial** | Acción Inmediata |
| > 400 | **Intolerable** | NO PERMITIR |

#### Función:
```python
def assess_risk(probability, exposure, consequences):
    score = probability * exposure * consequences
    if score < 20:
        return "Trivial"
    elif score < 70:
        return "Tolerable"
    # ... etc
```

### **Gestión de Cámaras**

#### Base de Datos:
```python
CREATE TABLE cameras (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,           # Ej: "Entrada Principal"
    camera_index INTEGER,       # Índice de dispositivo: 0=webcam, 1=USB2, etc
    config TEXT                 # JSON con configuración personalizada
)
```

#### Funciones:
- `list_cameras()`: Obtiene todas las cámaras registradas
- `register_camera(name, index)`: Registra nueva cámara
- `get_camera_config(camera_id)`: Obtiene configuración

---


## Base de Datos

Base de datos SQLite local, archivo: safety_monitor.db
No se envian datos a servidores externos en ningun momento.

### Capacidad y tamano

| Aspecto | Valor |
|---|---|
| Tamano inicial (vacia) | ~80 KB |
| Por cada incidente (texto) | ~1 KB |
| Por cada imagen de evidencia | ~80 - 200 KB (JPEG en captures/) |
| Limite practico de la DB | Sin limite estricto (SQLite soporta hasta 281 TB) |
| Limite recomendado por rendimiento | Hasta ~50,000 incidentes sin degradacion notable |
| Imagenes de evidencia | Almacenadas en disco, no dentro del archivo .db |

El archivo safety_monitor.db solo contiene texto (registros, usuarios, logs).
Los archivos de imagen se guardan en captures/ y la DB guarda la ruta.

### Tabla: users
```sql
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,       -- PBKDF2-HMAC-SHA256 + sal aleatoria
    role     TEXT DEFAULT 'supervisor',
    qr_code  TEXT UNIQUE,
    email    TEXT
)
```

Usuario por defecto al iniciar por primera vez:
- Usuario: admin
- Contrasena: admin123  -- CAMBIAR INMEDIATAMENTE
- Rol: admin
- QR: ADMIN001

### Tabla: incidents
```sql
CREATE TABLE incidents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_name     TEXT,
    type            TEXT,          -- "Falta Casco", "Falta Chaleco"
    timestamp       TEXT,          -- "2026-03-17 22:30:01"
    description     TEXT,
    status          TEXT DEFAULT 'open',
    evidence_path   TEXT,          -- ruta relativa en captures/
    user_identified TEXT,
    occurrences     INTEGER DEFAULT 1,
    last_seen       TEXT
)
```

### Tabla: audit_logs
```sql
CREATE TABLE audit_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT,
    performed_by    TEXT,
    action          TEXT,
    target_user_id  INTEGER,
    details         TEXT
)
```

### Tabla: qr_downloads
```sql
CREATE TABLE qr_downloads (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,
    downloaded_by   INTEGER,    -- FK: users.id
    target_user_id  INTEGER,    -- FK: users.id
    download_path   TEXT
)
```

### Funciones principales (database.py)
```python
# Usuarios
register_user(username, password, qr_code, role) -> bool
authenticate_user(username, password) -> (id, username, role) | None
get_user_by_qr(qr_code) -> (id, username, role) | None
list_users() -> [(id, username, role, qr_code), ...]
update_user(user_id, username, qr_code) -> bool
update_user_role(user_id, role) -> bool
delete_user(user_id) -> bool
reset_user_password(performed_by, target_user_id, new_password) -> bool

# Incidentes
register_incident(camera_name, incident_type, description, user_identified, evidence_path, dedupe_window_minutes)
list_incidents() -> [(id, camera_name, type, timestamp, ...), ...]
update_incident(incident_id, status)

# Reportes
generate_report(output_path) -> str              # CSV
generate_report_xlsx(year, month, output_path) -> str  # Excel con imagenes
generate_report_by_period(year, month, output_path) -> str

# Auditoría
log_audit(performed_by, action, target_user_id, details)
get_audit_logs(limit=100) → [logs del usuario y cambios]
```

---

## Modulos del Sistema

### flask_server.py - Servidor principal

| Ruta | Metodo | Descripcion |
|------|--------|-------------|
| / | GET | Redirige al dashboard o login segun sesion |
| /dashboard | GET | Pagina de monitoreo en tiempo real |
| /manage | GET | Gestion de usuarios |
| /detect_json | POST | Recibe frame JPEG, ejecuta YOLO, devuelve JSON |
| /api/heartbeat | POST | Senhal de vida del navegador |
| /api/login | POST | Autenticacion |
| /api/me | GET | Datos del usuario en sesion |
| /api/logout | POST | Cierre de sesion |
| /api/users | GET/POST | Lista o crea usuarios |
| /api/users/<id> | PUT/DELETE | Edita o elimina usuario |
| /api/incidents | GET | Lista incidentes |
| /api/last_incidents | GET | Ultimos incidentes recientes |
| /api/last_qr | GET | Ultimo escaneo QR registrado |
| /api/report/xlsx | GET | Descarga reporte Excel |

### config.py - Configuracion global
```python
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(PROJECT_ROOT, 'runs/detect/train9/weights/best.pt')
DB_PATH      = os.path.join(PROJECT_ROOT, 'safety_monitor.db')
CAPTURES_DIR = os.path.join(PROJECT_ROOT, 'captures')

DEFAULT_CONF   = 0.9   # Umbral de confianza YOLO (0.0 - 1.0)
ALERT_COOLDOWN = 10    # Segundos minimos entre alertas del mismo tipo
QR_COOLDOWN    = 5     # Segundos minimos entre escaneos del mismo QR
```

### observer.py - Analisis de riesgos (Metodo William Fine)

Formula: Nivel de Riesgo = Probabilidad x Exposicion x Consecuencias

| Puntaje | Clasificacion | Accion Recomendada |
|---------|---------------|--------------------|
| < 20 | Trivial | Aceptable |
| 20 - 70 | Tolerable | Revisar periodicamente |
| 70 - 200 | Moderado | Intervencion planificada |
| 200 - 400 | Sustancial | Accion inmediata |
| > 400 | Intolerable | Detener actividad |


---

## Guia de Uso

### Inicio de Sesión

1. **Accede a**: `http://localhost:8000`
2. **Credenciales Predeterminadas**:
   - Username: `admin`
   - Password: `admin123` **CAMBIAR en producción**
3. **Cambiar Contraseña**: Admin → Perfil → Cambiar Contraseña

### Monitor en Vivo

1. **Tab: Monitor en Vivo**
2. **Click**: "Iniciar Transmisión WebRTC"
3. **Sistema Detectará Automáticamente**:
   - Personas sin chaleco de seguridad
   - Personas sin Casco
   - Códigos QR cercanos
4. **Alertas**: Se mostrarán en tiempo real

### Gestión de Usuarios (Admin)

1. **Tab: Admin**
2. **Sección: Gestión de Usuarios**
3. **Crear nuevo usuario**:
   - Username: `nombre_apellido`
   - Contraseña: Dejar vacía (genera aleatoria)
   - Click: "Registrar Usuario"
4. **Generar QR**:
   - Seleccionar usuario de lista
   - Click: "Generar QR"
   - Descarga PDF con código QR imprimible

### Reportes y Análisis

1. **Tab: Reportes**
2. **Ver**:
   - Historial de incidentes
   - Gráficos por tipo de evento
   - Ranking de usuarios más incidentes
   - Estadísticas por cámara
3. **Exportar**:
   - PDF: Informe completo
   - CSV: Datos brutos para Excel

### Configuración

1. **Tab: Admin → Configuración**
2. **Parámetros Ajustables**:
   - `DEFAULT_CONF`: Umbral de confianza YOLOv8 (0.0-1.0)
   - `ALERT_COOLDOWN`: Segundos entre alertas repetidas
   - `QR_COOLDOWN`: Segundos entre detecciones del mismo QR
   - Cámaras: Agregar/editar cámaras físicas


---

## Configuracion Avanzada

### Cambiar el umbral de confianza del modelo

Editar config.py:
```python
DEFAULT_CONF = 0.45  # Mas sensible (menos falsos negativos)
DEFAULT_CONF = 0.90  # Mas estricto (menos falsos positivos)
```
Recomendacion: comenzar con 0.45 y ajustar segun iluminacion del entorno.

### Reemplazar el modelo YOLOv8

1. Entrenar nuevo modelo:
```bash
yolo task=detect mode=train model=yolov8n.pt data=Safety-vest---v4-1/data.yaml epochs=100 imgsz=416
```
2. Verificar que exista el archivo de pesos:
```
runs/detect/trainX/weights/best.pt
```
3. Actualizar MODEL_PATH en config.py si el directorio cambia.

### Backup y restauracion de datos

```bash
# Backup
copy safety_monitor.db safety_monitor_backup_YYYYMMDD.db

# Restaurar
copy safety_monitor_backup_YYYYMMDD.db safety_monitor.db
```

### Reinicio completo (borrar todos los datos)

Para dejar el sistema en estado de fabrica sin modificar el codigo:
```powershell
Remove-Item safety_monitor.db, incidentes.log, incidents_raw.csv, reporte_analizado.xlsx -ErrorAction SilentlyContinue
Get-ChildItem captures\ | Remove-Item -Force
python -c "import database; database.init_db()"
```
Esto recrea la base de datos con el usuario admin/admin123 solamente.

---

## Solucion de Problemas

### El servidor no inicia
```
Verificar:
1. Python instalado: python --version
2. Dependencias: pip install -r requirement.txt
3. Puerto 8000 libre: netstat -an | findstr 8000
4. Revisar mensaje de error en la ventana de comandos
```

### No aparecen recuadros de deteccion
```
Verificar:
1. Que el modelo exista: runs/detect/train9/weights/best.pt
2. Reducir DEFAULT_CONF en config.py (probar con 0.45)
3. Mejorar la iluminacion del area supervizada
4. Abrir DevTools (F12) -> Consola -> buscar errores de fetch
5. Revisar los logs del servidor
```

### La camara no funciona en el navegador
```
Verificar:
1. Permitir acceso a camara en el navegador (icono de candado en la URL)
2. Windows: Configuracion -> Privacidad -> Camara -> Permitir acceso
3. Cerrar otras aplicaciones que usen la camara
4. Usar Chrome o Edge (mejor soporte WebRTC)
```

### Los codigos QR no se leen
```
Verificar:
1. pip install pyzbar pillow
2. Buena iluminacion y camara enfocada al QR
3. El usuario debe estar registrado en la base de datos
4. En algunos sistemas Windows se pueden necesitar las DLLs de zbar adicionales
```

### El servidor no se cierra al cerrar el navegador
```
El watchdog espera 15 segundos antes de cerrar.
Si el proceso persiste, terminar manualmente:
  taskkill /F /IM python.exe
```

---

## Seguridad

### Autenticacion
- Contrasenas protegidas con PBKDF2-HMAC-SHA256, 100,000 iteraciones y sal aleatoria de 16 bytes
- Sesiones firmadas con itsdangerous usando clave configurable en la variable de entorno SAFEBUILD_SECRET
- Registro de auditoria: cada cambio de contrasena queda en audit_logs

### Privacidad
- Todo el procesamiento ocurre en la maquina local, sin comunicacion con servidores externos
- Imagenes de evidencia almacenadas localmente en captures/
- Base de datos SQLite portable y completamente local

### Recomendaciones para produccion
- Cambiar inmediatamente la contrasena del usuario admin (por defecto: admin123)
- Establecer una clave secreta fuerte:
  set SAFEBUILD_SECRET=clave_segura_larga_aleatoria
- Hacer backups regulares de safety_monitor.db
- Limitar acceso fisico al equipo donde corre el servidor

---

## Casos de Uso

### Deteccion de incumplimiento de EPP
```
1. Operario entra al area sin casco
2. YOLOv8 detecta "not_helmet" con confianza >= umbral configurado
3. El frontend dibuja recuadro rojo con etiqueta "Falta Casco 90%"
4. El backend registra el incidente en la BD con captura de imagen
5. Si hay QR visible, el incidente queda vinculado al nombre del trabajador
6. El administrador puede revisar el historial en el dashboard
```

### Generacion de reporte
```
1. Admin accede a /manage
2. Descarga reporte Excel del periodo deseado
3. El Excel incluye incidentes, ocurrencias, e imagenes de evidencia incrustadas
4. Grafico circular de incidentes por camara incluido automaticamente
```

### Alta de nuevo trabajador
```
1. Admin accede a /manage
2. Completa nombre de usuario, contrasena y rol
3. Se genera un QR unico para ese usuario
4. Descarga el codigo QR como imagen para imprimir y entregar al trabajador
5. El trabajador muestra el QR ante la camara para identificarse
```

---

## Referencias

| Componente | Documentacion |
|---|---|
| YOLOv8 | https://docs.ultralytics.com/ |
| Flask | https://flask.palletsprojects.com/ |
| pyzbar | https://github.com/NaturalHistoryMuseum/pyzbar |
| Metodo William Fine | Implementado en observer.py |
| openpyxl | https://openpyxl.readthedocs.io/ |

---

## Soporte

Para reportar problemas:
1. Verificar Python 3.9+: python --version
2. Reinstalar dependencias: pip install -r requirement.txt --upgrade
3. Revisar los mensajes de error en la ventana de comandos al ejecutar python flask_server.py
4. Revisar la base de datos: safety_monitor.db