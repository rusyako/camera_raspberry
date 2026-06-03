import cv2
import time
import threading
import numpy as np
from .camera import Camera
from .detector import MotionDetector
from .recorder import Recorder
from .streamer import set_frame, run_server
from .usbwatcher import USBWatcher
from .config import FLASK_HOST, FLASK_PORT, FRAME_WIDTH, FRAME_HEIGHT, FPS, USB_CHECK_INTERVAL


def _placeholder_frame():
    frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    frame[:] = (60, 40, 20)
    cv2.putText(frame, "No Camera", (140, 250),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return frame


def main():
    camera = Camera()
    detector = MotionDetector()
    recorder = Recorder()
    usb = USBWatcher(mount_point="/mnt/usb", check_interval=USB_CHECK_INTERVAL)
    usb.start()
    camera_ok = True

    server_thread = threading.Thread(
        target=run_server,
        args=(FLASK_HOST, FLASK_PORT),
        daemon=True
    )
    server_thread.start()

    print(f"Server running at http://0.0.0.0:{FLASK_PORT}")
    print(f"[USB] Check every {USB_CHECK_INTERVAL}s")

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                if camera_ok:
                    print("[WARN] Camera not available")
                    camera_ok = False
                frame = _placeholder_frame()
                set_frame(frame)
                time.sleep(1.0 / FPS)
                continue

            if not camera_ok:
                print("[INFO] Camera connected")
                camera_ok = True

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            if usb.is_available():
                motion = detector.detect(frame)
                if motion:
                    recorder.signal_motion()
                recorder.write_frame(frame)
                recorder.check_timeout()
            else:
                if recorder.recording:
                    recorder.abort()
                    print("[USB] Recording stopped — device removed")

            set_frame(frame)

            time.sleep(1.0 / FPS)
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
