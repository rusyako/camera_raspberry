import os
import cv2
from .config import FRAME_WIDTH, FRAME_HEIGHT


class Camera:
    def __init__(self):
        env_mode = os.environ.get("CAMERA_MODE", "")
        self.mode = "opencv"

        if env_mode == "picamera2" or env_mode == "":
            try:
                from picamera2 import Picamera2
                self.picam2 = Picamera2()
                config = self.picam2.create_video_configuration(
                    main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "RGB888"}
                )
                self.picam2.configure(config)
                self.picam2.start()
                self.mode = "picamera2"
                print("[CAM] picamera2 mode")
                return
            except Exception:
                if env_mode == "picamera2":
                    print("[WARN] picamera2 failed, fallback to opencv")

        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        print("[CAM] opencv mode")

    def read(self):
        if self.mode == "picamera2":
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return True, frame
        else:
            return self.cap.read()

    def release(self):
        if self.mode == "picamera2":
            self.picam2.stop()
        else:
            self.cap.release()
