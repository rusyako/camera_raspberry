import cv2
import signal
import time
import shutil
import threading
import numpy as np
from .camera import Camera
from .detector import MotionDetector
from .facedetector import FaceDetector
from .recorder import Recorder
from .streamer import set_frame, set_status, run_server
from .usbwatcher import USBWatcher
from .config import (FLASK_HOST, FLASK_PORT, FRAME_WIDTH, FRAME_HEIGHT,
                     FPS, FPS_ACTIVE, FPS_IDLE, USB_CHECK_INTERVAL,
                     RECORDINGS_DIR, DISK_MIN_FREE_MB, FACE_DETECT_EVERY_N)


def _placeholder_frame():
    frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    frame[:] = (60, 40, 20)
    cv2.putText(frame, "No Camera", (140, 250),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return frame


def main():
    stop_event = threading.Event()

    def request_stop(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    camera = Camera()
    detector = MotionDetector()
    face_detector = FaceDetector()
    recorder = Recorder()
    usb = USBWatcher(mount_point="/mnt/usb", check_interval=USB_CHECK_INTERVAL)
    usb.start()
    camera_ok = True
    current_fps = FPS_IDLE
    frame_counter = 0
    last_faces = []

    server_thread = threading.Thread(
        target=run_server,
        args=(FLASK_HOST, FLASK_PORT),
        daemon=True
    )
    server_thread.start()

    print(f"Server running at http://0.0.0.0:{FLASK_PORT}")
    print(f"[USB] Check every {USB_CHECK_INTERVAL}s")

    try:
        while not stop_event.is_set():
            ret, frame = camera.read()
            if not ret:
                if camera_ok:
                    print("[WARN] Camera not available")
                    camera_ok = False
                frame = _placeholder_frame()
                set_frame(frame)
                usb_ok = usb.is_available()
                try:
                    free_mb = shutil.disk_usage(RECORDINGS_DIR).free // (1024 * 1024)
                except Exception:
                    free_mb = -1
                set_status(
                    recording=recorder.recording,
                    usb_connected=usb_ok,
                    last_motion=0,
                    face_mode=False,
                    free_mb=free_mb,
                    fps=FPS_IDLE,
                    face_count=0,
                )
                time.sleep(1.0 / FPS)
                continue

            if not camera_ok:
                print("[INFO] Camera connected")
                camera_ok = True

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            recorder.feed_buffer(frame)

            usb_ok = usb.is_available()

            if usb_ok:
                motion = detector.detect(frame)
                if motion:
                    recorder.signal_motion()
                    current_fps = FPS_ACTIVE
                    frame_counter += 1
                    if frame_counter % FACE_DETECT_EVERY_N == 0:
                        last_faces = face_detector.detect(frame)
                    face_detector.draw(frame, last_faces)
                    if last_faces:
                        recorder.signal_face()
                elif recorder.recording:
                    pass
                else:
                    current_fps = FPS_IDLE
                    last_faces = []
                recorder.write_frame(frame)
                recorder.check_timeout()
            else:
                current_fps = FPS_IDLE
                if recorder.recording:
                    recorder.abort()

            set_frame(frame)

            try:
                free_mb = shutil.disk_usage(RECORDINGS_DIR).free // (1024 * 1024)
            except Exception:
                free_mb = -1
            set_status(
                recording=recorder.recording,
                usb_connected=usb_ok,
                last_motion=recorder.last_motion_time if recorder.recording else 0,
                face_mode=recorder._face_mode,
                free_mb=free_mb,
                fps=current_fps,
                face_count=len(last_faces),
            )

            time.sleep(1.0 / current_fps)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        try:
            camera.release()
        except Exception:
            pass
        recorder.release()
        usb.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
