# Bug Tracking

- BUG-001 | 2026-11-16 | MainActivity.java | Guarded WiFi SecurityException on Android 12+ and added permission callback. Status: Tested
- BUG-002 | 2026-11-16 | MainActivity.java | Flip crashes app due to unreleased MediaCodec/surface and improper camera facing toggle. Status: Tested
- BUG-003 | 2026-11-17 | otter_app.py | Missing ADB on machines without Android Studio causes USB tunnel failure. Status: Tested
- BUG-004 | 2026-11-17 | unity_capture_bridge.py | Green diagnostic screen in DirectShow virtual camera due to event handshake and buffer layout mismatch. Status: Fixed
- BUG-005 | 2026-11-17 | MainActivity.java / cambridge_receiver.py | Video stream packet mismatch: H.264 NAL packets sent to cv2.imdecode caused None return and 0 decoded frames. Status: Fixed
- BUG-006 | 2026-11-17 | cambridge_receiver.py | FFmpeg pipe partial reads and unscaled resolution prevented frame dispatch to virtual cam. Status: Fixed
- BUG-007 | 2026-11-17 | obs_virtualcam_bridge.py | Struct alignment mismatch caused interval=0 in shared memory, crashing obs-virtualcam-module64.dll with c0000094. Status: Fixed
- BUG-008 | 2026-11-17 | cambridge_receiver.py / otter_app.py | Portrait phone orientation and manual camera rotation only applied to phone preview and not PC stream. Status: Tested