# Bug Tracking

- BUG-001 | 2026-11-16 | MainActivity.java | Guarded WiFi SecurityException on Android 12+ and added permission callback. Status: Tested
- BUG-002 | 2026-11-16 | MainActivity.java | Flip crashes app due to unreleased MediaCodec/surface and improper camera facing toggle. Status: Tested
- BUG-003 | 2026-11-17 | otter_app.py | Missing ADB on machines without Android Studio causes USB tunnel failure. Status: Tested
- BUG-004 | 2026-11-17 | unity_capture_bridge.py | Green diagnostic screen in DirectShow virtual camera due to event handshake and buffer layout mismatch. Status: Tested
- BUG-005 | 2026-11-17 | MainActivity.java / cambridge_receiver.py | Video stream packet mismatch: H.264 NAL packets sent to cv2.imdecode caused None return and 0 decoded frames. Status: Tested