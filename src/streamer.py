import os
import cv2
import time
import json
import threading
from flask import Flask, Response, render_template, jsonify

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

current_frame = None
frame_lock = threading.Lock()

_status = {
    "recording": False,
    "usb_connected": False,
    "last_motion": 0,
    "free_mb": 0,
    "fps": 20,
}
status_lock = threading.Lock()


def set_frame(frame):
    global current_frame
    with frame_lock:
        current_frame = frame.copy()


def set_status(**kwargs):
    with status_lock:
        _status.update(kwargs)


def generate_frames():
    global current_frame
    while True:
        with frame_lock:
            if current_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', current_frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/api/status')
def api_status():
    with status_lock:
        s = dict(_status)
    s["last_motion_ago"] = int(time.time() - s["last_motion"]) if s["last_motion"] else -1
    return jsonify(s)


def run_server(host, port):
    app.run(host=host, port=port, threaded=True, debug=False)
