# 🛡️ SafeBuild Monitor - Sistema Inteligente de Monitoreo de Seguridad en Obras

**Un sistema web de detección en tiempo real de incidentes de seguridad en construcciones utilizando IA (YOLOv8) y análisis de riesgos.**

<<<<<<< HEAD
---

## Contenido
1. [Características Principales](#características-principales)
2. [Instalación Rápida](#instalación-rápida)
3. [Funcionalidades Detalladas](#funcionalidades-detalladas)
4. [Requisitos del Sistema](#requisitos-del-sistema)
5. [Guía de Uso](#guía-de-uso)
6. [Funciones por Módulo](#funciones-por-módulo)
7. [Base de Datos](#base-de-datos)
8. [Configuración Avanzada](#configuración-avanzada)
=======
## Riesgos
- William Fine integrado en observer.py para severidad.
- Pruebas: Simula con videos; precisión >90%.
>>>>>>> b50a18c0e56f16fadfdab1bd888d654bf68c2258

---

## Características Principales

### Detección de Equipos de Protección (EPP)
- **Detección en Tiempo Real**: Identifica automáticamente a personas sin arnés de seguridad o chaleco de seguridad
- **Modelo YOLOv8 Entrenado**: Precisión superior al 90% en detección de chaleco de seguridad
- **Alertas Automáticas**: Notifica inmediatamente cuando se detecta ausencia de EPP

### Identificación de Usuarios mediante QR
- **Lectura de Códigos QR**: Identifica automáticamente trabajadores mediante códigos QR integrados
- **Mapeo por Proximidad**: Asocia códigos QR detectados con la persona más cercana en la cámara
- **Fallback para Identidades Desconocidas**: Si no hay QR, registra como "usuario desconocido"

### Gestión de Alertas Inteligentes
- **Sistema de Observadores**: Patrón Observer para reaccionar a eventos de seguridad
- **Deduplicación Automática**: Evita alertas repetidas del mismo evento en ventanas de 3 segundos
- **Cooldown Configurable**: Controla la frecuencia de alertas por tipo de evento

### Análisis de Riesgos (Matriz William Fine)
- **Evaluación de Severidad**: Calcula el nivel de riesgo de cada incidente
- **Fórmula William Fine**: Severidad = Probabilidad × Exposición × Consecuencia
- **Clasificación de Riesgos**: Categoriza incidentes en Trivial, Tolerable, Moderado, Sustancial o Intolerable

### Gestión de Base de Datos
- **SQLite Local**: Base de datos integrada con seguridad mediante PBKDF2-HMAC-SHA256
- **Registro de Incidentes**: Almacena todos los eventos con evidencia y contexto
- **Logs de Auditoría**: Registra todas las acciones administrativas
- **Historial de Descargas de QR**: Tracking de QR descargados por administradores

### Sistema de Usuarios y Permisos
- **Roles de Usuario**: Admin, Supervisor, Operario
- **Autenticación Segura**: Contraseñas hasheadas con sal
- **Generación de Códigos QR**: Admin puede generar QR para cada trabajador
- **Auditoría de Cambios**: Registra quién cambió contraseñas y cuándo

### Reportes y Análisis
- **Reportes Detallados**: Generación en PDF con historial de incidentes
- **Estadísticas por Cámara**: Análisis de frecuencia de incidentes
- **Ranking de Usuarios**: Identifica usuarios con mayor número de incidentes
- **Exportación de Datos**: Descarga de reportes en múltiples formatos

---

## Instalación Rápida

### Opción 1: Batch File (Windows - Más Simple)
```bash
# Solo haz doble-clic en:
EJECUTAR.bat
# O
RUN.bat
```

### Opción 2: PowerShell (Windows - Más Moderno)
```powershell
# Ejecutar primero una sola vez:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego:
.\RUN.ps1
```

### Opción 3: Manual (Cualquier Sistema)
```bash
# 1. Instala Python 3.9+ desde https://www.python.org/downloads/
# 2. Instala dependencias:
pip install -r requirement.txt

# 3. Entrena el modelo (opcional, ya incluido):
yolo task=detect mode=train model=yolov8n.pt data=Safety-vest---v4-1/data.yaml epochs=100

# 4. Ejecuta la aplicación:
streamlit run app.py

# 5. Accede a:
# http://localhost:8501
```

---

## 🔧 Funcionalidades Detalladas

### Monitor en Vivo
- Transmisión WebRTC: Acceso en tiempo real a la cámara web
- Análisis en Vivo: Procesamiento de frames a velocidad de video
- Visualización Dinamica: Dibuja bounding boxes adaptativos basados en tamaño y confianza
- Precision Visible: Cada detección muestra su score de confianza (0.00 a 1.00)
- Indicador de Confianza por Color: Rojo (baja) -> Amarillo (media) -> Verde (alta)
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

### Estructura de Tablas

#### 1. **users**
```python
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,       # "juan_perez"
    password TEXT,              # Hasheada con PBKDF2-HMAC-SHA256
    role TEXT DEFAULT 'supervisor',  # 'admin', 'supervisor', 'operario'
    qr_code TEXT UNIQUE         # "USER_12345ABC"
)
```

**Usuario por Defecto**:
- Username: `admin`
- Password: `admin123`
- Role: `admin`
- QR: `ADMIN001`

#### 2. **incidents**
```python
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    camera_name TEXT,           # "Frente de Obra A"
    type TEXT,                  # "MISSING_SAFETY_VEST", "MISSING_HARNESS", etc
    timestamp TEXT,             # ISO 8601: "2024-03-10T14:30:45"
    description TEXT,           # Detalles del incidente
    status TEXT DEFAULT 'open', # 'open', 'reviewed', 'resolved'
    evidence_path TEXT,         # Ruta a screenshot: "captures/incident_123.png"
    user_identified TEXT,       # "juan_perez" o "unknown"
    occurrences INTEGER DEFAULT 1,  # Conteo si es duplicado
    last_seen TEXT              # Timestamp de última ocurrencia
)
```

#### 3. **audit_logs**
```python
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,              # Cuándo ocurrió
    performed_by TEXT,           # Username de quién hizo la acción
    action TEXT,                 # "PASSWORD_RESET", "QR_GENERATED", etc
    target_user_id INTEGER,      # Usuario afectado
    details TEXT                 # Información adicional JSON
)
```

#### 4. **qr_downloads**
```python
CREATE TABLE qr_downloads (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    downloaded_by INTEGER,       # Foreign Key: users.id
    target_user_id INTEGER,      # Foreign Key: users.id
    download_path TEXT           # Donde se guardó el PDF
)
```

### Funciones de Base de Datos

#### Usuarios:
```python
register_user(username, password, qr_code=None) → bool
authenticate_user(username, password) → (id, username, role) or None
get_user_by_qr(qr_code) → (id, username, role) or None
list_users() → [(id, username, role, qr_code), ...]
get_user_by_id(user_id) → (id, username, role, qr_code) or None
reset_user_password(performed_by, target_user_id, new_password) → bool
```

#### Incidentes:
```python
register_incident(camera_name, incident_type, description, evidence_path, user_identified)
list_incidents() → [(id, camera_name, type, timestamp, ...), ...]
generate_report(output_path) → PDF con estadísticas
get_incidents_by_status(status) → [incidentes filtrados]
update_incident_status(incident_id, new_status) → bool
```

#### Auditoría:
```python
log_audit(performed_by, action, target_user_id, details)
get_audit_logs(limit=100) → [logs del usuario y cambios]
```

---

## Guía de Uso

### Inicio de Sesión

1. **Accede a**: `http://localhost:8501`
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

## Funciones por Módulo

### app.py - Interfaz Web (Streamlit)

Funcion: `draw_dynamic_box(frame, x1, y1, x2, y2, label, confidence, class_name)`
```python
# Dibuja un bounding box dinamico con:
# - Color basado en confianza (rojo bajo < 50%, amarillo medio, verde alto > 75%)
# - Grosor dinamico basado en tamaño del objeto (1-5 pixeles)
# - Label con clase y precision en formato: "clase 0.95"
# - Fondo de rectangulo para mejor contraste del texto

# Valores de color segun confianza:
# - confidence < 0.5: Transicion de Rojo (200,0,0) a Amarillo (0,255,255)
# - confidence >= 0.5: Transicion de Amarillo a Verde (0,255,0)
#
# Grosor = max(1, min(5, int(area_del_box / 20000)))
```

Funcion: `detect_qr_codes_in_frame(frame)`
```python
# Entrada: frame BGR (numpy array)
# Salida: ([(qr_text, cx, cy, rect), ...], annotated_frame)
# Usa: pyzbar para decodificar QRs
```

Funcion: `process_frame_with_model(frame, model)`
```python
# Entrada: frame BGR, modelo YOLO
# Salida: (annotated_frame, payload_dict)
#
# payload contiene:
#   - classes_detected: lista de clases encontradas con ID
#   - qr_mapping: mapeo QR -> usuario identificado
#   - timestamp: ISO 8601
#
# Internamente calcula:
#   - Confianza individual para cada detección
#   - Tamaño (width x height) de cada caja
#   - Distancia al centro del frame
#   - Agrupacion de detecciones por proximidad
```

Clase: `DetectorTransformer(VideoTransformerBase)`
```python
# Procesa frames en tiempo real desde WebRTC
# transform(frame): Procesa frame y devuelve anotado
# Coloca eventos en event_queue para procesamiento en hilo principal
```

Funcion: `capture_evidence(frame, incident_type)`
```python
# Guarda frame como evidencia en captures/
# Retorna: ruta del archivo
```

### **observer.py** - Patrón Observer

#### Clase: `SafetyMonitorSubject`
```python
__init__()                      # Inicializa state y observers
attach(observer: Observer)      # Registra un observador
detach(observer: Observer)      # Desregistra un observador
notify(event_data: dict)        # Notifica a todos los observadores

# Atributos:
_state: dict                    # Estado actual
_observers: List[Observer]      # Lista de observadores
_recent_event_times: dict       # Deduplicación (evento -> último timestamp)
_pending_events: dict           # Eventos esperando QR identification
PENDING_WINDOW = 4.0 segundos   # Ventana para esperar QR
```

#### Clase: `AlertLogger`
```python
update(subject, event_data)     # Registra alerta en UI
# Mensaje: "[TIMESTAMP] CÁMARA: ALERTA - Usuario: IDENTIFICADO"
```

#### Clase: `IncidentRegistrar`
```python
update(subject, event_data)     # Guarda en BD
# Llama: register_incident() con datos del evento
```

#### Clase: `RankingUpdater`
```python
update(subject, event_data)     # Actualiza contador de incidentes por usuario
get_ranking() → dict            # Retorna {usuario -> conteo}
```

### **database.py** - Gestión de Datos

#### Funciones de Usuario:
```python
register_user(username, password, qr_code)
authenticate_user(username, password) → (id, user, role)
get_user_by_qr(qr_code) → user
list_users() → [users]
update_password(user_id, new_password)
reset_user_password(performed_by, target_user_id, new_password)
```

#### Funciones de Incidentes:
```python
register_incident(camera_name, type, description, evidence_path, user_id)
list_incidents() → [incidents]
get_incidents_by_status(status) → [incidents]
update_incident_status(incident_id, status)
```

#### Funciones de Reportes:
```python
generate_report(output_path) → PDF
get_incident_statistics() → {por cámara, por tipo, etc}
```

### **config.py** - Configuración Global

```python
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'Safety-vest---v4-1')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'runs/detect/train9/weights/best.pt')
DB_PATH = os.path.join(PROJECT_ROOT, 'safety_monitor.db')
CAPTURES_DIR = os.path.join(PROJECT_ROOT, 'captures')

DEFAULT_CONF = 0.4              # Umbral de confianza YOLOv8
ALERT_COOLDOWN = 10             # Segundos mínimos entre alertas
QR_COOLDOWN = 5                 # Segundos entre detecciones del mismo QR
```

### **camera_widget.py** - Captura de Video

```python
class CameraCapture:
    __init__(camera_index=0)    # Inicializa cámara
    capture_frame() → frame     # Lee siguiente frame
    release()                   # Libera recurso
    is_opened() → bool          # Verifica si está activa
```

### **main_window.py** - Ventana Principal (Legacy)

> Nota: Actualmente la UI principal está en `app.py` (Streamlit). Este archivo puede ser para interfaz GUI alternativa.

---

## Configuración Avanzada

### Cambiar Modelo YOLOv8

Modelo Actual: train9 (precision > 90%)
Ubicacion: runs/detect/train9/weights/best.pt

Para entrenar un nuevo modelo:

1. **Entrenar Nuevo Modelo**:
```bash
yolo task=detect mode=train model=yolov8m.pt data=Safety-vest---v4-1/data.yaml epochs=150 imgsz=640
```

2. **Actualizar Ruta en config.py** si sales del train9:
```python
# Cambio actual (train9):
MODEL_PATH = os.path.join(PROJECT_ROOT, 'runs/detect/train9/weights/best.pt')

# Cambio a nuevo modelo (ej. train10):
MODEL_PATH = os.path.join(PROJECT_ROOT, 'runs/detect/train10/weights/best.pt')
```

3. **Verificar que el archivo existe**:
```bash
# Confirma que existe el archivo best.pt en la ruta
dir runs/detect/train9/weights/
```

### Ajustar Umbral de Confianza

**En config.py**:
```python
DEFAULT_CONF = 0.5  # Valores más altos = menos falsos positivos (pero más falsos negativos)
```

### Configurar Múltiples Cámaras

**En la UI Admin**:
1. Tab: **Admin**
2. Sección: **Configurar Cámaras**
3. **Agregar Cámara**:
   - Nombre: `Área de Almacén`
   - Tipo: `Webcam` / `IP Camera` / `USB`
   - Índice/URL: `0` / `http://192.168.1.100:8080`

### Habilitar SSL/HTTPS (Producción)

```bash
# Generar certificados
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Ejecutar con SSL
streamlit run app.py --logger.level=debug --server.sslKeyPath=key.pem --server.sslCertPath=cert.pem
```

### Backup de Base de Datos

```bash
# Copiar BD
copy safety_monitor.db safety_monitor_backup_2024-03-10.db

# Restaurar
copy safety_monitor_backup_2024-03-10.db safety_monitor.db
```

---

## Casos de Uso

### Caso 1: Detección de Incumplimiento de PPE
```
1. Operario entra al área sin chaleco
2. YOLOv8 detecta "person" sin "safety_vest"
3. Sistema genera alerta: "MISSING_SAFETY_VEST"
4. Si QR cercano → identifica usuario
5. Registra en BD con nombre del operario
6. Admin revisa en Reportes
```

### Caso 2: Identificación de Intruso
```
1. Persona desconocida entra a área restringida
2. No lleva QR ni está registrada
3. Sistema alerta: "INTRUDER_ALERT - Usuario: unknown"
4. Se captura screenshot como evidencia
5. Admin revisa y marca como "Acción Requerida"
6. Se registra en auditoría
```

### Caso 3: Análisis de Tendencias
```
1. Admin accede a Reportes
2. Ve gráfico: "Juan Pérez tiene 15 incidentes en 2 semanas"
3. Decide capacitación específica
4. Monitorea mejora en las próximas 2 semanas
5. Genera reporte de eficacia
```

---

## Estadísticas y Métricas

La aplicación rastrea automáticamente:

- **Total de Incidentes**: Conteo global
- **Incidentes por Tipo**: MISSING_VEST, MISSING_HARNESS, INTRUDER
- **Incidentes por Cámara**: Cuál área tiene más problemas
- **Incidentes por Usuario**: Ranking de frecuencia
- **Tasa de Resolución**: % de incidentes cerrados
- **Tiempo Promedio de Resolución**: Días desde incidente til cierre
- **Tendencias**: Gráficos de incidentes a lo largo del tiempo

---

## Seguridad

### Autenticación y Encriptación
- Contraseñas hasheadas con **PBKDF2-HMAC-SHA256** + sal
- **100,000 iteraciones** de hash (estándar OWASP)
- Auditoría de cambios de contraseña

### Privacidad
- BD local (no se envía datos a servidores externos)
- Evidencias guardadas localmente
- Logs completos para auditoría

### Buenas Prácticas
- **CAMBIAR contraseña default admin123 inmediatamente**
- Hacer backup regular de `safety_monitor.db`
- Usar HTTPS en producción (ver Configuración Avanzada)
- Limitar acceso a carpetas de archivos locales

---

## Solución de Problemas

### Problema: "Modelo no carga"
```
Solución:
1. Verifica ruta en config.py
2. Descarga modelo: 
   yolo task=detect mode=train model=yolov8n.pt data=Safety-vest---v4-1/data.yaml
3. Verifica que exista: runs/detect/train9/weights/best.pt
```

### Problema: "Cámara no funciona"
```
Solución:
1. Verifica que os.path.join(PROJECT_ROOT, 'runs/detect/train9/weights/best.pt') no esté vacía
2. Permite acceso a cámara en Windows:
   Configuración → Privacidad → Cámara → Allow access
3. Intenta con índice diferente (0, 1, 2...)
```

### Problema: "QR no se detecta"
```
Solución:
1. Asegúrate que la cámara esté enfocada a código QR
2. Mejora iluminación
3. Verifica que pyzbar esté instalado:
   pip install pyzbar python-bidi pillow
4. En Windows, puede requerir librerías adicionales
```

### Problema: "Alertas muy frecuentes / muy pocas"
```
Solución:
1. Aumenta DEFAULT_CONF en config.py para menos falsos positivos
2. Ajusta ALERT_COOLDOWN para menos repetición
3. Entrena modelo con más datos si es impreciso
```

---

## Arquitectura

```
SafeBuild Monitor
├── Frontend (Streamlit Web UI)
│   ├── Monitor en Vivo (WebRTC)
│   ├── Reportes (Gráficos y PDF)
│   ├── Admin Panel (Usuarios, Cámaras, Config)
│   └── Logs (Eventos en tiempo real)
│
├── Backend (Python)
│   ├── app.py (Orquestador principal)
│   ├── observer.py (Sistema de alertas)
│   ├── database.py (BD SQLite)
│   └── config.py (Configuración global)
│
├── IA/ML (YOLOv8)
│   ├── Modelo entrenado: runs/detect/train9/weights/best.pt
│   └── Dataset: Safety-vest---v4-1/
│
└── Datos
    ├── safety_monitor.db (BD)
    ├── captures/ (Evidencias fotográficas)
    └── incidentes.log (Log de eventos)
```

---

## Referencias y Documentación

### Modelo YOLOv8
- Repositorio: https://github.com/ultralytics/ultralytics
- Documentación: https://docs.ultralytics.com/

### Streamlit
- Documentación: https://docs.streamlit.io/
- WebRTC: https://github.com/whitphx/streamlit-webrtc

### Método William Fine
- Referencia: DOCUMENTO P4.docx (incluido en proyecto)
- Fórmula: Riesgo = Probabilidad × Exposición × Consecuencias

---

## Soporte y Actualizaciones

Para reportar bugs o solicitar características:
1. Verifica que tengas **Python 3.9+**
2. Ejecuta: `pip install -r requirement.txt --upgrade`
3. Comprueba los logs: `incidentes.log`
4. Consulta la BD: `safety_monitor.db`