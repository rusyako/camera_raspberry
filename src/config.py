import os

RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

MOTION_THRESHOLD = 5000
MOTION_TIMEOUT = 20
FLASK_PORT = 5000
FLASK_HOST = "0.0.0.0"
FRAME_WIDTH = 1024
FRAME_HEIGHT = 600
FPS = 20
DISK_MIN_FREE_MB = 500
USB_CHECK_INTERVAL = 40
RECORD_MAX_DAYS = 30
FPS_ACTIVE = 20
FPS_IDLE = 5
PREBUFFER_SECS = 5
