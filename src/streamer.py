import os
import cv2
import threading
from flask import Flask, Response, render_template

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

current_frame = None
lock = threading.Lock()


def set_frame(frame):
    global current_frame
    with lock:
        current_frame = frame.copy()


def generate_frames():
    global current_frame
    while True:
        with lock:
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


def run_server(host, port):
    app.run(host=host, port=port, threaded=True, debug=False)
