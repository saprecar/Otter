import socket
import json
import time

# [AI-BLOCK: CamBridge Remote Control Client for Zoom, Lens, Pause, Status]
class CamBridgeControl:
    def __init__(self, host="127.0.0.1", port=8090, timeout=3.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_command(self, payload: dict) -> dict:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                message = json.dumps(payload) + "\n"
                s.sendall(message.encode("utf-8"))
                response = s.recv(4096).decode("utf-8")
                return json.loads(response.strip()) if response else {}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def switch_camera(self):
        return self.send_command({"action": "switch_camera"})

    def toggle_mirror(self):
        return self.send_command({"action": "toggle_mirror"})

    def rotate_camera(self):
        return self.send_command({"action": "rotate_camera"})

    def set_rotation(self, angle: int):
        return self.send_command({"action": "set_rotation", "angle": angle})

    def toggle_torch(self):
        return self.send_command({"action": "toggle_torch"})

    def toggle_glow(self):
        return self.send_command({"action": "toggle_glow"})

    def toggle_af(self):
        return self.send_command({"action": "toggle_af"})

    def set_focus(self, auto: bool = True, distance: float = 0.0):
        return self.send_command({"action": "set_focus", "auto": auto, "distance": distance})

    def cycle_focus(self):
        return self.send_command({"action": "cycle_focus"})

    def cycle_exposure(self):
        return self.send_command({"action": "cycle_exposure"})

    def set_exposure(self, value: int):
        return self.send_command({"action": "set_exposure", "value": value})

    def set_resolution(self, width: int, height: int):
        return self.send_command({"action": "set_resolution", "width": width, "height": height})

    def zoom_in(self):
        return self.send_command({"action": "zoom_in"})

    def zoom_out(self):
        return self.send_command({"action": "zoom_out"})

    def set_zoom(self, zoom_factor: float):
        return self.send_command({"action": "set_zoom", "value": zoom_factor})

    def set_iso(self, value: int):
        return self.send_command({"action": "set_iso", "value": value})

    def set_shutter(self, value: int):
        return self.send_command({"action": "set_shutter", "value": value})

    def set_awb(self, mode: int):
        return self.send_command({"action": "set_awb", "mode": mode})

    def set_effect(self, effect: int):
        return self.send_command({"action": "set_effect", "effect": effect})

    def set_fps(self, fps: int):
        return self.send_command({"action": "set_fps", "fps": fps})

    def set_quick_mode(self, mode: str):
        return self.send_command({"action": "set_quick_mode", "mode": mode})

    def set_background_mode(self, mode: str, workload: str = "pc"):
        return self.send_command({"action": "set_background_mode", "mode": mode, "workload": workload})

    def toggle_keep_screen_on(self):
        return self.send_command({"action": "toggle_keep_screen_on"})

    def set_keep_screen_on(self, enabled: bool):
        return self.send_command({"action": "set_keep_screen_on", "enabled": enabled})

    def capture_still(self):
        return self.send_command({"action": "capture_still"})

    def get_capabilities(self):
        return self.send_command({"action": "get_capabilities"})

    def start_stream(self):
        return self.send_command({"action": "start_stream"})

    def stop_stream(self):
        return self.send_command({"action": "stop_stream"})

    def pause(self):
        return self.send_command({"action": "pause"})

    def resume(self):
        return self.send_command({"action": "resume"})

    def set_connection_mode(self, mode: str):
        return self.send_command({"action": "set_connection_mode", "mode": mode})

    def get_status(self):
        return self.send_command({"action": "get_status"})

    def get_info(self):
        return self.send_command({"action": "get_info"})
