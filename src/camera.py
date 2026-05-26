import os
import cv2
import numpy as np
from .config import FRAME_WIDTH, FRAME_HEIGHT

class Camera:
    def __init__(self):
        self.mode = os.environ.get("CAMERA_MODE", "opencv")
        if self.mode == "picamera2":
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            config = self.picam2.create_video_configuration(
                main={"size": (FRAME_WIDTH, FRAME_HEIGHT), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
        else:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, 20)

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
