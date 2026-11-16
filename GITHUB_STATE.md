# GitHub State & Snapshot Ledger

- **Version**: 1.1.0.0
- **Status**: Ready for Initial Git Push & Release
- **Last Verified**: 2026-11-17 00:25:00 IST (UTC+05:30)

## Snapshot Restore Points
- **Android Module**: `Dev/android/app/src/main/java/org/understory/cambridge/MainActivity.java`
  - Camera2 pipeline + MediaCodec H.264 hardware stream + TCP video/RPC control server.
  - Multi-screen responsive layout support (phone portrait, landscape split, tablet/foldable sw600dp).
  - Hardware flashlight brightness levels (Android 13+) and front screen glow ring light.
  - Real-time Auto Focus, Manual Focus distance cycling, and EV compensation.
- **Desktop Receiver & Controller**: `Dev/desktop/otter_app.py` & `cambridge_receiver.py`
  - Cross-platform PC controller with pyvirtualcam loopback, ADB forwarder, bidirectional focus/EV/zoom sync, and dependency manager.
- **Launchers**: `run_windows.bat`, `run_linux.sh`, `run_macos.sh`, `run_macos.command`.
- **Pre-Commit Security**: `Dev/scripts/scan_secrets_and_diff.py` passed with 0 leaks.
