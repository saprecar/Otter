import subprocess
import shutil
import os
import sys
import time

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

# [AI-BLOCK: ADB Automated Port Tunneling without Root]
class ADBTunnel:
    def __init__(self, stream_port=8089, control_port=8090):
        self.stream_port = stream_port
        self.control_port = control_port
        self.adb_bin = self._find_adb()

    def _find_adb(self):
        # 1. Check portable downloaded ADB from manage_adb
        try:
            from manage_adb import get_portable_adb_path
            portable = get_portable_adb_path()
            if portable:
                return portable
        except Exception:
            pass

        # 2. Check system PATH
        which_adb = shutil.which("adb")
        if which_adb:
            return which_adb
        # Common platform-tools locations on Windows & macOS/Linux
        sdk_candidates = [
            os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
            r"C:\Android\Sdk\platform-tools\adb.exe",
            r"C:\Program Files (x86)\Android\android-sdk\platform-tools\adb.exe",
            os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
            os.path.expanduser("~/Android/Sdk/platform-tools/adb")
        ]
        for path in sdk_candidates:
            if os.path.exists(path):
                return path
        return None

    def is_available(self) -> bool:
        return self.adb_bin is not None

    def list_devices(self) -> list:
        if not self.is_available():
            return []
        try:
            res = subprocess.run([self.adb_bin, "devices"], capture_output=True, text=True, check=True)
            lines = res.stdout.strip().splitlines()[1:]
            devices = [line.split()[0] for line in lines if "\tdevice" in line]
            return devices
        except Exception:
            return []

    def setup_forward(self, serial=None) -> bool:
        if not self.is_available():
            return False
        cmd_prefix = [self.adb_bin]
        if serial:
            cmd_prefix.extend(["-s", serial])

        try:
            # Forward video stream
            subprocess.run(
                cmd_prefix + ["forward", f"tcp:{self.stream_port}", f"tcp:{self.stream_port}"],
                check=True,
                capture_output=True
            )
            # Forward control commands
            subprocess.run(
                cmd_prefix + ["forward", f"tcp:{self.control_port}", f"tcp:{self.control_port}"],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_forward(self) -> None:
        if not self.is_available():
            return
        try:
            subprocess.run([self.adb_bin, "forward", "--remove", f"tcp:{self.stream_port}"], capture_output=True)
            subprocess.run([self.adb_bin, "forward", "--remove", f"tcp:{self.control_port}"], capture_output=True)
        except Exception:
            pass
