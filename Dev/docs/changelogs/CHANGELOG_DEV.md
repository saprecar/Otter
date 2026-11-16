# Development Changelog

## 2026-11-16 16:21:40 IST (UTC+05:30)
- Initialized tracking structure in `Dev/docs/` (requirements, features, bugs, changelogs, state).
- Formulated cross-platform architecture and project plan for F-Droid Android (7.0+) to PC (Linux, macOS, Windows) virtual camera streaming.
- Added non-root ADB, Wi-Fi, and HDMI/Capture pipeline designs with minimal UI and bidirectional control.

## 2026-11-16 16:24:00 IST (UTC+05:30)
- User confirmed Option A: Lightweight APK + Python PC Bridge (estimated 1-2 days MVP, 5-7 days F-Droid package).
- Created development roots `Dev/android`, `Dev/desktop`, and `Dev/scripts`.

## 2026-11-16 16:27:30 IST (UTC+05:30)
- Built Android Camera2 app architecture in `Dev/android/app/src/main/java/org/understory/cambridge/MainActivity.java` with hardware H.264 MediaCodec streaming and RPC control server.
- Built minimal Android layout in `Dev/android/app/src/main/res/layout/activity_main.xml` with Start, Pause, Stop, and Camera Flip controls.
- Built cross-platform desktop receiver in `Dev/desktop/cambridge_receiver.py` with automatic ADB port tunneling, pyvirtualcam virtual camera feed, and remote PC zoom/lens controls.
- Created `USER_GUIDE.md` and `GITHUB_STATE.md`.
- Ran pre-commit security scanner `Dev/scripts/scan_secrets_and_diff.py` with 0 secret leaks detected.

## 2026-11-16 23:45:00 IST (UTC+05:30)
- Fixed app immediate crash on open by wrapping `WifiManager.getConnectionInfo()` in a try-catch block to prevent `SecurityException` on Android 12+.
- Added `onRequestPermissionsResult` callback in `MainActivity.java` to initialize camera safely after user grants camera permission.
- Verified build via `compileDebugJavaWithJavac` and passed secret audit.

## 2026-11-16 23:51:50 IST (UTC+05:30)
- Fixed camera flip crash in `MainActivity.java` by targeting opposite `LENS_FACING` and safely swapping Camera2 session onto existing MediaCodec input surface without unhandled codec state crashes.
- Added live camera indicator badge (`Lens: BACK [0]` / `Lens: FRONT [1]`) and dynamic flip button state.
- Added multi-resolution toggle (1080p, 720p, 480p, 360p) with live pipeline restart.
- Enabled 360-degree all-orientation support (`screenOrientation="fullSensor"`) with `configureTransform` viewport matrix calculations.
- Added mirror flip/deflip toggle with GPU TextureView postScale transformation.
- Verified Java compilation with JBR and zero-secret audit.

## 2026-11-16 23:57:45 IST (UTC+05:30)
- Built native modern desktop controller in `Dev/desktop/otter_app.py` with multi-tab layout, connection modes, camera controls, and event log.
- Added in-app step-by-step guides for OBS Studio, Discord, Google Meet, Zoom, MS Teams, and web browsers.
- Rebranded app to "Otter" across Android and PC components; created vector icon in `Dev/android/app/src/main/res/drawable/ic_otter.xml`.
- Added MIT License in `LICENSE` with attribution to developer spacecar and repo https://github.com/saprecar/Otter.
- Re-assembled debug APK with new icon and verified zero-leak secret audit.

## 2026-11-17 00:03:30 IST (UTC+05:30)
- Built `OtterStreamService.java` ForegroundService with `camera` foregroundServiceType, ongoing notification, and `PARTIAL_WAKE_LOCK` for screen-off and locked device streaming.
- Added Lock Mode toggle (`Lock Mode: ON/OFF`) and OEM Battery Guide dialog in `MainActivity.java` with direct deep-link to battery optimization settings.
- Added comprehensive OEM anti-kill fixes for Xiaomi MIUI / HyperOS, Samsung One UI, OPPO / OnePlus ColorOS, and Vivo FuntouchOS.
- Created `Dev/desktop/manage_dependencies.py` CLI and GUI tab in `otter_app.py` for auto-install (pip), manual commands, uninstall option, and safety disclaimers.
- Re-assembled debug APK with foreground service and passed zero-secret pre-commit scan.

## 2026-11-17 00:06:00 IST (UTC+05:30)
- Added dedicated in-app window `AboutActivity.java` and `activity_about.xml` reachable from mobile header 'About' button.
- Embedded complete setup and installation instructions directly into the mobile app.
- Embedded common troubleshooting cards (USB debugging, Wi-Fi firewall, OEM battery limits) with battery optimization settings launcher.
- Included developer attribution (spacecar), official GitHub repository (https://github.com/saprecar/Otter), one-tap browser opening, clipboard copying, and MIT license notice.
- Assembled release APK and verified zero secrets.

## 2026-11-17 00:08:00 IST (UTC+05:30)
- Created cross-platform one-click desktop launcher scripts: `run_windows.bat`, `run_linux.sh`, `run_macos.sh`, and `run_macos.command`.
- Added automatic Python environment detection (checking python3, python, py launcher, and Windows local AppData).
- Added fallback instructions informing users how to install Python on Debian, Ubuntu, Fedora, Arch, and macOS if missing.
- Updated `USER_GUIDE.md` and passed zero-secret pre-commit scan.

## 2026-11-17 00:09:50 IST (UTC+05:30)
- Integrated step-by-step guides for Method A: USB Cable (Recommended for 0-latency) and Method B: Wi-Fi mode into `USER_GUIDE.md`.
- Embedded detailed connection cards into the Android mobile app's in-app guide window (`activity_about.xml`).
- Embedded connection cards into Tab 2 of the desktop controller (`otter_app.py`).
- Assembled updated debug APK and passed zero-secret pre-commit audit.

## 2026-11-17 00:12:30 IST (UTC+05:30)
- Added `<supports-screens>` in `AndroidManifest.xml` with `resizeableActivity="true"` supporting small, normal, large, and xlarge displays.
- Created `layout-land/activity_main.xml` providing side-by-side viewfinder (left) and scrollable control panel (right) for landscape phones, foldables, and tablets.
- Created `layout-sw600dp/activity_main.xml` optimized for 7-inch and 10-inch tablets with enlarged 48dp touch targets and generous padding.
- Wrapped portrait controls in a zero-scroll responsive container preventing button clipping on compact screens.
- Updated `configureTransform` viewport matrix calculations to adaptively fit varying aspect ratios without stretching.
- Assembled release APK and verified zero secrets.

## 2026-11-17 00:19:30 IST (UTC+05:30)
- Implemented hardware flashlight / torch control with low/high brightness levels (using Android 13+ `turnOnTorchWithStrengthLevel` when supported, or standard on/off fallback).
- Added auto-disable state ("Torch: N/A") when switching to lenses without flash hardware (such as front camera).
- Implemented front screen glow ring light (`screenGlowBorder`) with cycleable color temperatures (Warm, Daylight, Sunset, White) and automatic screen brightness maximization.
- Wired TCP control RPC handlers (`toggle_torch`, `toggle_glow`) in `MainActivity.java` and desktop client `cambridge_control.py`.
- Added remote torch and screen glow buttons to the desktop controller interface `otter_app.py`.
- Assembled debug APK and verified zero secrets.

## 2026-11-17 00:24:00 IST (UTC+05:30)
- Implemented real-time Auto Focus (AF) and Manual Focus (MF) controls with Camera2 `CONTROL_AF_MODE_CONTINUOUS_PICTURE`, `CONTROL_AF_MODE_OFF`, and `LENS_FOCUS_DISTANCE` from infinity to macro.
- Implemented Exposure Compensation (EV) stepping using `CONTROL_AE_EXPOSURE_COMPENSATION` and `CONTROL_AE_COMPENSATION_STEP`.
- Added AF/MF/EV buttons to phone UI (`activity_main.xml`, `layout-land`, `layout-sw600dp`).
- Extended TCP RPC protocol with `toggle_af`, `set_focus`, `cycle_focus`, `cycle_exposure`, and `set_exposure`.
- Added Desktop UI controls (`btn_af`, `btn_focus_dist`, `btn_ev`, `btn_sync_status`) with background polling loop syncing lens, zoom, AF/MF, EV, mirror, and glow state in real-time.
- Assembled updated debug APK and passed zero-secret pre-commit verification.

## 2026-11-17 00:25:30 IST (UTC+05:30)
- Implemented software camera rotation controls allowing users to rotate the camera feed in 90-degree increments (0°, 90°, 180°, 270°).
- Enabled support for inverted phone placement, monitor mounts, laptop bezel mounts, and down-to-up camera angles.
- Added software matrix rotation (`matrix.postRotate(manualRotationAngle, centerX, centerY)`) in `MainActivity.java` `configureTransform`.
- Added Rotate button to mobile layouts (`activity_main.xml`, `layout-land`, `layout-sw600dp`).
- Extended TCP RPC protocol with `rotate_camera` and `set_rotation` actions, including `rotationAngle` in `get_status`.
- Added remote camera rotation button (`Rotate: 0°`) and RPC handling to desktop app (`otter_app.py`, `cambridge_control.py`).
- Assembled updated debug APK and passed pre-commit zero-secret leak scan.

## 2026-11-17 00:27:30 IST (UTC+05:30)
- Implemented standalone ADB & Platform Tools manager (`Dev/desktop/manage_adb.py`) that downloads official lightweight Google platform-tools (~15MB) into Otter's portable directory so users do not need Android Studio.
- Updated `adb_tunnel.py` to auto-detect portable minimal platform-tools before falling back to system PATH or Android Studio SDK.
- Added ADB management GUI card into Tab 3 of `otter_app.py` with real-time detection, one-click download, and removal options.
- Added auto-prompt on connecting via USB mode when ADB is missing, offering to download Google's minimal tool automatically.
- Added special thanks and acknowledgements to the Google Android Platform Tools (ADB) team, spacecar, and open-source contributors across both Android app (`activity_about.xml`) and Desktop controller (`otter_app.py`).
- Assembled updated debug APK and passed zero-secret pre-commit verification.






## 2026-11-17 02:10:00 IST (UTC+05:30)
- Implemented native OBS Virtual Camera shared memory fallback bridge (`Dev/desktop/driver/obs_virtualcam_bridge.py`) writing directly to `OBSVirtualCamVideo` IPC ring buffer in NV12 format.
- Resolved UnityCapture DirectShow green diagnostic screen bug (`Dev/desktop/driver/unity_capture_bridge.py`) by correcting row stride from byte pitch to pixel width (`stride = w`), converting frames to true RGBA (`FORMAT_UINT8 = 0`), and setting persist timeout.
- Enabled dual-output in `cambridge_receiver.py` so incoming Android frames broadcast simultaneously to both 'Unity Video Capture' and 'OBS Virtual Camera' without driver conflicts.
- Updated documentation and in-app instructions (`USER_GUIDE.md`, `otter_app.py`) to guide users on selecting either virtual device.

## 2026-11-17 02:26:00 IST (UTC+05:30)
- Fixed video stream decode mismatch in `cambridge_receiver.py`: Integrated `H264DecoderPipe` powered by standalone static `imageio-ffmpeg` to decode Android MediaCodec H.264 NAL packets in real-time, resolving the issue where `cv2.imdecode` returned `None` on video packets.
- Maintained compatibility for both H.264 stream slices and standard JPEG frames with auto-detection.
- Added Android 14+ Native USB Webcam control card and ADB trigger (`svc usb setFunctions uvc`) in Tab 3 of `otter_app.py` for Google Pixel, Motorola, and supported devices.
- Added graceful OEM detection informing users when manufacturers (such as Vivo/iQOO) have stripped native UVC kernel drivers, automatically utilizing Otter's high-speed ADB tunnel instead.
- Updated `requirements.txt` and `manage_dependencies.py` to include `imageio-ffmpeg`.
