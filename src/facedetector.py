import cv2
import os


class FaceDetector:
    def __init__(self, scale_factor=1.1, min_neighbors=5, min_size=(60, 60)):
        cascade_file = "haarcascade_frontalface_default.xml"
        paths = [
            os.path.join(os.path.dirname(cv2.__file__), "data", cascade_file),
            "/usr/share/opencv4/haarcascades/" + cascade_file,
            "/usr/local/share/opencv4/haarcascades/" + cascade_file,
        ]
        cascade_path = None
        for p in paths:
            if os.path.exists(p):
                cascade_path = p
                break
        if cascade_path is None:
            raise FileNotFoundError(f"Cascade file {cascade_file} not found")
        self.cascade = cv2.CascadeClassifier(cascade_path)
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
        )
        return faces

    @staticmethod
    def draw(frame, faces, color=(0, 255, 0), thickness=2):
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        return frame
