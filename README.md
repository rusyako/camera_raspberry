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
│   ├── recorder.py          # MP4 recorder with 10s timeout, H.264, auto-cleanup
│   ├── streamer.py          # Flask + MJPEG stream
│   ├── config.py            # Settings
│   └── templates/
│       └── index.html       # Browser live view
├── recordings/              # Saved MP4 files (gitignored)
├── requirements.txt         # Dev/PC dependencies
├── requirements-pi.txt      # Pi dependencies (includes picamera2)
├── Dockerfile               # Multi-stage (pi + dev)
├── docker-compose.yml       # Device + volume + port mapping
└── camera.service           # systemd unit for auto-start (bare-metal)
```

## Quick start (local dev on PC)

```bash
pip install -r requirements.txt
python -m src.main
```

Opens browser at `http://localhost:5000`

Uses webcam by default (OpenCV).

---

# Raspberry Pi — bare-metal (рекомендуется)

## 1. Установка Raspberry Pi OS

Рекомендуется **Raspberry Pi OS Lite (64-bit) Bookworm** через Raspberry Pi Imager.

Перед записью образа в Imager нажми `Ctrl+Shift+X` и настрой:
- Hostname: `ubuntu-pi-server` (или любой)
- SSH: включить
- Username: `backupadmin`
- Пароль: твой пароль
- Wi-Fi: если нужно

## 2. Первый вход по SSH

```bash
ssh backupadmin@192.168.22.84
```

## 3. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

## 4. Включение камеры

```bash
sudo raspi-config
# → Interface Options → Camera → Enable → Finish
# Если пункта Camera нет — выйди и сделай вручную:
echo "dtoverlay=imx219" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

## 5. Клонирование проекта

```bash
git clone https://github.com/rusyako/camera_raspberry.git && cd camera_raspberry
```

## 6. Установка зависимостей

```bash
# Системные библиотеки (OpenCV + камера)
sudo apt install -y python3-pip python3-opencv python3-picamera2 libgl1-mesa-glx

# Проверка picamera2
python3 -c "from picamera2 import Picamera2; print('OK')"
# Если ошибка — установить:
sudo apt install -y python3-picamera2
```

## 7. Настройка USB-флешки для записей

```bash
# Отформатировать флешку в exFAT (если не форматирована)
sudo apt install -y exfat-fuse exfatprogs
sudo mkfs.exfat -n CAMERA_USB /dev/sda1

# Смонтировать
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
sudo chown -R backupadmin:backupadmin /mnt/usb
mkdir -p /mnt/usb/recordings

# Автомонтирование при загрузке
echo "UUID=$(sudo blkid -s UUID -o value /dev/sda1) /mnt/usb exfat defaults,uid=1000,gid=1000,umask=000,nofail 0 2" | sudo tee -a /etc/fstab

# Симлинк на папку записей
rm -rf ~/camera_raspberry/recordings
ln -s /mnt/usb/recordings ~/camera_raspberry/recordings
```

## 8. Запуск вручную

```bash
cd ~/camera_raspberry && python3 -m src.main
```

Открыть: `http://192.168.22.84:5000`

## 9. Автозапуск (systemd)

```bash
# Отредактировать camera.service под твой username
# Вместо backupadmin — твой юзер
sudo nano ~/camera_raspberry/camera.service
# Поменять User= на твоего и WorkingDirectory= на твой путь

# Установить сервис
sudo cp ~/camera_raspberry/camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now camera.service

# Проверить статус
sudo systemctl status camera.service

# Смотреть логи
journalctl -u camera.service -f
```

## 9.1. Автоподключение USB и restart сервиса

Если флешка вставляется уже после запуска камеры, можно поставить udev hook. Он реагирует на флешку с label `CAMERA_USB`, монтирует её в `/mnt/usb`, создаёт `/mnt/usb/recordings` и перезапускает `camera.service`.

```bash
cd ~/camera_raspberry
chmod +x scripts/camera_usb_plug.sh
sudo cp camera-usb-plug.service /etc/systemd/system/
sudo cp 99-camera-usb.rules /etc/udev/rules.d/
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Проверка:

```bash
sudo systemctl status camera-usb-plug.service
journalctl -u camera-usb-plug.service --no-pager -n 30
curl http://127.0.0.1:5000/api/status
```

## 10. Проверка после перезагрузки

```bash
sudo reboot
# Подождать 30 секунд, подключиться
ssh backupadmin@192.168.22.84
sudo systemctl status camera.service
# Должен быть active (running)
```

---

# Raspberry Pi — Docker

## 1. Установка Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker backupadmin
exit
# Перезайти по SSH
docker --version
```

## 2. Клонирование и сборка

```bash
git clone https://github.com/rusyako/camera_raspberry.git && cd camera_raspberry
docker-compose build
```

## 3. Запуск

```bash
docker-compose up -d
docker-compose logs -f
```

## 4. Автозапуск Docker-контейнера

```bash
sudo cp camera.service.docker /etc/systemd/system/
sudo systemctl enable --now camera.service
```

---

# Логика работы

**Детекция движения:**
```
движение → старт записи  
движение есть → продолжаем писать  
движение пропало → ждём 10 сек  
нет движения → стоп запись  
```

**Автоочистка:**
```
свободно < 500 МБ на флешке → удаляем самую старую запись → старт новой
```

---

# Команды

| Действие | Команда |
|---|---|
| Запустить вручную | `python3 -m src.main` |
| Статус сервиса | `sudo systemctl status camera.service` |
| Логи (live) | `journalctl -u camera.service -f` |
| Логи (все) | `journalctl -u camera.service --no-pager` |
| Перезапустить сервис | `sudo systemctl restart camera.service` |
| Остановить сервис | `sudo systemctl stop camera.service` |
| Просмотр записей | `ls -la ~/camera_raspberry/recordings/` |
