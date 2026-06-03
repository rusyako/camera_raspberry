import os
import time
import threading


class USBWatcher:
    def __init__(self, mount_point="/mnt/usb", check_interval=40):
        self.mount_point = mount_point
        self.check_interval = check_interval
        self.available = False
        self.lock = threading.Lock()
        self._stop = False
        self._thread = None

    def _scan_usb(self):
        if os.path.ismount(self.mount_point):
            return True
        try:
            for entry in os.listdir("/dev/disk/by-id"):
                if "usb" in entry.lower():
                    return True
        except Exception:
            pass
        try:
            for entry in os.listdir("/dev/disk/by-path"):
                if "usb" in entry.lower():
                    return True
        except Exception:
            pass
        return False

    def _run(self):
        while not self._stop:
            avail = self._scan_usb()
            with self.lock:
                if avail != self.available:
                    self.available = avail
                    print(f"[USB] {'Connected' if avail else 'Disconnected'}")
            time.sleep(self.check_interval)

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def is_available(self):
        with self.lock:
            return self.available
