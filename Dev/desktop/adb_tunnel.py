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

    def usb_serial(self):
        """Return first phone in 'device' state (USB debugging authorised), else None."""
        devices = self.list_devices()
        return devices[0] if devices else None

    def _adb_prefix(self, serial=None):
        return [self.adb_bin] + (["-s", serial] if serial else [])

    def clear_forward(self, serial=None):
        """Remove old forwards first. Stale forwards cause 'port in use' errors."""
        if not self.is_available():
            return
        for port in (self.stream_port, self.control_port):
            subprocess.run(
                self._adb_prefix(serial) + ["forward", "--remove", f"tcp:{port}"],
                capture_output=True,
                text=True
            )

    def get_forward_list(self) -> list:
        """List active ADB forward rules."""
        if not self.is_available():
            return []
        try:
            r = subprocess.run([self.adb_bin, "forward", "--list"], capture_output=True, text=True, timeout=5)
            return r.stdout.strip().splitlines()
        except Exception:
            return []

    def resolve_forward_ports(self, serial=None):
        """Resolve available local ports on 127.0.0.1. If occupied by non-ADB process, allocate dynamic ports."""
        import network_discovery
        fwd_list = "\n".join(self.get_forward_list())
        
        # Check stream port
        sp = self.stream_port
        if f"tcp:{sp}" not in fwd_list and network_discovery.is_port_in_use(sp, "127.0.0.1"):
            sp = network_discovery.find_available_port(sp + 1, "127.0.0.1")

        # Check control port
        cp = self.control_port
        if f"tcp:{cp}" not in fwd_list and network_discovery.is_port_in_use(cp, "127.0.0.1"):
            cp = network_discovery.find_available_port(max(cp + 1, sp + 1), "127.0.0.1", exclude=[sp])

        return sp, cp

    def setup_forward(self, serial=None, local_stream_port: int = None, local_control_port: int = None) -> bool:
        if not self.is_available():
            return False
        lsp = local_stream_port or self.stream_port
        lcp = local_control_port or self.control_port
        try:
            self.clear_forward(serial)
            for local_p, remote_p in ((lsp, self.stream_port), (lcp, self.control_port)):
                r = subprocess.run(
                    self._adb_prefix(serial) + ["forward", f"tcp:{local_p}", f"tcp:{remote_p}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if r.returncode != 0:
                    print(f"ADB forward failed on port {local_p}->{remote_p}: {(r.stderr or r.stdout).strip()}")
                    return False
            return True
        except Exception as e:
            print(f"ADB forward error: {e}")
            return False

    def remove_forward(self, serial=None) -> None:
        self.clear_forward(serial)
