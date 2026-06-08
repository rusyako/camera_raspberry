#!/usr/bin/env bash
set -euo pipefail

MOUNT_POINT="/mnt/usb"
USB_LABEL="CAMERA_USB"
APP_USER="admin"
APP_GROUP="admin"
APP_UID="$(id -u "$APP_USER")"
APP_GID="$(id -g "$APP_USER")"

mkdir -p "$MOUNT_POINT"

if ! findmnt -rno TARGET "$MOUNT_POINT" >/dev/null 2>&1; then
    mount -L "$USB_LABEL" "$MOUNT_POINT" -o uid="$APP_UID",gid="$APP_GID",umask=000
fi

mkdir -p "$MOUNT_POINT/recordings"
chown "$APP_USER:$APP_GROUP" "$MOUNT_POINT" "$MOUNT_POINT/recordings"

systemctl restart camera.service
