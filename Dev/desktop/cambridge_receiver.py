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
    from driver.obs_virtualcam_bridge import OBSVirtualCamBridge
    OBS_VIRTUALCAM_AVAILABLE = True
except Exception:
    try:
        from Dev.desktop.driver.obs_virtualcam_bridge import OBSVirtualCamBridge
        OBS_VIRTUALCAM_AVAILABLE = True
    except Exception:
        OBS_VIRTUALCAM_AVAILABLE = False

try:
    from driver.linux_v4l2_bridge import LinuxV4L2Bridge
    LINUX_V4L2_AVAILABLE = True
except Exception:
    try:
        from Dev.desktop.driver.linux_v4l2_bridge import LinuxV4L2Bridge
        LINUX_V4L2_AVAILABLE = True
    except Exception:
        LINUX_V4L2_AVAILABLE = False

# [AI-BLOCK: High-Performance Standalone H.264 Video Stream Decoder]
class H264DecoderPipe:
    """
    Decodes incoming raw H.264 NAL units (from Android MediaCodec) using standalone static FFmpeg.
    Outputs uncompressed BGR frames without needing pyvirtualcam or C++ compilation.
    """
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.frame_size = width * height * 3
        self.proc = None
        self.running = False
        self.latest_frame = None
        self.lock = threading.Lock()
        self.reader_thread = None
        self._init_ffmpeg()

    def _init_ffmpeg(self):
        ffmpeg_exe = "ffmpeg"
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

        cmd = [
            ffmpeg_exe,
            "-loglevel", "error",
            "-f", "h264",
            "-i", "pipe:0",
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-vsync", "0",
            "pipe:1"
        ]
        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**7
            )
            self.running = True
            self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            print(f"H.264 FFmpeg decoder init notice: {e}")
            self.proc = None

    def _reader_loop(self):
        while self.running and self.proc and self.proc.stdout:
            try:
                raw_bytes = self.proc.stdout.read(self.frame_size)
                if len(raw_bytes) == self.frame_size:
                    frame = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((self.height, self.width, 3))
                    with self.lock:
                        self.latest_frame = frame
                elif len(raw_bytes) == 0:
                    break
            except Exception:
                break

    def push_packet(self, data: bytes):
        if self.proc and self.proc.stdin:
            try:
                self.proc.stdin.write(data)
                self.proc.stdin.flush()
            except Exception:
                pass

    def get_latest_frame(self) -> np.ndarray:
        with self.lock:
            frame = self.latest_frame
            self.latest_frame = None
            return frame

    def close(self):
        self.running = False
        if self.proc:
            try:
                self.proc.stdin.close()
            except Exception:
                pass
            try:
                self.proc.kill()
            except Exception:
                pass
            self.proc = None

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

    def start_receiver(self, enable_virtualcam=True, show_preview=False):
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
        obs_bridge = None
        v4l2_bridge = None
        if enable_virtualcam:
            # Windows: Option B - Standalone DirectShow shared memory driver
            if sys.platform.startswith("win") and UNITY_CAPTURE_AVAILABLE:
                try:
                    uc_bridge = UnityCaptureSharedMemory(cap_num=0)
                    if uc_bridge.connect():
                        print("DirectShow Virtual Camera active: 'Unity Video Capture'")
                except Exception as e:
                    print(f"DirectShow initialization notice: {e}")

            # Windows: Option A - Official OBS Virtual Camera Fallback (Universal)
            if sys.platform.startswith("win") and OBS_VIRTUALCAM_AVAILABLE:
                try:
                    obs_bridge = OBSVirtualCamBridge(width=self.width, height=self.height, fps=self.fps)
                    if obs_bridge.connect():
                        print("OBS Virtual Camera Fallback active: 'OBS Virtual Camera'")
                except Exception as e:
                    print(f"OBS Virtual Camera initialization notice: {e}")

            # Linux: Native v4l2loopback loopback device
            elif sys.platform.startswith("linux") and LINUX_V4L2_AVAILABLE:
                try:
                    v4l2_bridge = LinuxV4L2Bridge(width=self.width, height=self.height, fps=self.fps)
                    if v4l2_bridge.connect():
                        print(f"Linux V4L2 Virtual Camera active on {v4l2_bridge.device_path}")
                except Exception as e:
                    print(f"Linux V4L2 initialization notice: {e}")

            # Fallback to pyvirtualcam if available
            if uc_bridge is None and obs_bridge is None and v4l2_bridge is None and VIRTUAL_CAM_AVAILABLE:
                try:
                    vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR, device=self.camera_name)
                    print(f"Virtual Camera initialized: {vcam.device}")
                except Exception as e:
                    try:
                        vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR)
                        print(f"Virtual Camera initialized (default device): {vcam.device}")
                    except Exception as ex:
                        print(f"Virtual camera initialization notice: {ex}.")

        # Real-time H.264 stream decoder pipe
        decoder = H264DecoderPipe(width=self.width, height=self.height)

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

                frame = None
                # Check for standard JPEG packet
                if packet_data.startswith(b'\xff\xd8'):
                    nparr = np.frombuffer(packet_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                else:
                    # Raw H.264 NAL packet from Android MediaCodec
                    decoder.push_packet(packet_data)
                    frame = decoder.get_latest_frame()

                if frame is not None:
                    # Resize to match standard virtual camera canvas if needed
                    if frame.shape[1] != self.width or frame.shape[0] != self.height:
                        frame = cv2.resize(frame, (self.width, self.height))

                    if uc_bridge:
                        uc_bridge.send_frame(frame)
                    if obs_bridge:
                        obs_bridge.send_frame(frame)
                    if v4l2_bridge:
                        v4l2_bridge.send_frame(frame)
                    if vcam:
                        vcam.send(frame)
                        vcam.sleep_until_next_frame()

                    # Preview: only safe from main thread; skip in background thread mode
                    if show_preview:
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
            decoder.close()
            sock.close()
            if vcam:
                vcam.close()
            if uc_bridge:
                uc_bridge.close()
            if obs_bridge:
                obs_bridge.close()
            if v4l2_bridge:
                v4l2_bridge.close()
            if show_preview:
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
