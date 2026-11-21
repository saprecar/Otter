import http.server
import socketserver
import json
import os
import sys
import threading
import time
import shutil
import subprocess
import socket
from typing import Optional

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from adb_tunnel import ADBTunnel
    from cambridge_control import CamBridgeControl
    from cambridge_receiver import CamBridgeReceiver
    import network_discovery
except ImportError:
    from Dev.desktop.adb_tunnel import ADBTunnel
    from Dev.desktop.cambridge_control import CamBridgeControl
    from Dev.desktop.cambridge_receiver import CamBridgeReceiver
    import Dev.desktop.network_discovery as network_discovery

# [AI-BLOCK: Cross-Platform Universal Web UI Controller Server & Stream Bridge]
class OtterWebController:
    """
    HTTP & MJPEG Controller Server for Otter Desktop.
    Replaces Tkinter with a zero-driver web dashboard and bridges mobile Safari / Chrome (REQ-023).
    """
    def __init__(self, port: int = 8080):
        # Auto-resolve free port, skipping OS/system-reserved ports
        self.port = network_discovery.find_available_port(start_port=port, host="0.0.0.0")
        self.receiver = None
        self.receiver_thread = None
        self.adb_tunnel = None
        self.controller = None
        self.is_connected = False
        self.active_mode = "auto"
        self.active_ip = "127.0.0.1"
        self.stream_port = 8089
        self.ctrl_port = 8090
        
        self.latest_frame = None
        self.latest_frame_lock = threading.Lock()
        self.web_streamer_active = False
        self.last_web_frame_time = 0
        
        # Virtual camera initial bridge
        self.vcam_initialized = False

    def get_lan_ip(self) -> str:
        """Get best reachable LAN IP for mobile browser QR/link."""
        try:
            lan = network_discovery.detect_lan_adapters()
            if lan and lan[0].get("ips"):
                return lan[0]["ips"][0]
        except Exception:
            pass
        return "127.0.0.1"

    def update_frame(self, frame):
        """Callback from CamBridgeReceiver or Web Streamer with newest BGR frame."""
        if frame is None:
            return
        with self.latest_frame_lock:
            self.latest_frame = frame

    def push_web_streamer_frame(self, jpeg_bytes: bytes):
        """Decode JPEG from mobile Safari/Chrome and push to Virtual Webcam and MJPEG monitor."""
        if not CV2_AVAILABLE:
            return
        nparr = np.frombuffer(jpeg_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            self.web_streamer_active = True
            self.last_web_frame_time = time.time()
            self.update_frame(img)
            
            # Ensure virtual camera is active and dispatch to it
            if self.receiver:
                self.receiver.push_external_frame(img)
            else:
                self._ensure_virtualcam()
                if self.receiver:
                    self.receiver.push_external_frame(img)

    def _ensure_virtualcam(self):
        if not self.receiver:
            self.receiver = CamBridgeReceiver(
                host=self.active_ip,
                stream_port=self.stream_port,
                control_port=self.ctrl_port,
                camera_name="Otter Camera"
            )
            self.receiver.on_frame_cb = self.update_frame
            self.receiver.start_virtualcam_only()
            self.vcam_initialized = True

    def start_stream(self, ip: str, stream_p: int, ctrl_p: int, mode: str = "auto") -> dict:
        self.active_mode = mode
        self.stream_port = stream_p
        self.ctrl_port = ctrl_p
        reforward_cb = None
        target_ip = ip

        if mode == "auto":
            self.adb_tunnel = ADBTunnel(stream_port=stream_p, control_port=ctrl_p)
            serial = self.adb_tunnel.usb_serial() if self.adb_tunnel.is_available() else None
            if serial:
                lp_s, lp_c = self.adb_tunnel.resolve_forward_ports(serial)
                if self.adb_tunnel.setup_forward(serial, lp_s, lp_c):
                    target_ip = "127.0.0.1"
                    stream_p, ctrl_p = lp_s, lp_c
                    reforward_cb = lambda: self.adb_tunnel.setup_forward(serial, lp_s, lp_c)
            else:
                tether = network_discovery.detect_tethering_adapter()
                if tether and tether.get("gateways"):
                    target_ip = tether["gateways"][0]
                elif tether and tether.get("ips"):
                    sub = ".".join(tether["ips"][0].split(".")[:3])
                    target_ip = f"{sub}.1"
        elif mode == "usb":
            self.adb_tunnel = ADBTunnel(stream_port=stream_p, control_port=ctrl_p)
            serial = self.adb_tunnel.usb_serial() if self.adb_tunnel.is_available() else None
            lp_s, lp_c = self.adb_tunnel.resolve_forward_ports(serial)
            if self.adb_tunnel.setup_forward(serial, lp_s, lp_c):
                target_ip = "127.0.0.1"
                stream_p, ctrl_p = lp_s, lp_c
                reforward_cb = lambda: self.adb_tunnel.setup_forward(serial, lp_s, lp_c)
        elif mode == "tether":
            tether = network_discovery.detect_tethering_adapter()
            if tether and tether.get("gateways"):
                target_ip = tether["gateways"][0]

        self.active_ip = target_ip
        self.receiver = CamBridgeReceiver(
            host=target_ip,
            stream_port=stream_p,
            control_port=ctrl_p,
            camera_name="Otter Camera"
        )
        self.receiver.on_frame_cb = self.update_frame
        if reforward_cb:
            self.receiver.reforward_cb = reforward_cb

        self.controller = CamBridgeControl(host=target_ip, port=ctrl_p)

        def runner():
            try:
                self.receiver.start_receiver(enable_virtualcam=True, show_preview=False)
            finally:
                self.is_connected = False

        self.receiver_thread = threading.Thread(target=runner, daemon=True)
        self.receiver_thread.start()
        self.is_connected = True
        return {"status": "ok", "message": f"Connecting to {target_ip}:{stream_p}"}

    def stop_stream(self) -> dict:
        self.is_connected = False
        self.web_streamer_active = False
        if self.receiver:
            self.receiver.stop_receiver()
        if self.adb_tunnel:
            self.adb_tunnel.remove_forward()
        return {"status": "ok", "message": "Stream stopped"}

    def get_status(self) -> dict:
        # Check if web streamer timed out (>3s without frame)
        if self.web_streamer_active and (time.time() - self.last_web_frame_time > 3.0):
            self.web_streamer_active = False

        vcam_name = "Ready (Unity / OBS / V4L2)"
        source_type = "No Active Source"
        if self.is_connected:
            source_type = f"Android App ({self.active_mode.upper()})"
        elif self.web_streamer_active:
            source_type = "Mobile Browser (HTML5 WebRTC Streamer)"

        return {
            "is_connected": self.is_connected,
            "web_streamer_active": self.web_streamer_active,
            "source_type": source_type,
            "active_port": self.port,
            "host_lan_ip": self.get_lan_ip(),
            "virtual_camera_name": vcam_name
        }


# [AI-BLOCK: Custom HTTP Request Handler for API & MJPEG Streaming]
class OtterHTTPHandler(http.server.BaseHTTPRequestHandler):
    controller: OtterWebController = None
    web_ui_dir = os.path.join(_CURRENT_DIR, "web_ui")

    def log_message(self, format, *args):
        # Silence routine HTTP polling logs to avoid console pollution
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_file(os.path.join(self.web_ui_dir, "index.html"), "text/html")
        elif self.path == "/streamer" or self.path == "/streamer.html":
            self._serve_file(os.path.join(self.web_ui_dir, "streamer.html"), "text/html")
        elif self.path == "/qrcode.min.js":
            self._serve_file(os.path.join(self.web_ui_dir, "qrcode.min.js"), "application/javascript")
        elif self.path.startswith("/api/qr"):
            # Dynamic SVG / Data QR fallback or proxy endpoint
            query = self.path.split("?", 1)[-1] if "?" in self.path else ""
            import urllib.parse
            params = urllib.parse.parse_qs(query)
            data_url = params.get("data", ["http://localhost:8080/streamer"])[0]
            # Use lightweight QR Server or redirect
            qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(data_url)}"
            self.send_response(302)
            self.send_header("Location", qr_api)
            self.end_headers()
        elif self.path == "/api/status":
            st = self.controller.get_status()
            self._send_json(st)
        elif self.path.startswith("/api/detect_ip"):
            tether = network_discovery.detect_tethering_adapter()
            ip = None
            mode_type = "Wi-Fi"
            if tether and tether.get("gateways"):
                ip = tether["gateways"][0]
                mode_type = "USB Tethering Gateway"
            else:
                lan = network_discovery.detect_lan_adapters()
                if lan and lan[0].get("ips"):
                    ip = lan[0]["ips"][0]
                    mode_type = "LAN IP"
            self._send_json({"ip": ip, "type": mode_type})
        elif self.path.startswith("/mjpeg"):
            self._serve_mjpeg()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""

        if self.path == "/api/stream/start":
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
            res = self.controller.start_stream(
                ip=body.get("ip", "127.0.0.1"),
                stream_p=int(body.get("stream_port", 8089)),
                ctrl_p=int(body.get("control_port", 8090)),
                mode=body.get("mode", "auto")
            )
            self._send_json(res)

        elif self.path == "/api/stream/stop":
            res = self.controller.stop_stream()
            self._send_json(res)

        elif self.path == "/api/control":
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
            res = {}
            if self.controller.controller:
                res = self.controller.controller.send_command(body)
            self._send_json(res)

        elif self.path == "/api/background":
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
            mode = body.get("mode", "off")
            if self.controller.receiver:
                if mode == "preset":
                    preset_name = body.get("preset", "modern_office")
                    preset_path = os.path.join(_CURRENT_DIR, "wallpapers", f"{preset_name}.jpg")
                    self.controller.receiver.set_bg_image(preset_path)
                    self.controller.receiver.set_bg_mode("custom_image")
                else:
                    self.controller.receiver.set_bg_mode(mode)
            self._send_json({"status": "ok", "mode": mode})

        elif self.path == "/api/push_frame":
            # Direct frame transmission from mobile browser
            self.controller.push_web_streamer_frame(post_data)
            self._send_json({"status": "ok"})
        else:
            self.send_error(404, "Endpoint Not Found")

    def _serve_file(self, filepath: str, mime: str):
        if not os.path.exists(filepath):
            self.send_error(404, "File Not Found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_mjpeg(self):
        """Serve live MJPEG multipart video feed to web browser viewfinder."""
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()

        while True:
            frame = None
            with self.controller.latest_frame_lock:
                if self.controller.latest_frame is not None:
                    frame = self.controller.latest_frame.copy()

            if frame is not None and CV2_AVAILABLE:
                # Downscale preview thumbnail to preserve network bandwidth and CPU
                h, w = frame.shape[:2]
                target_w = 640
                target_h = int(h * (target_w / w))
                thumb = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                _, jpeg = cv2.imencode(".jpg", thumb, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
                frame_data = jpeg.tobytes()

                try:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                    self.wfile.write(frame_data)
                    self.wfile.write(b"\r\n")
                except (BrokenPipeError, ConnectionResetError):
                    break
            time.sleep(0.04) # ~25 FPS


# [AI-BLOCK: Browser Defaults & Detection Protocol (Brave Browser Default)]
def open_browser(url: str):
    """
    Open url in Brave Browser as primary default browser per coding agent rules.
    If Brave is unavailable, fall back to default system browser.
    """
    brave_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        "/usr/bin/brave-browser",
        "/usr/bin/brave",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    ]
    for p in brave_paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, url])
                return
            except Exception:
                pass

    brave_which = shutil.which("brave-browser") or shutil.which("brave")
    if brave_which:
        try:
            subprocess.Popen([brave_which, url])
            return
        except Exception:
            pass

    # Standard fallback
    import webbrowser
    webbrowser.open(url)


# [AI-BLOCK: Threaded HTTP Server Runner]
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_server(port: int = 8080, auto_open: bool = True):
    ctrl = OtterWebController(port=port)
    OtterHTTPHandler.controller = ctrl
    server = ThreadedHTTPServer(("0.0.0.0", ctrl.port), OtterHTTPHandler)

    url = f"http://localhost:{ctrl.port}"
    print("===================================================")
    print(f"  Otter Web Controller running at: {url}")
    print(f"  Mobile Web Streamer available at: {url}/streamer")
    print("===================================================")

    if auto_open:
        threading.Thread(target=lambda: (time.sleep(0.5), open_browser(url)), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Otter Web Controller...")
    finally:
        ctrl.stop_stream()
        server.server_close()


if __name__ == "__main__":
    start_server(port=8080, auto_open=True)
