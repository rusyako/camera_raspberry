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
            except Exception as e:
                if env_mode == "picamera2":
                    print(f"[WARN] picamera2 failed: {e}")

        for dev in ("/dev/video0", "/dev/video1", 0):
            self.cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            if self.cap.isOpened():
                w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                print(f"[CAM] opencv mode ({dev} {int(w)}x{int(h)})")
                return

        print("[WARN] no camera device found")

    def read(self):
        if self.mode == "picamera2":
            try:
                frame = self.picam2.capture_array()
                return True, frame
            except Exception as e:
                print(f"[WARN] picamera2 read failed: {e}")
                return False, None
        else:
            return self.cap.read()

    def release(self):
        if self.mode == "picamera2":
            try:
                self.picam2.stop()
            except Exception:
                pass
            try:
                self.picam2.close()
            except Exception:
                pass
        else:
            self.cap.release()
