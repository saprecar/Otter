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

## 2026-11-17 02:51:30 IST (UTC+05:30)
- Fixed H.264 stream decoding and size mismatch in `cambridge_receiver.py`:
  - Added `-vf scale={width}:{height}` to FFmpeg pipeline to guarantee exact output dimensions matching the PC virtual camera canvas regardless of phone sensor aspect ratio or orientation.
  - Replaced partial `pipe.read()` with an exact byte-accumulation loop (`_read_exact`) ensuring zero dropped chunks and continuous full-frame decoding.
  - Set `stderr=None` in subprocess call to surface any FFmpeg warnings and stream diagnostics directly in the console.
  - Implemented real-time `on_frame` direct dispatching to both `Unity Video Capture` and `OBS Virtual Camera` with live dispatch logging.

## 2026-11-17 02:58:30 IST (UTC+05:30)
- Fixed `c0000094` divide-by-zero crash in `obs-virtualcam-module64.dll`:
  - Replaced manual `struct.pack` in `obs_virtualcam_bridge.py` with native C `QueueHeader` ctypes structure matching MSVC 64-bit alignment.
  - Fixed 4-byte padding offset before `uint64_t interval`, ensuring `interval` is placed at offset 40 (`333333` for 30 FPS) instead of offset 36. This prevents `obs-virtualcam-module64.dll` from reading `interval = 0` during DirectShow device enumeration.
  - Set queue header `state = SHARED_QUEUE_STATE_STOPPING` on receiver termination to cleanly detach shared memory.

## 2026-11-17 03:15:00 IST (UTC+05:30)
- Fixed portrait orientation mismatch and bidirectional stream rotation synchronization:
  - Added live rotation angle (`rotation_angle`) and `set_rotation(angle)` to `CamBridgeReceiver` with OpenCV lossless rotation (`cv2.ROTATE_90_CLOCKWISE`, `ROTATE_180`, `ROTATE_90_COUNTERCLOCKWISE`).
  - Added aspect-ratio preserving pillarboxing for portrait mode so 90°/270° orientation is centered on standard 16:9 1280x720 canvas with zero geometric distortion.
  - Implemented background thread (`_sync_device_rotation`) continuously querying Android device rotation angle via control RPC.
  - Added remote `start_stream` and `stop_stream` control RPC actions in `MainActivity.java` and desktop client.
  - Fixed camera flip freeze by properly calling `stopEncoder()` and reinitializing MediaCodec input surfaces on Camera2 lens switches.
  - Installed updated APK on connected device (`10BCA5153U000ER`) and verified live stream decoding, rotation sync, and virtual camera frame dispatch.

## 2026-11-17 03:26:00 IST (UTC+05:30)
- Implemented comprehensive Android UI overhaul and Pro Camera engine:
  - Rebuilt Android UI across phone portrait (`layout/activity_main.xml`), landscape (`layout-land/`), and tablet (`layout-sw600dp/`) using modern dark glassmorphic design (`#0D1117` / `#161B22` / `#21262D`).
  - Added live overlay badges on viewfinder: `● Live` pill, resolution badge, and FPS badge.
  - Added floating on-screen zoom controls (`[ + ]`, `[ - ]`, `1.0x`) and smooth two-finger pinch-to-zoom on the live viewfinder TextureView.
  - Added dedicated Exposure Compensation stepper buttons (`[ EV - ]`, `[ EV + ]`) with real-time SeekBar and EV readout.
  - Implemented Pro Manual Camera Mode: ISO selector (`Auto`, `100` to `3200`), Shutter Speed selector (`Auto`, `1/1000s` to `1/30s`), White Balance (`Auto`, `Daylight`, `Cloudy`, `Fluorescent`, `Tungsten`), and Color Effects (Color, B&W Mono, Negative, Sepia).
  - Implemented dynamic hardware capability detection querying `StreamConfigurationMap` for resolutions up to 4K (`3840x2160`) and sensor FPS ranges up to 60 FPS.
  - Implemented 8 Quick Mode presets: Meetings, Online Class, Streaming, Snapshot, Scan/OCR, Security, Fun Filter, and Pro Manual.
  - Implemented Ultra Photo pipeline using full-sensor `ImageReader` capturing maximum resolution uncompressed JPEG (64MP/48MP/16MP).
  - Added Fullscreen mode with collapsible floating action menu (`⚡`) matching reference design.
  - Extended TCP RPC control server with `get_capabilities`, `set_zoom`, `ev_step`, `set_iso`, `set_shutter`, `set_awb`, `set_effect`, `set_fps`, `set_quick_mode`, and `capture_still`.
  - Compiled debug APK via Gradle with zero errors (778 KB binary).


## 2026-11-17 09:11:30 IST (UTC+05:30)
- Redesigned PC desktop controller in `Dev/desktop/otter_app.py` with modern scrollable dark layout, Quick Modes grid, and pro camera controls.
- Added PC sliders for Zoom (1.0x-8.0x) with +/- buttons, and discrete sliders for ISO (100-3200), Shutter Speed (1/2000s-1/15s), White Balance (Daylight/Cloudy/Fluorescent/Tungsten), and Color FX (Mono/Negative/Sepia).
- Implemented Auto toggle interlocks on PC: enabling Auto locks slider to disabled and sends auto command; disabling Auto unlocks slider for fine manual adjustment.
- Added OpenCamera-style sensor orientation math (`sensorOrientation - deviceOrientation`) via `OrientationEventListener` in `MainActivity.java` so camera preview and PC stream stay upright in both portrait and landscape.
- Fixed landscape UI bug by setting `screenOrientation="portrait"` on `MainActivity`, preserving the clean portrait layout while allowing the camera sensor to adapt to landscape holding.
- Added comprehensive PC Desktop Client download and run instructions card with one-click clipboard copying to `AboutActivity.java` and `activity_about.xml`.

## 2026-11-17 09:36:30 IST (UTC+05:30)
- Created isolated stable release folders under `Stable/`: `Stable_Desktop_Client/` and `Stable_android_app/`.
- Configured desktop client launcher scripts (`run_windows.bat`, `run_linux.sh`, `run_macos.command`, `run_macos.sh`) to execute with `Stable_Desktop_Client` as the root directory, ensuring local imports resolve correctly across all platforms.
- Packaged clean Android source tree into `Stable/Stable_android_app/` with `versionCode 2` and `versionName "1.1.0.0"`.
- Compiled and packaged pre-built signed release APK `Otter-v1.1.0.0.apk` (618 KB) into `Stable/Stable_android_app/`.
- Cleaned intermediate build artifacts and cache directories (`build/`, `.gradle/`, `__pycache__/`) from both stable directories.
- Removed `Stable/` from `.gitignore` to allow full tracking and uploading of stable release deliverables to GitHub.
- Created `Stable/README.md`, `Stable/Stable_android_app/README.md`, and official release changelog `stable_release/CHANGELOG_STABLE.md`.

## 2026-11-17 09:43:00 IST (UTC+05:30)
- Separated stable releases into dedicated distribution packages: `Stable/stable_playstore_version/` and `Stable/stable_non_playstore_version/`.
- Authored comprehensive Privacy Policy (`docs/PRIVACY_POLICY.md` & `privacy_policy.html`) and User Agreement (`docs/USER_AGREEMENT.md` & `user_agreement.html`) governed by the Laws of the Republic of India (IT Act 2000, Section 43A, SPDI Rules 2011).
- Incorporated mandatory legal disclaimers: zero developer data collection, 100% peer-to-peer local processing, disclosure of OS-level Google Play analytics, absolute disclaimer of warranties (AS-IS), and complete limitation of liability for data leakage, software bugs, and third-party network risks.
- Added in-app Privacy Policy and User Agreement triggers and visual card to `AboutActivity.java` and `activity_about.xml`.
- Generated Google Play Console Data Safety questionnaire guide (`docs/GOOGLE_PLAY_DATA_SAFETY.md`).
- Built production Android App Bundle `Otter-v1.1.0.0.aab` (625 KB) in `stable_playstore_version/`.
- Built pre-signed release APK `Otter-v1.1.0.0-signed.apk` (619 KB) and unsigned APK `Otter-v1.1.0.0-unsigned.apk` (611 KB) in `stable_non_playstore_version/`.

## 2026-11-17 09:47:00 IST (UTC+05:30)
- Completed comprehensive brand audit across all workspace files, documentation, scripts, and source trees for "DroidCam", "dev47apps", "Iriun", "EpocCam", "iVCam", and related third-party brand names.
- Confirmed zero occurrences across all codebases and documentation; all terminology is strictly generic ("virtual webcam", "remote camera", "video streaming tool").
- Respected build constraints: zero APK builds generated.

## 2026-11-17 09:51:00 IST (UTC+05:30)
- Implemented first-time start and per-update mandatory consent enforcement on both Android and PC:
  - Android (`MainActivity.java`): Added `checkAndEnforceConsent()` evaluating stored `accepted_policy_version` against `POLICY_VERSION`. Displays non-dismissible modal agreement outlining zero developer data collection, local P2P architecture, OS-level telemetry disclosure, and Indian Law jurisdiction. "Accept & Continue" saves agreement state; "Decline & Exit" calls `finishAffinity()` terminating app.
  - Desktop Client (`otter_app.py`): Added `_check_consent_policy()` checking `~/.otter_consent.json`. Displays modal dialog blocking user interaction until acceptance. "I Agree & Continue" persists version consent; "Decline & Exit" terminates client.
  - Online Policy Links: Replaced all hardcoded policy texts with dynamic external browser links to GitHub-hosted `PRIVACY_POLICY.md`, `USER_AGREEMENT.md`, and `LICENSE` across `AboutActivity.java`, `activity_about.xml`, `otter_app.py`, and consent dialogs.
  - Synchronized changes across `Dev/`, `Stable/stable_playstore_version/`, `Stable/stable_non_playstore_version/`, and `Stable/Stable_Desktop_Client/`.
  - Respected user constraint: zero APK builds generated.

## 2026-11-17 10:15:30 IST (UTC+05:30)
- Consolidated all separate legal policies into universal `Policies And Agreement/` directory containing pure Markdown documentation (`POLICIES_AND_AGREEMENT.md`, `ATTRIBUTION_AND_LICENSES.md`, `PRIVACY_POLICY.md`, `USER_AGREEMENT.md`, `GOOGLE_PLAY_DATA_SAFETY.md`, `README.md`). Removed all temporary HTML policy files.
- Updated legal jurisdiction across all documents, in-app screens, and desktop controller to the Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).
- Added explicit legal clauses: zero developer data retention (making server deletion inapplicable), zero liability for local network data transmission/interception/packet loss, and clear OEM/Google Play platform telemetry disclaimers.
- Added mandatory attribution clause requiring all redistributions, forks, or derivations to credit developer `spacecar`, name `Otter`, and link to `https://github.com/saprecar/Otter`.
- Updated contact protocol to `getspacecar@gmail.com` with mandatory subject line tags (`[Otter-Legal]`, `[Otter-Inquiry]`) or official GitHub issues.
- Updated Android app (`MainActivity.java`, `AboutActivity.java`, `activity_about.xml`) and PC desktop client (`otter_app.py`) so consent dialogs and About screens link directly to the consolidated policy.
- Verified syntax with `py_compile` and `compileDebugJavaWithJavac`. Respected build constraints: zero APK builds generated.
