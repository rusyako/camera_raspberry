import os

RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

MOTION_THRESHOLD = 5000
MOTION_TIMEOUT = 10
FLASK_PORT = 5000
FLASK_HOST = "0.0.0.0"
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 20
