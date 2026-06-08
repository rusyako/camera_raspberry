#!/usr/bin/env bash
set -u

echo "== Camera service =="
systemctl is-enabled camera.service 2>/dev/null || true
systemctl is-active camera.service 2>/dev/null || true
systemctl --no-pager --full status camera.service 2>/dev/null | sed -n '1,18p' || true

echo
echo "== Port 5000 =="
ss -tlnp 2>/dev/null | grep ':5000' || echo "Port 5000 is not listening"

echo
echo "== Local HTTP =="
curl -fsS -I http://127.0.0.1:5000/ 2>/dev/null | head -5 || echo "HTTP localhost:5000 is not responding"
curl -fsS http://127.0.0.1:5000/api/status 2>/dev/null || echo "API /api/status is not responding"
echo

echo
echo "== USB recordings =="
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS,MODEL
echo
df -h /mnt/usb 2>/dev/null || echo "/mnt/usb is not mounted"
echo
ls -lah /mnt/usb/recordings 2>/dev/null | tail -20 || echo "/mnt/usb/recordings is not available"

echo
echo "== Camera detection =="
rpicam-hello --list-cameras 2>/dev/null || true
cam -l 2>/dev/null || true

echo
echo "== Docker =="
systemctl is-active docker 2>/dev/null || true
docker ps 2>/dev/null || echo "Docker is not available or current user has no permission"

echo
echo "== Last camera logs =="
journalctl -u camera.service --no-pager -n 40 2>/dev/null || true
