import socket
import subprocess
import re
import platform
import concurrent.futures
from typing import List, Tuple, Optional, Dict, Any

# [AI-BLOCK: LAN Camera IP & Port Auto-Discovery Scanner with Mode-Aware Network Detection]
COMMON_TETHER_IPS = [
    "192.168.42.129", # Android standard default USB tethering gateway
    "192.168.42.1",
    "192.168.43.1",
    "192.168.44.1",
    "192.168.49.1"
]

VIRTUAL_ADAPTER_KEYWORDS = [
    "virtual", "hyper-v", "vethernet", "wsl", "docker", "vbox", "vmnet",
    "vmware", "loopback", "pseudo", "teredo", "isatap", "tap", "tun",
    "wireguard", "tailscale", "zerotier", "nord", "expressvpn", "surfshark",
    "proton", "cisco", "anyconnect", "fortinet", "pulse", "bluetooth",
    "wi-fi direct virtual"
]

TETHER_KEYWORDS = [
    "rndis", "remote ndis", "usb ethernet", "cdc ncm", "cdc_ncm", "ncm",
    "apple mobile device ethernet"
]

TETHER_SUBNETS = [
    "192.168.42.", "192.168.43.", "192.168.44.", "192.168.49.", "192.168.50."
]

def is_virtual_or_vpn(name: str, desc: str, ip: str) -> bool:
    """Check if an adapter is virtual, VPN, container, loopback or APIPA."""
    combined = (name + " " + desc).lower()
    for kw in VIRTUAL_ADAPTER_KEYWORDS:
        if kw in combined:
            return True
    if ip.startswith("127.") or ip.startswith("169.254."):
        return True
    # Tailscale CGNAT range (100.64.0.0/10)
    if ip.startswith("100."):
        parts = ip.split(".")
        if len(parts) > 1 and 64 <= int(parts[1]) <= 127:
            return True
    return False

def is_tether_adapter(name: str, desc: str, ip: str, gateways: List[str]) -> bool:
    """Check if an adapter belongs to an active USB tethering connection."""
    combined = (name + " " + desc).lower()
    for kw in TETHER_KEYWORDS:
        if kw in combined:
            return True
    for sub in TETHER_SUBNETS:
        if ip.startswith(sub):
            return True
        for gw in gateways:
            if gw.startswith(sub):
                return True
    return False

def get_network_adapters() -> List[Dict[str, Any]]:
    """Enumerate all active network adapters cross-platform without external dependencies."""
    adapters = []
    sys_plat = platform.system()

    if sys_plat == "Windows":
        try:
            out = subprocess.check_output("ipconfig /all", text=True, errors="ignore")
            current = None
            for raw_line in out.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                if ("adapter" in line.lower() or "configuration" in line.lower()) and line.endswith(":"):
                    if current and current.get("ips") and not current.get("disconnected"):
                        adapters.append(current)
                    current = {
                        "name": line[:-1],
                        "desc": "",
                        "disconnected": False,
                        "ips": [],
                        "gateways": []
                    }
                    continue
                if not current:
                    continue
                if "Media State" in line and "Media disconnected" in line:
                    current["disconnected"] = True
                elif "Description" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current["desc"] = parts[1].strip()
                elif "IPv4 Address" in line or "IP Address" in line:
                    m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                    if m:
                        current["ips"].append(m.group(1))
                elif "Default Gateway" in line:
                    m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                    if m:
                        current["gateways"].append(m.group(1))

            if current and current.get("ips") and not current.get("disconnected"):
                adapters.append(current)
        except Exception:
            pass
    elif sys_plat == "Linux":
        try:
            out = subprocess.check_output(["ip", "-4", "-o", "addr", "show"], text=True, errors="ignore")
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    iface = parts[1]
                    cidr = parts[3]
                    ip = cidr.split("/")[0]
                    if not ip.startswith("127."):
                        adapters.append({
                            "name": iface,
                            "desc": iface,
                            "disconnected": False,
                            "ips": [ip],
                            "gateways": []
                        })
        except Exception:
            pass
    elif sys_plat == "Darwin":
        try:
            out = subprocess.check_output(["ifconfig"], text=True, errors="ignore")
            current = None
            for line in out.splitlines():
                if line and not line[0].isspace() and ":" in line:
                    if current and current.get("ips"):
                        adapters.append(current)
                    iface = line.split(":")[0]
                    current = {"name": iface, "desc": iface, "disconnected": False, "ips": [], "gateways": []}
                elif current and "inet " in line:
                    parts = line.strip().split()
                    idx = parts.index("inet")
                    if idx + 1 < len(parts):
                        ip = parts[idx + 1]
                        if not ip.startswith("127."):
                            current["ips"].append(ip)
            if current and current.get("ips"):
                adapters.append(current)
        except Exception:
            pass

    # Generic fallback using socket
    if not adapters:
        try:
            host = socket.gethostname()
            for ip in socket.gethostbyname_ex(host)[2]:
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    adapters.append({
                        "name": "Default Interface",
                        "desc": "Default Interface",
                        "disconnected": False,
                        "ips": [ip],
                        "gateways": []
                    })
        except Exception:
            pass

    # Tag each adapter
    for a in adapters:
        ip = a["ips"][0] if a.get("ips") else ""
        a["is_tether"] = is_tether_adapter(a["name"], a.get("desc", ""), ip, a.get("gateways", []))
        a["is_virtual"] = is_virtual_or_vpn(a["name"], a.get("desc", ""), ip)

    return adapters

def detect_tethering_adapter() -> Optional[Dict[str, Any]]:
    """Detect active USB Tethering adapter on the host PC."""
    adapters = get_network_adapters()
    for a in adapters:
        if a.get("is_tether") and a.get("ips"):
            return a
    return None

def detect_lan_adapters() -> List[Dict[str, Any]]:
    """Detect all active physical LAN / Wi-Fi network adapters excluding virtual & VPN."""
    adapters = get_network_adapters()
    lan = []
    for a in adapters:
        if not a.get("is_virtual") and not a.get("is_tether") and a.get("ips"):
            lan.append(a)
    return lan

def get_local_ip_subnets() -> List[str]:
    """Retrieve /24 subnets from active physical LAN adapters."""
    subnets = []
    lan_adapters = detect_lan_adapters()
    for a in lan_adapters:
        for ip in a.get("ips", []):
            parts = ip.split(".")
            if len(parts) == 4:
                subnets.append(".".join(parts[:3]))
    if not subnets:
        # Fallback to general socket discovery
        try:
            hostname = socket.gethostname()
            for ip in socket.gethostbyname_ex(hostname)[2]:
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    parts = ip.split(".")
                    if len(parts) == 4:
                        subnets.append(".".join(parts[:3]))
        except Exception:
            pass
    if not subnets:
        subnets.append("192.168.1")
    return list(dict.fromkeys(subnets))

# [AI-BLOCK: Reserved System / OS Port Blacklist]
# Exclude known privileged, core system, and high-conflict service ports even when currently unbound.
SYSTEM_RESERVED_PORTS = {
    # Well-known / privileged (1 - 1024)
    *range(1, 1024),
    # Common database / infrastructure ports
    1433, 1434, 1521, 2049, 2375, 2376, 3000, 3306, 4000, 5000, 5432, 5900, 6379, 8000, 8443, 9000, 9200, 11211,
    # Windows RPC, Apple, & Linux system / MDNS daemons
    135, 137, 138, 139, 445, 500, 4500, 5353, 5355,
}

def is_system_reserved_port(port: int) -> bool:
    """Check if port is within privileged range or matches well-known OS / system services."""
    if port < 1024 or port in SYSTEM_RESERVED_PORTS:
        return True
    return False

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a specific port is already in use by a listening socket on the host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.15)
        return s.connect_ex((host, port)) == 0

def find_available_port(start_port: int = 8089, host: str = "127.0.0.1", max_port: int = 65535, exclude: List[int] = None) -> int:
    """Find the next available bindable port starting from start_port, skipping OS/system-reserved ports."""
    port = max(1025, start_port)
    exclude = set(exclude or [])
    while port <= max_port:
        if port not in exclude and not is_system_reserved_port(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((host, port))
                    return port
                except OSError:
                    pass
        port += 1
    return start_port

def check_camera_host(ip: str, port: int, timeout: float = 0.3) -> Tuple[bool, str, int]:
    """Prioritise probing control port (8090) first to protect active video stream socket."""
    probe_port = (port + 1) if port == 8089 else port
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, probe_port)) == 0:
                return (True, ip, port)
    except Exception:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                return (True, ip, port)
    except Exception:
        pass
    return (False, ip, port)

def scan_network_for_cameras(port: int = 8089, subnets: List[str] = None, max_workers: int = 60, timeout: float = 0.35) -> List[str]:
    """Scan local network subnets for responsive Otter camera servers."""
    detected = []

    # Check USB Tethering default addresses first with fast timeout
    for tether_ip in COMMON_TETHER_IPS:
        alive, ip, _ = check_camera_host(tether_ip, port, timeout=0.2)
        if alive and ip not in detected:
            detected.append(ip)

    if subnets is None:
        subnets = get_local_ip_subnets()

    targets = []
    for subnet in subnets:
        for i in range(1, 255):
            target_ip = f"{subnet}.{i}"
            if target_ip not in detected and target_ip not in COMMON_TETHER_IPS:
                targets.append(target_ip)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_camera_host, ip, port, timeout): ip for ip in targets}
        for future in concurrent.futures.as_completed(futures):
            try:
                alive, ip, _ = future.result()
                if alive:
                    detected.append(ip)
            except Exception:
                pass

    return sorted(detected)
