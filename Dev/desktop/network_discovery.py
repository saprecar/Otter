import socket
import concurrent.futures
from typing import List, Tuple

# [AI-BLOCK: LAN Camera IP & Port Auto-Discovery Scanner]
def get_local_ip_subnets() -> List[str]:
    subnets = []
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

def check_camera_host(ip: str, port: int, timeout: float = 0.3) -> Tuple[bool, str, int]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                return (True, ip, port)
    except Exception:
        pass
    return (False, ip, port)

def scan_network_for_cameras(port: int = 8089, max_workers: int = 60, timeout: float = 0.35) -> List[str]:
    detected = []
    subnets = get_local_ip_subnets()

    targets = []
    for subnet in subnets:
        for i in range(1, 255):
            targets.append(f"{subnet}.{i}")

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
