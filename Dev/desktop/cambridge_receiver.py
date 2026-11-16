import argparse
import socket
import struct
import sys
import threading
import time

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import pyvirtualcam
    VIRTUAL_CAM_AVAILABLE = True
except ImportError:
    VIRTUAL_CAM_AVAILABLE = False

from adb_tunnel import ADBTunnel
from cambridge_control import CamBridgeControl

try:
    from driver.unity_capture_bridge import UnityCaptureSharedMemory
    UNITY_CAPTURE_AVAILABLE = True
except Exception:
    try:
        from Dev.desktop.driver.unity_capture_bridge import UnityCaptureSharedMemory
        UNITY_CAPTURE_AVAILABLE = True
    except Exception:
        UNITY_CAPTURE_AVAILABLE = False

try:
    from driver.linux_v4l2_bridge import LinuxV4L2Bridge
    LINUX_V4L2_AVAILABLE = True
except Exception:
    try:
        from Dev.desktop.driver.linux_v4l2_bridge import LinuxV4L2Bridge
        LINUX_V4L2_AVAILABLE = True
    except Exception:
        LINUX_V4L2_AVAILABLE = False

# [AI-BLOCK: Main CamBridge Receiver and Virtual Camera Feed]
class CamBridgeReceiver:
    def __init__(self, host="127.0.0.1", stream_port=8089, control_port=8090, width=1280, height=720, fps=30, camera_name="Otter Camera 1", window_title=None):
        self.host = host
        self.stream_port = stream_port
        self.control_port = control_port
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_name = camera_name
        self.window_title = window_title if window_title else f"Otter PC Monitor - {camera_name} [Port: {stream_port}]"
        self.running = False
        self.controller = CamBridgeControl(host=self.host, port=self.control_port)

    def start_receiver(self, enable_virtualcam=True):
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            print("Notice: 'opencv-python' or 'numpy' is not installed. Please install with: pip install -r requirements.txt")
            return

        self.running = True
        print(f"CamBridge connecting to {self.host}:{self.stream_port}...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        connected = False
        while self.running and not connected:
            try:
                sock.connect((self.host, self.stream_port))
                connected = True
                print("Connected to CamBridge video stream.")
            except Exception:
                time.sleep(1.0)

        if not connected:
            return

        sock.settimeout(None)

        # Virtual camera setup or OpenCV preview fallback
        vcam = None
        uc_bridge = None
        v4l2_bridge = None
        if enable_virtualcam:
            # Windows: Standalone DirectShow shared memory driver (Priority 1)
            if sys.platform.startswith("win") and UNITY_CAPTURE_AVAILABLE:
                try:
                    uc_bridge = UnityCaptureSharedMemory(cap_num=0)
                    if uc_bridge.connect():
                        print("DirectShow Virtual Camera initialized: 'Unity Video Capture' (Standalone Driver active)")
                except Exception as e:
                    print(f"Standalone DirectShow initialization notice: {e}")

            # Linux: Native v4l2loopback loopback device (Priority 1 on Linux)
            elif sys.platform.startswith("linux") and V4L2_LOOPBACK_AVAILABLE:
                try:
                    v4l2_bridge = LinuxV4L2Bridge(width=self.width, height=self.height, fps=self.fps)
                    if v4l2_bridge.connect():
                        print(f"Linux V4L2 Virtual Camera initialized on {v4l2_bridge.device_path}")
                except Exception as e:
                    print(f"Linux V4L2 initialization notice: {e}")

            # Fallback to pyvirtualcam if available
            if uc_bridge is None and v4l2_bridge is None and VIRTUAL_CAM_AVAILABLE:
                try:
                    vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR, device=self.camera_name)
                    print(f"Virtual Camera initialized: {vcam.device}")
                except Exception as e:
                    try:
                        vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR)
                        print(f"Virtual Camera initialized (default device): {vcam.device}")
                    except Exception as ex:
                        print(f"Virtual camera initialization notice: {ex}.")
            if vcam is None and sys.platform.startswith("linux") and LINUX_V4L2_AVAILABLE:
                try:
                    v4l2_bridge = LinuxV4L2Bridge(width=self.width, height=self.height, fps=self.fps)
                    if v4l2_bridge.connect():
                        print(f"Linux V4L2 Virtual Camera initialized on {v4l2_bridge.device}")
                except Exception as e:
                    print(f"Linux V4L2 initialization notice: {e}")

        # Demux packet stream (Length prefix + NAL payload)
        try:
            while self.running:
                raw_len = self._recv_exact(sock, 4)
                if not raw_len:
                    break
                (packet_len,) = struct.unpack("!I", raw_len)
                if packet_len <= 0 or packet_len > 10_000_000:
                    continue

                packet_data = self._recv_exact(sock, packet_len)
                if not packet_data:
                    break

                # Frame decode via OpenCV
                nparr = np.frombuffer(packet_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Resize to match standard virtual camera canvas if needed
                    if frame.shape[1] != self.width or frame.shape[0] != self.height:
                        frame = cv2.resize(frame, (self.width, self.height))

                    if vcam:
                        vcam.send(frame)
                        vcam.sleep_until_next_frame()
                    elif uc_bridge:
                        uc_bridge.send_frame(frame)
                    elif v4l2_bridge:
                        v4l2_bridge.send_frame(frame)

                    # Interactive PC control window
                    cv2.imshow(self.window_title, frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key in (ord('+'), ord('=')):
                        self.controller.zoom_in()
                    elif key == ord('-'):
                        self.controller.zoom_out()
                    elif key == ord('c'):
                        self.controller.switch_camera()
                    elif key == ord(' '):
                        info = self.controller.get_info()
                        if info.get("isPaused", False):
                            self.controller.resume()
                        else:
                            self.controller.pause()

        except Exception as e:
            print(f"Stream encountered event: {e}")
        finally:
            self.running = False
            sock.close()
            if vcam:
                vcam.close()
            if uc_bridge:
                uc_bridge.close()
            if v4l2_bridge:
                v4l2_bridge.close()
            cv2.destroyAllWindows()
            print("CamBridge Receiver terminated cleanly.")

    def stop_receiver(self):
        self.running = False

    def _recv_exact(self, sock, num_bytes):
        buffer = bytearray()
        while len(buffer) < num_bytes and self.running:
            try:
                packet = sock.recv(num_bytes - len(buffer))
                if not packet:
                    return None
                buffer.extend(packet)
            except Exception:
                return None
        return bytes(buffer)

def main():
    parser = argparse.ArgumentParser(description="CamBridge Desktop Virtual Camera & Remote Controller")
    parser.add_argument("--mode", choices=["usb", "wifi"], default="usb", help="Connection mode: usb (via ADB tunnel) or wifi")
    parser.add_argument("--ip", default="127.0.0.1", help="Target IP for WiFi mode (default: 127.0.0.1 for USB/ADB)")
    parser.add_argument("--stream-port", type=int, default=8089, help="Video stream port")
    parser.add_argument("--control-port", type=int, default=8090, help="Control RPC port")
    parser.add_argument("--no-vcam", action="store_true", help="Disable virtual camera and only show window monitor")

    args = parser.parse_args()

    tunnel = None
    target_ip = args.ip

    if args.mode == "usb":
        tunnel = ADBTunnel(stream_port=args.stream_port, control_port=args.control_port)
        if tunnel.is_available():
            devices = tunnel.list_devices()
            if devices:
                print(f"Detected ADB device: {devices[0]}. Configuring non-root tunnel...")
                tunnel.setup_forward(devices[0])
            else:
                print("No USB device found with 'adb devices'. Ensure USB debugging is ON.")
        else:
            print("Notice: 'adb' executable not found in PATH. If using WiFi or external tunnel, specify --mode wifi --ip <phone-ip>.")

    receiver = CamBridgeReceiver(
        host=target_ip,
        stream_port=args.stream_port,
        control_port=args.control_port
    )

    try:
        receiver.start_receiver(enable_virtualcam=not args.no_vcam)
    finally:
        if tunnel:
            tunnel.remove_forward()

if __name__ == "__main__":
    main()
