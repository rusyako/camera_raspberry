import cv2
import os
import time
import glob
import shutil
import threading
from datetime import datetime
from .config import RECORDINGS_DIR, MOTION_TIMEOUT, FRAME_WIDTH, FRAME_HEIGHT, FPS, DISK_MIN_FREE_MB


class Recorder:
    def __init__(self):
        self.writer = None
        self.recording = False
        self.last_motion_time = 0
        self.lock = threading.Lock()

    def _get_filename(self):
        return f"{RECORDINGS_DIR}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

    def _cleanup_old(self):
        free_mb = shutil.disk_usage(RECORDINGS_DIR).free / (1024 * 1024)
        while free_mb < DISK_MIN_FREE_MB:
            files = sorted(glob.glob(os.path.join(RECORDINGS_DIR, "*.mp4")), key=os.path.getmtime)
            if not files:
                break
            os.remove(files[0])
            print(f"[REC] Cleaned: {os.path.basename(files[0])}")
            free_mb = shutil.disk_usage(RECORDINGS_DIR).free / (1024 * 1024)

    def signal_motion(self):
        with self.lock:
            self.last_motion_time = time.time()
            if not self.recording:
                self._start_recording()

    def _start_recording(self):
        self._cleanup_old()
        filename = self._get_filename()
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        self.writer = cv2.VideoWriter(filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
        if not self.writer.isOpened():
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
