import cv2
import os
import time
import glob
import shutil
import threading
from collections import deque
from datetime import datetime, timedelta
from .config import RECORDINGS_DIR, MOTION_TIMEOUT, FRAME_WIDTH, FRAME_HEIGHT, FPS, DISK_MIN_FREE_MB, RECORD_MAX_DAYS, PREBUFFER_SECS


class Recorder:
    def __init__(self):
        self.writer = None
        self.recording = False
        self.last_motion_time = 0
        self.lock = threading.Lock()
        self._base_ts = ""
        self._segment = 0
        self._frame_in_segment = 0
        self.SEGMENT_FRAMES = FPS * 30
        self.prebuffer = deque(maxlen=FPS * PREBUFFER_SECS)

    def _get_filename(self, seg):
        return f"{RECORDINGS_DIR}/{self._base_ts}_{seg:03d}.mp4"

    def _cleanup_old(self):
        self._cleanup_by_age()
        self._cleanup_by_space()

    def _cleanup_by_age(self):
        cutoff = time.time() - RECORD_MAX_DAYS * 86400
        files = sorted(glob.glob(os.path.join(RECORDINGS_DIR, "*.mp4")), key=os.path.getmtime)
        for f in files:
            if os.path.getmtime(f) < cutoff:
                os.remove(f)
                print(f"[REC] Expired: {os.path.basename(f)}")

    def _cleanup_by_space(self):
        free_mb = shutil.disk_usage(RECORDINGS_DIR).free / (1024 * 1024)
        while free_mb < DISK_MIN_FREE_MB:
            files = sorted(glob.glob(os.path.join(RECORDINGS_DIR, "*.mp4")), key=os.path.getmtime)
            if not files:
                break
            os.remove(files[0])
            print(f"[REC] Cleaned: {os.path.basename(files[0])}")
            free_mb = shutil.disk_usage(RECORDINGS_DIR).free / (1024 * 1024)

    def feed_buffer(self, frame):
        with self.lock:
            self.prebuffer.append(frame.copy())

    def signal_motion(self):
        with self.lock:
            self.last_motion_time = time.time()
            if not self.recording:
                self._start_recording()

    def _start_recording(self):
        self._cleanup_old()
        self._base_ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self._segment = 1
        self._frame_in_segment = 0
        self._open_writer()
        buf_count = len(self.prebuffer)
        for f in self.prebuffer:
            self.writer.write(f)
        self.prebuffer.clear()
        print(f"[REC] Pre-buffer flushed {buf_count} frames")

    def _open_writer(self):
        filename = self._get_filename(self._segment)
        for codec in ('H264', 'avc1', 'mp4v'):
            fourcc = cv2.VideoWriter_fourcc(*codec)
            self.writer = cv2.VideoWriter(filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
            if self.writer.isOpened():
                break
        self.recording = True
        print(f"[REC] Started: {filename}")

    def write_frame(self, frame):
        with self.lock:
            if self.recording and self.writer:
                self.writer.write(frame)
                self._frame_in_segment += 1
                if self._frame_in_segment >= self.SEGMENT_FRAMES:
                    self._close_writer()
                    self._segment += 1
                    self._frame_in_segment = 0
                    self._open_writer()

    def check_timeout(self):
        with self.lock:
            if self.recording and (time.time() - self.last_motion_time) > MOTION_TIMEOUT:
                self._stop_recording()

    def _close_writer(self):
        if self.writer:
            self.writer.release()
            self.writer = None
            os.sync()

    def _stop_recording(self):
        self._close_writer()
        self.recording = False
        print("[REC] Stopped")

    def abort(self):
        with self.lock:
            self._stop_recording()

    def release(self):
        self._stop_recording()
