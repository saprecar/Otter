import os
import sys
import subprocess
import shutil

# [AI-BLOCK: Linux v4l2loopback Virtual Camera Driver Manager & Streamer]

def find_available_v4l2_device() -> str:
    """Finds an existing /dev/video* node created by v4l2loopback"""
    if not sys.platform.startswith("linux"):
        return None
    for i in range(10, 30):
        dev = f"/dev/video{i}"
        if os.path.exists(dev):
            return dev
    for i in range(0, 10):
        dev = f"/dev/video{i}"
        if os.path.exists(dev):
            return dev
    return None

class LinuxV4L2Bridge:
    def __init__(self, device: str = None, width: int = 1280, height: int = 720, fps: int = 30):
        self.device = device or find_available_v4l2_device() or "/dev/video10"
        self.width = width
        self.height = height
        self.fps = fps
        self.process = None

    def connect(self) -> bool:
        if not sys.platform.startswith("linux"):
            return False
        if not os.path.exists(self.device):
            print(f"[Notice] Linux v4l2 device {self.device} not found. Run 'sudo modprobe v4l2loopback video_nr=10 card_label=\"Otter Camera\" exclusive_caps=1'")
            return False

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            print("[Notice] ffmpeg not found. Install via 'sudo apt install ffmpeg'.")
            return False

        cmd = [
            ffmpeg_bin,
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", f"{self.width}x{self.height}",
            "-r", str(self.fps),
            "-i", "-",
            "-f", "v4l2",
            "-pix_fmt", "yuyv422",
            self.device
        ]
        try:
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"[Error] Failed to spawn v4l2 ffmpeg pipe: {e}")
            return False

    def send_frame(self, frame_bgr) -> bool:
        if not self.process or self.process.poll() is not None:
            if not self.connect():
                return False
        try:
            self.process.stdin.write(frame_bgr.tobytes())
            self.process.stdin.flush()
            return True
        except Exception:
            return False

    def close(self):
        if self.process:
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except Exception:
                pass
            self.process = None
