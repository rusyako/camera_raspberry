import cv2
import time
import threading
from datetime import datetime
from .config import RECORDINGS_DIR, MOTION_TIMEOUT, FRAME_WIDTH, FRAME_HEIGHT, FPS

class Recorder:
    def __init__(self):
        self.writer = None
        self.recording = False
        self.last_motion_time = 0
        self.lock = threading.Lock()

    def _get_filename(self):
        return f"{RECORDINGS_DIR}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

    def signal_motion(self):
        with self.lock:
            self.last_motion_time = time.time()
            if not self.recording:
                self._start_recording()

    def _start_recording(self):
        filename = self._get_filename()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
        self.recording = True
        print(f"[REC] Started: {filename}")

    def write_frame(self, frame):
        with self.lock:
            if self.recording and self.writer:
                self.writer.write(frame)

    def check_timeout(self):
        with self.lock:
            if self.recording and (time.time() - self.last_motion_time) > MOTION_TIMEOUT:
                self._stop_recording()

    def _stop_recording(self):
        if self.writer:
            self.writer.release()
            self.writer = None
        self.recording = False
        print("[REC] Stopped")

    def release(self):
        self._stop_recording()
