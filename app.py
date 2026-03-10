# app.py
# SafeBuild - Streamlit + streamlit-webrtc (cola de eventos para procesar Subject en hilo principal)

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av
import cv2
import numpy as np
import os
import time
from datetime import datetime
from ultralytics import YOLO
from queue import Queue, Empty

# módulos del proyecto
from config import MODEL_PATH, DEFAULT_CONF, CAPTURES_DIR, PROJECT_ROOT
from observer import SafetyMonitorSubject, AlertLogger, IncidentRegistrar, RankingUpdater
from database import init_db, list_incidents, generate_report

# pyzbar (QR)
try:
    import pyzbar.pyzbar as pyzbar
except Exception:
    pyzbar = None

# ---------------------------
# Config y setup inicial
# ---------------------------
st.set_page_config(page_title="SafeBuild Monitor", layout="wide")
st.title("SafeBuild Monitor (Web)")

# Inicializar model en session_state (carga controlada)
if "model" not in st.session_state:
    try:
        if MODEL_PATH and os.path.exists(MODEL_PATH):
            st.session_state.model = YOLO(MODEL_PATH)
            st.session_state.model_path = MODEL_PATH
        else:
            st.session_state.model = YOLO("yolov8n.pt")  # fallback
            st.session_state.model_path = "yolov8n.pt (fallback)"
    except Exception as e:
        st.error(f"No se pudo cargar modelo YOLO: {e}")
        st.session_state.model = None

# Inicializar Subject/Observers y colas para comunicar transformador -> hilo principal
if "subject" not in st.session_state:
    subj = SafetyMonitorSubject()

    # cola de eventos: el transformador colocará diccionarios aquí
    st.session_state.event_queue = Queue()

    # mensajes visibles en UI (lista simple)
    st.session_state.alert_messages = []

    # Logger adaptado: escribe a st.session_state.alert_messages (se usará desde hilo principal)
    class StreamlitAlertLogger(AlertLogger):
        def __init__(self):
            super().__init__(log_widget=None)

        def update(self, subject_obj, event_data):
            timestamp = event_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            camera = event_data.get('camera', 'webcam')
            alert_type = event_data.get('alert_type', '')
            user_ident = event_data.get('user_identified', 'unknown')
            if alert_type:
                msg = f"[{timestamp}] {camera}: {alert_type} - Usuario: {user_ident}"
            else:
                msg = f"[{timestamp}] {camera}: Evento - Usuario: {user_ident}"
            # dedupe simple
            last = st.session_state.alert_messages[-1] if st.session_state.alert_messages else None
            if last != msg:
                st.session_state.alert_messages.append(msg)

    stream_logger = StreamlitAlertLogger()
    registrar = IncidentRegistrar()
    ranking_updater = RankingUpdater({})

    subj.attach(stream_logger)
    subj.attach(registrar)
    subj.attach(ranking_updater)

    st.session_state.subject = subj
    st.session_state.ranking_updater = ranking_updater

# Asegurar DB y carpetas
init_db()
os.makedirs(CAPTURES_DIR, exist_ok=True)

# ---------------------------
# Utilidades de detección
# ---------------------------
def detect_qr_codes_in_frame(frame):
    detected = []
    if pyzbar is None:
        return detected, frame
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objs = pyzbar.decode(gray)
        for obj in objs:
            try:
                qr_data = obj.data.decode("utf-8")
            except Exception:
                continue
            rect = getattr(obj, "rect", None)
            if rect:
                x, y, w, h = rect
                cx = int(x + w / 2)
                cy = int(y + h / 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                detected.append((qr_data, cx, cy, (x, y, w, h)))
            else:
                detected.append((qr_data, None, None, None))
    except Exception:
        pass
    return detected, frame


def draw_dynamic_box(frame, x1, y1, x2, y2, label, confidence, class_name):
    """
    Dibuja un bounding box dinamico con:
    - Color basado en confianza (rojo bajo, verde alto)
    - Grosor del linea basado en tamaño del objeto
    - Label con clase y precision
    """
    # Calcular tamaño del box
    width = x2 - x1
    height = y2 - y1
    box_area = width * height
    
    # Grosor dinamico: basado en tamaño del objeto (1-5 pixeles)
    thickness = max(1, min(5, int(box_area / 20000)))
    
    # Color dinamico: basado en confianza
    # Rojo (200,0,0) → Amarillo (0,255,255) → Verde (0,255,0)
    if confidence < 0.5:
        # Rojo a amarillo
        ratio = confidence / 0.5
        b, g, r = 0, int(255 * ratio), 200
    else:
        # Amarillo a verde
        ratio = (confidence - 0.5) / 0.5
        b, g, r = 0, 255, int(200 * (1 - ratio))
    
    color = (b, g, r)
    
    # Dibujar rectangulo
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # Preparar label con clase y precision
    label_text = f"{class_name} {confidence:.2f}"
    font_scale = 0.6
    font_thickness = 1
    
    # Obtener tamaño de texto
    text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
    text_width = text_size[0]
    text_height = text_size[1]
    
    # Fondo para el texto (pequeno rectangulo)
    text_x = x1
    text_y = max(y1 - 10, text_height + 5)
    cv2.rectangle(frame, (text_x, text_y - text_height - 5), (text_x + text_width + 5, text_y + 5), color, -1)
    
    # Dibujar texto
    cv2.putText(frame, label_text, (text_x + 2, text_y - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
    
    return frame


def process_frame_with_model(frame, model):
    """
    Procesa un frame BGR y devuelve:
      - annotated_frame (ndarray BGR)
      - payload (dict) con keys: classes_detected (list), qr_map (dict), timestamp (str)
    NOTA: Dibuja boxes dinamicos con precision visible.
    """
    annotated_frame = frame.copy()
    classes_detected = []
    qr_map_by_pos = []

    # detectar QR
    try:
        qr_map_by_pos, annotated_frame = detect_qr_codes_in_frame(annotated_frame)
    except Exception:
        qr_map_by_pos = []

    qr_mapping = {}
    try:
        if model is not None:
            results = model.predict(source=frame, imgsz=416, conf=DEFAULT_CONF, verbose=False)
            if results and len(results) > 0:
                res0 = results[0]
                boxes = getattr(res0, "boxes", None)
                
                if boxes is not None and hasattr(boxes, "xyxy") and hasattr(boxes, "cls"):
                    xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else boxes.xyxy.numpy()
                    cls_ids = boxes.cls.cpu().numpy() if hasattr(boxes.cls, "cpu") else boxes.cls.numpy()
                    
                    # Obtener confianzas (scores)
                    try:
                        conf_scores = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else boxes.conf.numpy()
                    except Exception:
                        conf_scores = [DEFAULT_CONF] * len(xyxy)
                    
                    flat = []
                    
                    # Dibujar boxes dinamicos
                    for i, box in enumerate(xyxy):
                        x1, y1, x2, y2 = [int(v) for v in box]
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        cname = res0.names[int(cls_ids[i])]
                        confidence = float(conf_scores[i]) if i < len(conf_scores) else DEFAULT_CONF
                        
                        # Dibujar box dinamico
                        annotated_frame = draw_dynamic_box(annotated_frame, x1, y1, x2, y2, cname, confidence, cname)
                        
                        flat.append({
                            "class": cname, 
                            "cx": cx, 
                            "cy": cy, 
                            "bbox": (x1, y1, x2, y2),
                            "confidence": confidence,
                            "width": x2 - x1,
                            "height": y2 - y1
                        })
                    
                    # Agrupar por cercanía
                    persons = {}
                    next_pid = 1
                    for det in flat:
                        assigned = None
                        for pid, info in persons.items():
                            avgx = int(sum([c[0] for c in info["centers"]]) / len(info["centers"]))
                            avgy = int(sum([c[1] for c in info["centers"]]) / len(info["centers"]))
                            dist = ((avgx - det["cx"]) ** 2 + (avgy - det["cy"]) ** 2) ** 0.5
                            if dist < 120:
                                assigned = pid
                                break
                        if assigned is None:
                            assigned = next_pid
                            persons[assigned] = {
                                "classes": set(), 
                                "centers": [], 
                                "bboxes": [],
                                "confidences": [],
                                "distances": []
                            }
                            next_pid += 1
                        persons[assigned]["classes"].add(det["class"])
                        persons[assigned]["centers"].append((det["cx"], det["cy"]))
                        persons[assigned]["bboxes"].append(det["bbox"])
                        persons[assigned]["confidences"].append(det["confidence"])
                        
                        # Calcular distancia del objeto al centro del frame
                        frame_center_x = frame.shape[1] // 2
                        frame_center_y = frame.shape[0] // 2
                        dist_to_center = ((det["cx"] - frame_center_x) ** 2 + (det["cy"] - frame_center_y) ** 2) ** 0.5
                        persons[assigned]["distances"].append(dist_to_center)
                    
                    # map QR by proximity
                    for qr in qr_map_by_pos:
                        user_info, qx, qy, rect = qr
                        if qx is None or qy is None:
                            continue
                        best_pid = None
                        best_dist = float("inf")
                        for pid, info in persons.items():
                            avgx = int(sum([c[0] for c in info["centers"]]) / len(info["centers"]))
                            avgy = int(sum([c[1] for c in info["centers"]]) / len(info["centers"]))
                            dist = ((avgx - qx) ** 2 + (avgy - qy) ** 2) ** 0.5
                            if dist < best_dist and dist < 200:
                                best_dist = dist
                                best_pid = pid
                        if best_pid is not None:
                            qr_mapping[f"qr_{best_pid}"] = user_info
                    if qr_map_by_pos:
                        qr_mapping["any"] = qr_map_by_pos[0][0]
                    
                    # construir clases_detectadas
                    classes_detected = []
                    for pid, info in persons.items():
                        for c in info["classes"]:
                            classes_detected.append(f"{c}_{pid}")
                        if f"qr_{pid}" in qr_mapping:
                            classes_detected.append(f"qr_{pid}")
                    
                    # fallback simple
                    if not classes_detected:
                        try:
                            classes_detected = [f"{res0.names[int(c)]}" for c in cls_ids]
                        except Exception:
                            classes_detected = []
        else:
            classes_detected = []
    except Exception as e:
        print("Error en predict YOLO:", e)
        classes_detected = []
        annotated_frame = frame

    # timestamp
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cv2.putText(annotated_frame, ts, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    except Exception:
        pass

    payload = {
        "timestamp": ts,
        "classes_detected": classes_detected,
        "qr_map": qr_mapping,
    }
    return annotated_frame, payload

# ---------------------------
# Video transformer (no llama a Streamlit ni Subject)
# ---------------------------
class DetectorTransformer(VideoTransformerBase):
    def __init__(self):
        # obtener referencias ya creadas en hilo principal
        self.model = st.session_state.get("model", None)
        # tomar la cola desde session_state (Queue es thread-safe)
        self.event_queue = st.session_state.get("event_queue", None)
        self.camera_name = "webcam"

    def transform(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        try:
            annotated, payload = process_frame_with_model(img, self.model)
            # adjuntar metadata adicional
            payload.update({"camera": self.camera_name})
            # colocar en la cola si hay eventos detectados (o siempre si quieres registro)
            try:
                if self.event_queue is not None:
                    # enviar solo cuando hay detecciones para reducir carga
                    if payload.get("classes_detected"):
                        self.event_queue.put(payload)
            except Exception as e:
                print("Error poniendo evento en cola:", e)
            # asegurar ndarray
            if not isinstance(annotated, np.ndarray):
                annotated = np.array(annotated)
            return av.VideoFrame.from_ndarray(annotated, format="bgr24")
        except Exception as e:
            print("Error transform:", e)
            return frame

# ---------------------------
# Interfaz Streamlit y consumo de cola
# ---------------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.header("Cámara (cliente)")
    st.write("Presiona Start y permite el acceso a la cámara cuando el navegador lo solicite.")

    webrtc_ctx = webrtc_streamer(
        key="safebuild-webrtc",
        mode=WebRtcMode.SENDRECV,
        video_transformer_factory=DetectorTransformer,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )


    if webrtc_ctx and webrtc_ctx.state.playing:
        st.info("Cámara activa. Procesando detecciones...")
    else:
        st.warning("Cámara inactiva. Presiona Start para iniciar.")

# Procesar todos los eventos pendientes en la cola (esto se ejecuta en el hilo principal Streamlit)
queue_obj = st.session_state.get("event_queue", None)
if queue_obj is not None:
    processed = 0
    while True:
        try:
            ev = queue_obj.get_nowait()
        except Empty:
            break
        try:
            # enviar al Subject en hilo principal (seguirá notify y observers)
            classes = ev.get("classes_detected", [])
            qr_map = ev.get("qr_map", None)
            ts = ev.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            camera = ev.get("camera", "webcam")
            # subject.detect_event espera listado clases y camera y optional user_identified
            st.session_state.subject.detect_event(classes, camera, user_identified=qr_map, evidence_path=None)
        except Exception as e:
            print("Error procesando evento de cola:", e)
        processed += 1
    if processed:
        # opcional: forzar rerun para que UI muestre inmediatamente nuevas alertas (si lo deseas)
        # st.experimental_rerun()
        pass

with col2:
    st.header("Logs / Alerts")
    recent = st.session_state.alert_messages[-30:]
    if recent:
        for msg in reversed(recent):
            st.write(msg)
    else:
        st.write("No hay alertas.")

    st.markdown("---")
    st.subheader("Ranking de cámaras")
    ranking = st.session_state.ranking_updater.ranking_counter if hasattr(st.session_state.ranking_updater, "ranking_counter") else {}
    if ranking:
        for i, (name, cnt) in enumerate(sorted(ranking.items(), key=lambda x: x[1], reverse=True), start=1):
            st.write(f"{i}. {name}: {cnt} alertas")
    else:
        st.write("Sin datos aún.")

    st.markdown("---")
    if st.button("Generar reporte (CSV)"):
        try:
            out = os.path.join(PROJECT_ROOT, f"reporte_{int(time.time())}.csv")
            path = generate_report(output_path=out)
            st.success(f"Reporte generado: {path}")
        except Exception as e:
            st.error(f"Error generando reporte: {e}")

    if st.button("Ver incidentes (últimos 50)"):
        try:
            incs = list_incidents()
            for inc in incs[:50]:
                st.write(inc)
        except Exception as e:
            st.error(f"Error listando incidentes: {e}")

st.markdown("---")
st.caption("SafeBuild Web - Versión convertida desde PyQt5 a Streamlit")
