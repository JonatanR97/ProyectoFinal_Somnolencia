from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "face_landmarker.task"

CAMERA_INDEX = 0
FRAME_WIDTH = 760
FRAME_HEIGHT = 920
FPS = 15

MIN_FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_PRESENCE_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

EAR_THRESHOLD = 0.22

EAR_THRESHOLD = 0.22
DROWSINESS_TIME_SECONDS = 2.0

WINDOW_NAME = "Detector de Somnolencia"

PANEL_WIDTH = 360

# Configuración para detección de bostezos
MAR_THRESHOLD = 0.25
YAWN_TIME_SECONDS = 1.5

# Evaluación de fatiga
YAWN_LIMIT = 3
YAWN_WINDOW_SECONDS = 300  # 5 minutos

# Puntuación gradual de fatiga
FATIGUE_YAWN_POINTS = 12
FATIGUE_EYE_ALERT_POINTS = 35

# Puntos que disminuyen por segundo sin nuevos eventos
FATIGUE_DECAY_PER_SECOND = 0.5


# Límites de nivel
FATIGUE_ATTENTION_THRESHOLD = 30
FATIGUE_ALERT_THRESHOLD = 60
FATIGUE_CRITICAL_THRESHOLD = 85