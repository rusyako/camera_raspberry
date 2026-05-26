import cv2
from .config import MOTION_THRESHOLD

class MotionDetector:
    def __init__(self):
        self.prev_frame = None

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame is None:
            self.prev_frame = gray
            return False

        diff = cv2.absdiff(self.prev_frame, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.prev_frame = gray

        for c in contours:
            if cv2.contourArea(c) > MOTION_THRESHOLD:
                return True
        return False
