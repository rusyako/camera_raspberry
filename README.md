# Camera Surveillance System for Raspberry Pi 4

Live streaming + motion detection + MP4 recording with auto-start.

## Project structure

```
camera_raspberry/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point / orchestrator
│   ├── camera.py            # Picamera2 (Pi) / OpenCV webcam (PC dev)
│   ├── detector.py          # Motion detection (frame differencing)
│   ├── recorder.py          # MP4 recorder with 10s timeout
│   ├── streamer.py          # Flask + MJPEG stream
│   ├── config.py            # Settings
│   └── templates/
│       └── index.html       # Browser live view
├── recordings/              # Saved MP4 files (gitignored)
├── requirements.txt         # Dev/PC dependencies
├── requirements-pi.txt      # Pi dependencies (includes picamera2)
├── Dockerfile               # Docker image for Raspberry Pi 4 (arm64)
├── docker-compose.yml       # Device + volume + port mapping
└── camera.service           # systemd unit for auto-start on boot
```

## Quick start (local dev on PC)

```bash
pip install -r requirements.txt
python -m src.main
```

Opens browser at `http://localhost:5000`

Uses webcam by default (`CAMERA_MODE=opencv`).

## Deploy to Raspberry Pi 4

### 1. Clone and build

```bash
git clone https://github.com/rusyako/camera_raspberry.git && cd camera_raspberry
docker-compose build --build-arg USE_PICAMERA=true
```

### 2. Run

```bash
docker-compose up -d
```

### 3. Open browser

```
http://<RASPBERRY_IP>:5000
```

### 4. Auto-start on boot

```bash
sudo cp camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable camera.service
sudo systemctl start camera.service
```

### 5. Check logs

```bash
docker-compose logs -f
```
