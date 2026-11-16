#!/usr/bin/env bash
# [AI-BLOCK: Linux v4l2loopback Virtual Camera Installer]

echo "==================================================="
echo "  Otter - Linux Virtual Camera Setup (v4l2loopback)"
echo "==================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "[NOTICE] Requesting sudo permissions to load v4l2loopback..."
    exec sudo bash "$0" "$@"
fi

# 1. Install packages if missing
if command -v apt &>/dev/null; then
    echo "Installing v4l2loopback-dkms and ffmpeg on Debian/Ubuntu..."
    apt update -y && apt install -y v4l2loopback-dkms v4l2loopback-utils ffmpeg
elif command -v dnf &>/dev/null; then
    echo "Installing v4l2loopback and ffmpeg on Fedora..."
    dnf install -y v4l2loopback ffmpeg
elif command -v pacman &>/dev/null; then
    echo "Installing v4l2loopback and ffmpeg on Arch Linux..."
    pacman -S --noconfirm v4l2loopback-dkms ffmpeg
fi

# 2. Load module with device number 10 and card label "Otter Camera"
echo "Loading v4l2loopback kernel module..."
modprobe -r v4l2loopback 2>/dev/null
modprobe v4l2loopback video_nr=10 card_label="Otter Camera" exclusive_caps=1

if [ -e "/dev/video10" ]; then
    echo ""
    echo "[SUCCESS] Virtual Camera created at /dev/video10 ('Otter Camera')!"
    echo "Zoom, Google Meet, Teams, Discord, and Chrome will now detect 'Otter Camera' natively!"
else
    echo "[WARNING] /dev/video10 was not created. Please verify your kernel headers."
fi
echo ""
read -p "Press Enter to exit..."
