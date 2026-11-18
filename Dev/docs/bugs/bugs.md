# Bug Tracking

- BUG-001 | 2026-11-16 | MainActivity.java | Guarded WiFi SecurityException on Android 12+ and added permission callback. Status: Tested
- BUG-002 | 2026-11-16 | MainActivity.java | Flip crashes app due to unreleased MediaCodec/surface and improper camera facing toggle. Status: Tested
- BUG-003 | 2026-11-17 | otter_app.py | Missing ADB on machines without Android Studio causes USB tunnel failure. Status: Tested
- BUG-004 | 2026-11-17 | unity_capture_bridge.py | Green diagnostic screen in DirectShow virtual camera due to event handshake and buffer layout mismatch. Status: Fixed
- BUG-005 | 2026-11-17 | MainActivity.java / cambridge_receiver.py | Video stream packet mismatch: H.264 NAL packets sent to cv2.imdecode caused None return and 0 decoded frames. Status: Fixed
- BUG-006 | 2026-11-17 | cambridge_receiver.py | FFmpeg pipe partial reads and unscaled resolution prevented frame dispatch to virtual cam. Status: Fixed
- BUG-007 | 2026-11-17 | obs_virtualcam_bridge.py | Struct alignment mismatch caused interval=0 in shared memory, crashing obs-virtualcam-module64.dll with c0000094. Status: Fixed
- BUG-008 | 2026-11-17 | cambridge_receiver.py / otter_app.py | Portrait phone orientation and manual camera rotation only applied to phone preview and not PC stream. Status: Fixed
- BUG-009 | 2026-11-17 | MainActivity.java | IllegalStateException on stream start caused by encoding loop polling MediaCodec before Executing state. Status: Fixed
- BUG-010 | 2026-11-17 | MainActivity.java / layout-land | Landscape camera sensor direction calculation and landscape layout viewport sizing mismatch. Status: Fixed
- BUG-011 | 2026-11-18 | run_linux.sh / run_macos.sh | PEP 668 externally-managed-environment and missing python3-tk cause launch crash on Linux/macOS. Status: Tested
- BUG-012 | 2026-11-18 | MainActivity.java | Max-resolution 50MP ImageReader in session targets caused onConfigureFailed and green screen. Fix: Decoupled still target from streaming session. Status: Tested
- BUG-013 | 2026-11-18 | MainActivity.java | MediaCodec missing KEY_PREPEND_HEADER_TO_SYNC_FRAMES and keyframe request on connect. Fix: In-band headers and sync frame on accept. Status: Tested
- BUG-014 | 2026-11-18 | AboutActivity.java / activity_about.xml | App settings hardcoded v1.0.0.1. Fix: Dynamic PackageManager lookup for versionName and versionCode. Status: Tested
- BUG-015 | 2026-11-18 | MainActivity.java / otter_app.py | Phone bottom label always showed Wi-Fi IP. Fix: Dynamic client IP detection and set_connection_mode RPC. Status: Tested
- BUG-016 | 2026-11-19 | otter_app.py | USB Tethering mode used loopback 127.0.0.1 instead of detected RNDIS gateway. Fix: Mode-aware tether gateway fallback in start_stream and mode switch. Status: Tested
- BUG-017 | 2026-11-19 | otter_app.py / cambridge_receiver.py | Client hung in streaming state on device disconnect; connect button stayed disabled. Fix: Socket timeout disconnect detector and start/stop RPC sync. Status: Tested
- BUG-018 | 2026-11-19 | MainActivity.java / otter_app.py | Viewfinder sideways on phone and pillarboxed on desktop canvas. Fix: Sensor rotation mapping, TextureView transform fix, and canvas aspect ratio fit. Status: Tested