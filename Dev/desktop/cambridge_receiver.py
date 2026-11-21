import argparse
import os
import socket
import struct
import subprocess
import shutil
import sys
import threading
import time

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

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

try:
    from adb_tunnel import ADBTunnel
    from cambridge_control import CamBridgeControl
except ImportError:
    from Dev.desktop.adb_tunnel import ADBTunnel
    from Dev.desktop.cambridge_control import CamBridgeControl

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
    def __init__(self, width=1280, height=720, on_frame=None):
        self.width = width
        self.height = height
        self.frame_size = width * height * 3
        self.on_frame = on_frame
        self.proc = None
        self.running = False
        self.latest_frame = None
        self.lock = threading.Lock()
        self.reader_thread = None
        self._init_ffmpeg()

    def _find_ffmpeg(self) -> str:
        # 1. Try imageio_ffmpeg in current python environment
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.isfile(exe):
                return exe
        except Exception:
            pass

        # 2. Check local/parent .venv site-packages for bundled imageio_ffmpeg binary
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidate_dirs = [
            os.path.join(script_dir, ".venv"),
            os.path.join(script_dir, "..", "..", ".venv"),
            os.path.join(script_dir, "venv"),
            os.path.join(script_dir, "..", "..", "venv"),
            os.path.dirname(sys.executable)
        ]
        for cdir in candidate_dirs:
            if not os.path.isdir(cdir):
                continue
            for root, _, files in os.walk(cdir):
                if "imageio_ffmpeg" in root and "binaries" in root:
                    for f in files:
                        if f.startswith("ffmpeg") and (f.endswith(".exe") or not f.endswith(".py")):
                            full_path = os.path.join(root, f)
                            if os.path.isfile(full_path):
                                return full_path

        # 3. Check system PATH
        which_ffmpeg = shutil.which("ffmpeg")
        if which_ffmpeg:
            return which_ffmpeg

        # 4. Common Windows paths
        win_candidates = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\obs-studio\bin\64bit\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
            os.path.expanduser(r"~\scoop\apps\ffmpeg\current\bin\ffmpeg.exe")
        ]
        for p in win_candidates:
            if os.path.isfile(p):
                return p

        return "ffmpeg"

    def _init_ffmpeg(self):
        ffmpeg_exe = self._find_ffmpeg()

        cmd = [
            ffmpeg_exe,
            "-loglevel", "warning",
            "-f", "h264",
            "-i", "pipe:0",
            "-vf", f"scale={self.width}:{self.height}",
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "pipe:1"
        ]
        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=None,
                bufsize=0
            )
            self.running = True
            self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            print(f"H.264 FFmpeg decoder init notice: {e} (binary attempted: {ffmpeg_exe})")
            self.proc = None

    def _read_exact(self, n):
        buf = bytearray()
        while len(buf) < n and self.running:
            try:
                chunk = self.proc.stdout.read(min(n - len(buf), 65536))
                if not chunk:
                    return None
                buf.extend(chunk)
            except Exception:
                return None
        return bytes(buf)

    def _reader_loop(self):
        while self.running and self.proc and self.proc.stdout:
            raw_bytes = self._read_exact(self.frame_size)
            if raw_bytes and len(raw_bytes) == self.frame_size:
                frame = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((self.height, self.width, 3))
                with self.lock:
                    self.latest_frame = frame
                if self.on_frame:
                    try:
                        self.on_frame(frame)
                    except Exception:
                        pass
            elif not self.running:
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

# [AI-BLOCK: Virtual Background Replacement & Workload Offload Processor]
class VirtualBackgroundProcessor:
    """
    Real-time virtual background compositing and AI offload engine.
    Supports:
      - Workload routing: PC GPU/CPU offload vs on-device mobile processing.
      - Modes: 'off', 'blur_light', 'blur_heavy', 'custom_image', 'chroma_green'.
      - Fast image caching and dynamic resolution scaling.
      - Dual pipeline: High-speed OpenCV color/vignette keying + optional MediaPipe AI segmentation.
    """
    def __init__(self):
        self.mode = "off"
        self.workload = "pc"
        self.custom_image_path = None
        self.cached_bg_image = None
        self.cached_bg_res = (0, 0)
        self.lock = threading.Lock()

        self.mp_segmentation = None
        try:
            import mediapipe as mp
            self.mp_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
        except Exception:
            self.mp_segmentation = None

    def set_mode(self, mode: str):
        with self.lock:
            self.mode = str(mode).strip().lower()
            print(f"Virtual Background mode set to: {self.mode}")

    def set_workload(self, workload: str):
        with self.lock:
            self.workload = str(workload).strip().lower()
            print(f"Virtual Background workload routed to: {self.workload}")

    def set_custom_image(self, path: str):
        with self.lock:
            self.custom_image_path = path
            self.cached_bg_image = None
            self.cached_bg_res = (0, 0)
            print(f"Virtual Background custom image set: {path}")

    def _get_background_image(self, width: int, height: int) -> np.ndarray:
        if self.custom_image_path and os.path.isfile(self.custom_image_path):
            if self.cached_bg_image is not None and self.cached_bg_res == (width, height):
                return self.cached_bg_image
            try:
                img = cv2.imread(self.custom_image_path)
                if img is not None:
                    scaled = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
                    self.cached_bg_image = scaled
                    self.cached_bg_res = (width, height)
                    return scaled
            except Exception:
                pass
        fallback = np.full((height, width, 3), (35, 25, 20), dtype=np.uint8)
        return fallback

    def _create_portrait_mask(self, frame: np.ndarray, w: int, h: int) -> np.ndarray:
        if self.mp_segmentation is not None:
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = self.mp_segmentation.process(rgb)
                if res.segmentation_mask is not None:
                    mask = res.segmentation_mask
                    mask = cv2.GaussianBlur(mask, (7, 7), 0)
                    return np.clip(mask, 0.0, 1.0)
            except Exception:
                pass

        cx, cy = w // 2, int(h * 0.55)
        rx, ry = max(1, int(w * 0.38)), max(1, int(h * 0.48))
        y, x = np.ogrid[:h, :w]
        dist_sq = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        mask = np.clip(1.0 - (dist_sq - 0.45) / 0.75, 0.0, 1.0)
        mask = cv2.GaussianBlur(mask.astype(np.float32), (31, 31), 0)
        return mask

    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame is None or not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            return frame

        with self.lock:
            mode = self.mode
            workload = self.workload

        if mode in ("off", "none", "") or workload == "mobile":
            return frame

        h, w = frame.shape[:2]

        if mode == "blur_light":
            blurred = cv2.GaussianBlur(frame, (25, 25), 0)
            mask = self._create_portrait_mask(frame, w, h)
            mask_3c = cv2.merge([mask, mask, mask])
            out = (frame.astype(np.float32) * mask_3c + blurred.astype(np.float32) * (1.0 - mask_3c)).astype(np.uint8)
            return out

        elif mode == "blur_heavy":
            blurred = cv2.GaussianBlur(frame, (55, 55), 0)
            mask = self._create_portrait_mask(frame, w, h)
            mask_3c = cv2.merge([mask, mask, mask])
            out = (frame.astype(np.float32) * mask_3c + blurred.astype(np.float32) * (1.0 - mask_3c)).astype(np.uint8)
            return out

        elif mode in ("green_screen", "solid_green", "chroma_key"):
            mask = self._create_portrait_mask(frame, w, h)
            mask_3c = cv2.merge([mask, mask, mask])
            green_bg = np.zeros((h, w, 3), dtype=np.uint8)
            green_bg[:, :] = (0, 255, 0) # Pure Chroma Green in BGR (0, 255, 0)
            out = (frame.astype(np.float32) * mask_3c + green_bg.astype(np.float32) * (1.0 - mask_3c)).astype(np.uint8)
            return out

        elif mode == "chroma_green":
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_green = np.array([35, 45, 45], dtype=np.uint8)
            upper_green = np.array([85, 255, 255], dtype=np.uint8)
            green_mask = cv2.inRange(hsv, lower_green, upper_green)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
            green_mask = cv2.GaussianBlur(green_mask, (7, 7), 0)
            alpha_bg = (green_mask.astype(np.float32) / 255.0)[:, :, np.newaxis]

            bg = self._get_background_image(w, h)
            out = (frame.astype(np.float32) * (1.0 - alpha_bg) + bg.astype(np.float32) * alpha_bg).astype(np.uint8)
            return out

        elif mode == "custom_image":
            mask = self._create_portrait_mask(frame, w, h)
            mask_3c = cv2.merge([mask, mask, mask])
            bg = self._get_background_image(w, h)
            out = (frame.astype(np.float32) * mask_3c + bg.astype(np.float32) * (1.0 - mask_3c)).astype(np.uint8)
            return out

        return frame

# [AI-BLOCK: Main CamBridge Receiver and Virtual Camera Feed]
class CamBridgeReceiver:
    def __init__(self, host="127.0.0.1", stream_port=8089, control_port=8090, width=1280, height=720, fps=30, camera_name="Otter Camera 1", window_title=None, rotation=0):
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
        self.rotation_angle = rotation
        self.bg_processor = VirtualBackgroundProcessor()
        self.reforward_cb = None   # set by caller: re-runs 'adb forward' before each retry
        self.on_frame_cb = None    # optional callback for GUI live preview thumbnail

    def set_rotation(self, angle: int):
        self.rotation_angle = ((angle % 360) + 360) % 360
        print(f"Receiver video rotation set to {self.rotation_angle}°.")

    def set_bg_mode(self, mode: str):
        self.bg_processor.set_mode(mode)

    def set_bg_workload(self, workload: str):
        self.bg_processor.set_workload(workload)

    def set_bg_image(self, path: str):
        self.bg_processor.set_custom_image(path)

    def _connect_with_retry(self, host, port, max_wait=10.0):
        """Retry until phone stream is up. Re-run ADB forward each try. Gives a clear error."""
        deadline = time.time() + max_wait
        while self.running:
            if self.reforward_cb:
                try:
                    self.reforward_cb()
                except Exception as e:
                    print(f"Re-forward failed: {e}")
            try:
                s = socket.create_connection((host, port), timeout=3)
                s.settimeout(2.5)
                print(f"Connected to {host}:{port}")
                return s
            except OSError as e:
                print(f"Waiting for phone stream on {host}:{port} ({e.__class__.__name__}).")
                if time.time() > deadline:
                    print("TIMEOUT: Camera stream port not reachable. Check: 1) Start pressed on phone  2) USB debugging / Tethering ON "
                          "3) Cable connected  4) 'adb devices' shows phone if USB mode  "
                          "5) if Wi-Fi mode, phone IP is right.")
                    return None
                time.sleep(1.5)
        return None

    def start_receiver(self, enable_virtualcam=True, show_preview=False):
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            print("Notice: 'opencv-python' or 'numpy' is not installed. Please install with: pip install -r requirements.txt")
            return

        self.running = True
        print(f"CamBridge connecting to {self.host}:{self.stream_port}...")

        sock = self._connect_with_retry(self.host, self.stream_port)
        if not sock:
            return
        self.sock = sock

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

        # Background thread to sync rotation state from mobile device
        def _sync_device_rotation():
            while self.running:
                try:
                    time.sleep(1.0)
                    st = self.controller.get_status()
                    if st.get("status") == "ok":
                        remote_rot = st.get("rotationAngle")
                        if remote_rot is not None and remote_rot != self.rotation_angle:
                            self.rotation_angle = remote_rot
                            print(f"Synced video rotation from mobile device: {self.rotation_angle}°.")
                except Exception:
                    pass

        rot_sync_thread = threading.Thread(target=_sync_device_rotation, daemon=True)
        rot_sync_thread.start()

        self.dispatched_count = 0
        def dispatch_frame(frame):
            if frame is None:
                return

            rot = self.rotation_angle % 360
            if rot == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif rot == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif rot == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Pass clean rotated camera frame to UI viewfinder preview before pillarboxing
            if self.on_frame_cb:
                try:
                    self.on_frame_cb(frame)
                except Exception:
                    pass

            fh, fw = frame.shape[:2]
            if fw != self.width or fh != self.height:
                if rot in (90, 270):
                    # Aspect-ratio preserving fit with black pillarboxes on sides for portrait orientation
                    scale = min(self.width / fw, self.height / fh)
                    nw, nh = int(fw * scale), int(fh * scale)
                    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
                    canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    x_off = (self.width - nw) // 2
                    y_off = (self.height - nh) // 2
                    canvas[y_off:y_off + nh, x_off:x_off + nw] = resized
                    frame = canvas
                else:
                    frame = cv2.resize(frame, (self.width, self.height))

            # Apply Virtual Background replacement & AI offload engine
            frame = self.bg_processor.process(frame)

            if uc_bridge:
                uc_bridge.send_frame(frame)
            if obs_bridge:
                obs_bridge.send_frame(frame)
            if v4l2_bridge:
                v4l2_bridge.send_frame(frame)
            if vcam:
                vcam.send(frame)
                vcam.sleep_until_next_frame()

            self.dispatched_count += 1
            if self.dispatched_count == 1:
                print(f"Streaming live video: First frame received and dispatched ({self.width}x{self.height}, rot={rot}°).")
            elif self.dispatched_count % 150 == 0:
                print(f"Streaming live video: Dispatched {self.dispatched_count} frames to virtual cameras (rot={rot}°).")

        # Real-time H.264 stream decoder pipe with auto-scaling and direct frame dispatch
        decoder = H264DecoderPipe(width=self.width, height=self.height, on_frame=dispatch_frame)

        # Demux packet stream (Length prefix + NAL payload)
        try:
            consecutive_timeouts = 0
            while self.running:
                try:
                    raw_len = self._recv_exact(sock, 4)
                except socket.timeout:
                    consecutive_timeouts += 1
                    if consecutive_timeouts >= 2:
                        print("Phone video stream timeout: Device disconnected.")
                        break
                    continue
                except (ConnectionResetError, BrokenPipeError, OSError) as e:
                    print(f"Phone video connection lost: {e}")
                    break

                if not raw_len:
                    print("Phone video connection closed.")
                    break
                consecutive_timeouts = 0

                (packet_len,) = struct.unpack("!I", raw_len)
                if packet_len <= 0 or packet_len > 10_000_000:
                    continue

                try:
                    packet_data = self._recv_exact(sock, packet_len)
                except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError):
                    print("Phone video connection lost mid-packet.")
                    break
                if not packet_data:
                    break

                # Check for standard JPEG packet fallback
                if packet_data.startswith(b'\xff\xd8'):
                    nparr = np.frombuffer(packet_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    dispatch_frame(frame)
                else:
                    # Raw H.264 NAL packet from Android MediaCodec
                    decoder.push_packet(packet_data)

                # Preview: only safe from main thread; skip in background thread mode
                if show_preview:
                    preview_frame = decoder.get_latest_frame()
                    if preview_frame is not None:
                        cv2.imshow(self.window_title, preview_frame)
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

    def push_external_frame(self, frame):
        """
        [AI-BLOCK: Push an uncompressed BGR frame directly to active Virtual Cameras and UI monitor]
        Enables REQ-023/REQ-024 browser WebRTC/HTML5 streamer to pipe video directly to virtual webcam drivers.
        """
        if frame is None or not CV2_AVAILABLE:
            return

        rot = self.rotation_angle % 360
        if rot == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rot == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rot == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if self.on_frame_cb:
            try:
                self.on_frame_cb(frame)
            except Exception:
                pass

        fh, fw = frame.shape[:2]
        if fw != self.width or fh != self.height:
            if rot in (90, 270):
                scale = min(self.width / fw, self.height / fh)
                nw, nh = int(fw * scale), int(fh * scale)
                resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
                canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                x_off = (self.width - nw) // 2
                y_off = (self.height - nh) // 2
                canvas[y_off:y_off + nh, x_off:x_off + nw] = resized
                frame = canvas
            else:
                frame = cv2.resize(frame, (self.width, self.height))

        frame = self.bg_processor.process(frame)

        if hasattr(self, 'uc_bridge') and self.uc_bridge:
            self.uc_bridge.send_frame(frame)
        if hasattr(self, 'obs_bridge') and self.obs_bridge:
            self.obs_bridge.send_frame(frame)
        if hasattr(self, 'v4l2_bridge') and self.v4l2_bridge:
            self.v4l2_bridge.send_frame(frame)
        if hasattr(self, 'vcam') and self.vcam:
            self.vcam.send(frame)
            self.vcam.sleep_until_next_frame()

    def start_virtualcam_only(self):
        """Initialize virtual camera drivers without connecting to an Android TCP stream socket."""
        self.running = True
        self.uc_bridge = None
        self.obs_bridge = None
        self.v4l2_bridge = None
        self.vcam = None

        if sys.platform.startswith("win") and UNITY_CAPTURE_AVAILABLE:
            try:
                self.uc_bridge = UnityCaptureSharedMemory(cap_num=0)
                if self.uc_bridge.connect():
                    print("DirectShow Virtual Camera active: 'Unity Video Capture'")
            except Exception as e:
                print(f"DirectShow initialization notice: {e}")

        if sys.platform.startswith("win") and OBS_VIRTUALCAM_AVAILABLE:
            try:
                self.obs_bridge = OBSVirtualCamBridge(width=self.width, height=self.height, fps=self.fps)
                if self.obs_bridge.connect():
                    print("OBS Virtual Camera Fallback active: 'OBS Virtual Camera'")
            except Exception as e:
                print(f"OBS Virtual Camera initialization notice: {e}")

        elif sys.platform.startswith("linux") and LINUX_V4L2_AVAILABLE:
            try:
                self.v4l2_bridge = LinuxV4L2Bridge(width=self.width, height=self.height, fps=self.fps)
                if self.v4l2_bridge.connect():
                    print(f"Linux V4L2 Virtual Camera active on {self.v4l2_bridge.device_path}")
            except Exception as e:
                print(f"Linux V4L2 initialization notice: {e}")

        if self.uc_bridge is None and self.obs_bridge is None and self.v4l2_bridge is None and VIRTUAL_CAM_AVAILABLE:
            try:
                self.vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR, device=self.camera_name)
                print(f"Virtual Camera initialized: {self.vcam.device}")
            except Exception as e:
                try:
                    self.vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR)
                    print(f"Virtual Camera initialized (default device): {self.vcam.device}")
                except Exception as ex:
                    print(f"Virtual camera initialization notice: {ex}.")

    def stop_receiver(self):
        self.running = False
        if hasattr(self, 'sock') and self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def _recv_exact(self, sock, num_bytes):
        buffer = bytearray()
        while len(buffer) < num_bytes and self.running:
            try:
                packet = sock.recv(num_bytes - len(buffer))
                if not packet:
                    return None
                buffer.extend(packet)
            except socket.timeout:
                if len(buffer) == 0:
                    raise
                continue
            except (ConnectionResetError, BrokenPipeError, OSError):
                return None
            except Exception:
                return None
        return bytes(buffer)

def main():
    parser = argparse.ArgumentParser(description="CamBridge Desktop Virtual Camera & Remote Controller")
    parser.add_argument("--mode", choices=["auto", "usb", "wifi"], default="auto", help="Connection mode: auto (USB first, then Wi-Fi), usb (via ADB tunnel) or wifi")
    parser.add_argument("--ip", default="127.0.0.1", help="Target IP for WiFi mode (default: 127.0.0.1 for USB/ADB)")
    parser.add_argument("--stream-port", type=int, default=8089, help="Video stream port")
    parser.add_argument("--control-port", type=int, default=8090, help="Control RPC port")
    parser.add_argument("--no-vcam", action="store_true", help="Disable virtual camera and only show window monitor")
    parser.add_argument("--rotate", type=int, choices=[0, 90, 180, 270], default=0, help="Initial video rotation in degrees")

    args = parser.parse_args()

    tunnel = None
    target_ip = args.ip
    reforward_cb = None

    if args.mode in ("auto", "usb"):
        tunnel = ADBTunnel(stream_port=args.stream_port, control_port=args.control_port)
        serial = tunnel.usb_serial() if tunnel.is_available() else None
        if serial:
            print(f"Detected ADB device: {serial}. Configuring non-root tunnel...")
            if tunnel.setup_forward(serial):
                target_ip = "127.0.0.1"
                reforward_cb = lambda: tunnel.setup_forward(serial)
            elif args.mode == "auto":
                print("ADB forward failed. Falling back to Wi-Fi target IP...")
                target_ip = args.ip
        elif args.mode == "usb":
            print("No USB device found with 'adb devices'. Ensure USB debugging is ON.")
            target_ip = "127.0.0.1"
            if tunnel.is_available():
                reforward_cb = lambda: tunnel.setup_forward()
        else: # auto mode without USB device
            print(f"No USB device detected. Using Wi-Fi target IP: {args.ip}...")
            target_ip = args.ip
    else: # wifi mode
        target_ip = args.ip

    receiver = CamBridgeReceiver(
        host=target_ip,
        stream_port=args.stream_port,
        control_port=args.control_port,
        rotation=args.rotate
    )
    if reforward_cb:
        receiver.reforward_cb = reforward_cb

    try:
        receiver.start_receiver(enable_virtualcam=not args.no_vcam)
    finally:
        if tunnel:
            tunnel.remove_forward()

if __name__ == "__main__":
    main()
