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

## 2026-11-17 11:25:00 IST (UTC+05:30)
- Implemented Dual-Execution Virtual Background and AI Workload Routing engine:
  - Added `VirtualBackgroundProcessor` in `Dev/desktop/cambridge_receiver.py` supporting: Off/Pass-Through, Custom Image Background, Light Bokeh Blur, Heavy Privacy Blur, and Green Screen Chroma Keying.
  - Added workload routing selector allowing users to choose between PC GPU/CPU Offload (preserves phone thermals and battery life during long 1080p/60fps streams) and On-Device Mobile processing.
  - Integrated image caching, dynamic resolution scaling, and automatic MediaPipe Selfie Segmentation detection with seamless pure OpenCV fallback.
  - Updated Desktop Controller (`otter_app.py`) with workload radio options, background mode dropdown, and custom image file browser.
  - Updated TCP RPC protocol (`cambridge_control.py`, `MainActivity.java`) with `set_background_mode` and status synchronization.
- Implemented User-Selectable Screen Wake & Power Management:
  - Added Keep Screen On user toggle (`FLAG_KEEP_SCREEN_ON`) in Android app (`MainActivity.java`, `activity_main.xml`) allowing users to choose between keeping the display awake or allowing standard device sleep to conserve battery.
  - Added display dimming mode (`btnScreenDim`) reducing screen backlight brightness to minimum during streams to save power and prevent OLED burn-in.
  - Persisted user preference in `otter_settings` SharedPreferences across app relaunches.
  - Added remote screen wake toggle to PC Desktop client (`otter_app.py`, `cambridge_control.py`) with bidirectional status sync.
- Created comprehensive master GitHub Guidebook (`GUIDEBOOK.md`) covering architecture, USB/Wi-Fi/UVC setup, virtual background routing, Pro optics, virtual camera bridges, OEM anti-kill, and legal compliance.
- Updated UI layouts and operational documentation in `USER_GUIDE.md`.
- Synchronized changes to `Stable/Stable_Desktop_Client/`, `Stable/stable_playstore_version/`, and `Stable/stable_non_playstore_version/`.
- Verified syntax with `py_compile` and `compileDebugJavaWithJavac` across all modules. Respected build constraints: zero APK builds generated.

## 2026-11-17 11:35:00 IST (UTC+05:30)
- Upgraded Android build targets to Android 16 (API Level 36):
  - Updated `compileSdk` to 36 and `targetSdk` to 36 across `Dev/android` and all `Stable/` projects (`stable_playstore_version`, `stable_non_playstore_version`).
  - Added `android.suppressUnsupportedCompileSdk=35,36` to `gradle.properties`.
  - Installed Android SDK Platform 36 and verified compilation with `compileDebugJavaWithJavac` (BUILD SUCCESSFUL, 0 errors, 0 APKs generated).
- Google Play Store Compliance & Policy Corrections:
  - Corrected Data Safety questionnaire (`GOOGLE_PLAY_DATA_SAFETY.md`): declared "Encrypted in transit: No" reflecting truthful local raw TCP socket streaming without application-layer TLS certificate encapsulation.
  - Corrected statutory citation in `POLICIES_AND_AGREEMENT.md`: specifically cited Section 66E (Violation of Privacy) for clandestine recording/surveillance, and Section 67 for transmitting obscene material under the Indian IT Act, 2000.
  - Removed restricted permission `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` from `AndroidManifest.xml` across all versions to eliminate risk of Play Store policy rejection, retaining clean in-app guidance via standard settings intents.
  - Explicitly documented internal package identifier `org.understory.cambridge` alongside public application display name `Otter`.

## 2026-11-17 12:10:00 IST (UTC+05:30)
- Generated Google Play Store listing metadata and visual assets:
  - High-resolution 512x512 PNG app icon (`playstore_icon_512x512.png`).
  - 1024x500 Feature Graphic in PNG and JPEG formats (`playstore_feature_graphic_1024x500.png`, `playstore_feature_graphic_1024x500.jpg`).
  - Multi-language translation file (`store_listing_translations.csv`) and master listing specification (`STORE_LISTING.md`) covering English (`en-US`), Hindi (`hi-IN`), and Spanish (`es-ES`) verified within Google Play Console character bounds.
  - Authored tablet screenshot generation engine (`Dev/scripts/generate_tablet_screenshots.py`) and generated eight 10-inch tablet screenshots in 16:9 landscape aspect ratio (1920x1080, < 8 MB each) complying with Google Play Console specifications:
    1. 1080p 60 FPS Ultra-Low Latency Streaming (`playstore_tablet_10inch_screenshot_1.png`)
    2. Pro Manual Optics & Camera2 Controls (`playstore_tablet_10inch_screenshot_2.png`)
    3. Dual Virtual Background Engine with PC GPU Offload (`playstore_tablet_10inch_screenshot_3.png`)
    4. 8 One-Touch Purpose Presets (`playstore_tablet_10inch_screenshot_4.png`)
    5. Smart Power & Battery Protection with Screen Keep-ON & Dimming (`playstore_tablet_10inch_screenshot_5.png`)
    6. 100% Private Zero-Cloud Architecture (`playstore_tablet_10inch_screenshot_6.png`)
    7. Multi-Lens Switching & 4K Ultra Photo (`playstore_tablet_10inch_screenshot_7.png`)
    8. Universal Compatibility for OBS Studio, Zoom, and Teams (`playstore_tablet_10inch_screenshot_8.png`)
  - Mirrored all Play Store visual assets to `Stable/stable_playstore_version/` and `Dev/android/app/src/main/`.

## 2026-11-17 13:28:00 IST (UTC+05:30)
- Integrated visual showcase into GitHub repository documentation:
  - Updated root `README.md` with centered 512x512 app icon, full-width 1024x500 Feature Graphic banner, and a 2-column visual gallery presenting all eight 10-inch tablet screenshots with descriptive titles.
  - Embedded high-resolution diagrams and feature screenshots into `GUIDEBOOK.md` across Architecture Overview, Virtual Background Engine, Screen Wake & Power Management, Pro Manual Optics, and Quick Presets sections.
  - Sanitized UI layout blocks in `USER_GUIDE.md`, replacing non-standard unicode symbols with clean ASCII characters to enforce strict zero-emoji compliance.
  - Verified layout rendering and relative image paths across GitHub markdown viewers.

## 2026-11-17 14:10:00 IST (UTC+05:30)
- Upgraded `minSdkVersion` to 24 (Android 7.0 Nougat) for Google Play Automatic Protection compliance:
  - Updated `minSdk 24` across all Gradle build configurations (`Dev/android/app/build.gradle`, `Stable/stable_playstore_version/app/build.gradle`, and `Stable/stable_non_playstore_version/app/build.gradle`).
  - Re-packaged Android App Bundle (`app-release.aab`) in `Stable/stable_playstore_version` via `gradlew bundleRelease` (BUILD SUCCESSFUL, zero errors).
  - Updated `Stable/stable_playstore_version/Otter-v1.1.0.0.aab`.
  - Verified `minSdkVersion 24` inside bundle AndroidManifest.
  - Respected build constraints: zero APKs generated.

## 2026-11-17 14:15:00 IST (UTC+05:30)
- Created F-Droid & IzzyOnDroid distribution metadata and submission guide:
  - Authored official F-Droid build recipe specification (`Stable/stable_non_playstore_version/org.understory.cambridge.yml`).
  - Created step-by-step submission guide (`Stable/stable_non_playstore_version/FDROID_SUBMISSION_GUIDE.md`) detailing F-Droid source-build Merge Requests, IzzyOnDroid direct APK release indexing, and self-hosted F-Droid repository setup via GitHub Pages.
  - Updated documentation across `Stable/README.md` and `Stable/stable_non_playstore_version/README.md`.

## 2026-11-17 14:35:00 IST (UTC+05:30)
- Configured Fastlane metadata and dual F-Droid & IzzyOnDroid submission suite:
  - Scaffolding Fastlane metadata structure (`fastlane/metadata/android/en-US/`) with localized `title.txt`, `short_description.txt`, `full_description.txt`, and full visual assets (`icon.png`, `featureGraphic.png`, and eight 10-inch tablet screenshots) for automatic ingestion by F-Droid and IzzyOnDroid servers.
  - Enhanced F-Droid build recipe (`org.understory.cambridge.yml`) with automated version checking (`AutoUpdateMode: Version`, `UpdateCheckMode: Tags`).
  - Updated `FDROID_SUBMISSION_GUIDE.md` with complete copy-paste templates for GitHub Releases, IzzyOnDroid GitLab inclusion issues, and official F-Droid Merge Requests.

## 2026-11-17 14:55:00 IST (UTC+05:30)
- Virtual Background Wallpaper Specifications & Sample Wallpapers:
  - Generated four 1920x1080 (16:9) high-definition sample wallpapers in `Dev/desktop/wallpapers/` and `Stable/Stable_Desktop_Client/wallpapers/` (`modern_office.jpg`, `studio_bokeh.jpg`, `minimalist_bookshelf.jpg`, `cozy_coffee_shop.jpg`).
  - Updated Desktop Controller (`otter_app.py`) file dialog and info labels with clear wallpaper sizing specifications: 16:9 aspect ratio (1920x1080 FHD / 1280x720 HD), PNG/JPG/WEBP formats (<15MB), with automatic aspect-preserving scaling.
  - Added comprehensive wallpaper specification section in `GUIDEBOOK.md` and `USER_GUIDE.md`.
- Live Camera Streaming Notification:
  - Enhanced `OtterStreamService.java` to show a persistent ongoing notification (`Otter Camera: LIVE`) while streaming is active, displaying live port (8089), resolution, "Camera in use" subtext, and a native `[Stop Stream]` action button.
  - Updated `MainActivity.java` to start the foreground notification unconditionally whenever streaming is active, dynamically update notification status on pause/resume, and cleanly process `ACTION_STOP_STREAM` from the notification shade.
  - Added runtime `POST_NOTIFICATIONS` permission check for Android 13+ (API 33+) devices.
  - Re-bundled `Otter-v1.1.0.0.aab` and verified compilation with zero errors across all modules. Respected build constraints: zero APKs generated.

## 2026-11-17 15:05:00 IST (UTC+05:30)
- Android Version Bump for Play Console Submission Compliance:
  - Incremented `versionCode` to `4` (even number for stable release per Rule 13) and `versionName` to `"1.2.0.0"` in `Stable/stable_playstore_version/app/build.gradle` and `Stable/stable_non_playstore_version/app/build.gradle`.
  - Incremented `versionCode` to `3` (odd number for dev build) and `versionName` to `"1.2.0.1"` in `Dev/android/app/build.gradle`.
  - Re-packaged Google Play App Bundle `Otter-v1.2.0.0.aab` via `gradlew bundleRelease` (BUILD SUCCESSFUL in 18s).
  - Verified `base/manifest/AndroidManifest.xml` inside bundle confirms `versionCode 4`, `versionName 1.2.0.0`, and `minSdkVersion 24`.
  - Updated F-Droid build recipe `org.understory.cambridge.yml`, `FDROID_SUBMISSION_GUIDE.md`, and `output-metadata.json`. Respected build constraints: zero APKs generated.

## 2026-11-18 16:24:00 IST (UTC+05:30)
- Cross-Platform Launcher Resilience & Self-Bootstrapping (.venv):
  - Overhauled `run_linux.sh`, `run_macos.sh`, `run_macos.command`, and `run_windows.bat` with automated `.venv` creation and dependency installation.
  - Eliminated PEP 668 `externally-managed-environment` failures on Ubuntu 24.04+, Debian 12+, Arch, and macOS Homebrew.
  - Added explicit Tkinter pre-flight diagnostics with exact 1-line installation commands (`sudo apt install python3-tk`, `brew install python-tk`) and terminal pause on failure.
  - Added fallback `--break-system-packages` and `--user` retry logic in `manage_dependencies.py`.
- Automated Cross-Platform Test Suite & GitHub Actions CI Matrix:
  - Authored `Dev/scripts/test_cross_platform.py` validating syntax compilation, LF line endings, mock Linux (`sys.platform = 'linux'`), mock macOS (`sys.platform = 'darwin'`), and tethering IP detection directly on Windows host.
  - Configured GitHub Actions CI workflow `.github/workflows/desktop_cross_platform.yml` executing tests across `ubuntu-latest`, `macos-latest`, and `windows-latest` VMs.
- ADB-Free USB Tethering Connection Mode:
  - Added native USB Tethering connection mode in `otter_app.py` connecting directly over high-speed USB cable to Android default tethering gateway (`192.168.42.129:8089`) with zero ADB and zero Developer Options required.
  - Enhanced `network_discovery.py` to probe USB tethering subnets (`192.168.42.129`, `192.168.43.1`) during auto-detection.
  - Updated `MainActivity.java` across all packages to detect active USB tethering interfaces (`rndis0`, `usb0`), display `USB Tether: <ip> | Port: 8089`, and provide `openTetheringSettings()` shortcut. Respected build constraints: zero APKs generated.

## 2026-11-18 16:29:00 IST (UTC+05:30)
- Android 5.0 (API Level 21, Lollipop) Support for F-Droid / Non-Play Store Distribution:
  - Lowered `minSdkVersion` to `21` in `Stable/stable_non_playstore_version/app/build.gradle` and `Dev/android/app/build.gradle` to restore legacy device compatibility back to Android 5.0 Lollipop.
  - Preserved `minSdkVersion 24` in `Stable/stable_playstore_version/app/build.gradle` without any changes, maintaining Google Play Automatic Protection compliance.
  - Verified compilation via `compileDebugJavaWithJavac` (BUILD SUCCESSFUL in 54s, zero errors).
  - Updated `output-metadata.json`, `FDROID_SUBMISSION_GUIDE.md`, and `Stable/README.md`. Respected build constraints: zero APKs generated.

## 2026-11-18 16:55:00 IST (UTC+05:30)
- Mobile & Desktop Virtual Background & Green Screen Selection Suite:
  - Added full gallery image picker (`ACTION_GET_CONTENT`) and wallpaper selection dialog to Android mobile app across `Dev/android`, `Stable/stable_playstore_version`, and `Stable/stable_non_playstore_version`.
  - Added background effect options: Light Bokeh Portrait Blur, Heavy Privacy Blur, Solid Green Screen (Chroma Key RGB 0, 255, 0), and four 1080p preset wallpapers (Modern Office, Studio Bokeh, Minimalist Bookshelf, Cozy Coffee Shop).
  - Added Quick Effects toolbar and Preset BG selector in Desktop Client (`otter_app.py`) and solid green screen rendering in `cambridge_receiver.py`.
  - Added in-dialog wallpaper specifications guide detailing 16:9 aspect ratio, 1920x1080 FHD / 1280x720 HD resolutions, formats (PNG, JPG, WEBP <15MB), and PC offload benefits.
  - Verified syntax compilation across all Android packages via `compileDebugJavaWithJavac` (BUILD SUCCESSFUL, zero errors) and desktop cross-platform test suite (`test_cross_platform.py`, 5/5 passed). Respected build constraints: zero APKs generated.

## 2026-11-18 17:15:00 IST (UTC+05:30)
- High-Resolution Quad-Bayer Sensor Detection & Ultra Photo Upgrades:
  - Resolved Poco F6 / iQOO Z7 resolution confusion by detecting hardware physical sensor megapixels (`SENSOR_INFO_PIXEL_ARRAY_SIZE`) alongside ISP pixel-binning modes (e.g. 64MP sensor binned to 16MP / 50MP sensor binned to 12.5MP-13MP).
  - Added Android 12+ (API 31+) `SCALER_STREAM_CONFIGURATION_MAP_MAXIMUM_RESOLUTION` auto-upgrade and `SENSOR_PIXEL_MODE_MAXIMUM_RESOLUTION` for full unbinned remosaic capture where supported.
  - Dynamically updated Ultra Photo button label to show sensor capability: `★ Ultra (64MP Full)` or `★ Ultra (64MP/16MP Bin)`.
- 60 FPS Range Negotiation & MediaCodec Encoder Adaptation:
  - Added `getBestFpsRange()` inspecting `CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES` to negotiate exact fixed `[60, 60]` or flexible `[30, 60]` ranges supported by OEM camera HALs.
  - Configured MediaCodec H.264 encoder with dynamic bitrate boosting (`8 Mbps` for 1080p60, `5 Mbps` for 720p60) and runtime encoder reconfiguration on FPS change.
- User-Selectable Foreground Service & Notification Toggle:
  - Added `isForegroundServiceEnabled` toggle to `MainActivity.java` and UI layout (`activity_main.xml`).
  - Users can now toggle Foreground Service ON (active ongoing notification and wake lock for continuous streaming with screen off) or OFF (streaming strictly in foreground with zero ongoing notification drawer presence).
  - Verified compilation via `compileDebugJavaWithJavac` across Dev, Play Store, and F-Droid variants (BUILD SUCCESSFUL, zero errors). Respected build constraints: zero APKs generated.

## 2026-11-18 18:10:00 IST (UTC+05:30)
- Fixed Green Screen on ADB and USB Tethering Connections:
  - Root cause: Session targets in `MainActivity.java` previously included a 50MP/64MP high-resolution `ImageReader` surface alongside preview and record surfaces, exceeding hardware stream combination limits on OEM devices (e.g. Poco F6, Xiaomi, Samsung) and causing `createCaptureSession` to fail with `onConfigureFailed`.
  - Fix: Decoupled still image capture targets from streaming capture session, isolating `targets` strictly to `previewSurface` and `encoderInputSurface` as in Release 1.
  - Added `MediaFormat.KEY_PREPEND_HEADER_TO_SYNC_FRAMES` on API 29+ to prepend SPS/PPS NAL units to all sync frames.
  - Implemented `requestSyncFrame()` triggering `MediaCodec.PARAMETER_KEY_REQUEST_SYNC_FRAME` immediately upon client socket accept, ensuring instant IDR frame delivery without green screen buffer lag.
- Fixed Connection Mode Status Display on Android:
  - Phone stream status text dynamically inspects client remote address upon connection: `127.0.0.1` -> `ADB USB Tunnel | Port: 8089`, `192.168.42.x` / `192.168.43.x` -> `USB Tether: <ip> | Port: 8089`, and LAN IP -> `Wi-Fi IP: <ip> | Port: 8089`.
  - Added `set_connection_mode` RPC command allowing desktop client to inform mobile app of the selected transport mode upon connection.
- Fixed App Settings Version Number:
  - Replaced hardcoded `Otter (v1.0.0.1)` in `activity_about.xml` with dynamic runtime lookup via `PackageManager.getPackageInfo(getPackageName(), 0)` in `AboutActivity.java`.
  - Bumped version standard to `1.3.0.0` (versionCode `6` for Stable / Dev).
- Fixed ADB & UVC Desktop Client Methods:
  - Resolved `AttributeError: 'ADBTunnel' object has no attribute 'adb_cmd'` in `otter_app.py` by referencing `tunnel.adb_bin`.
  - Probed control port (8090) during auto-discovery in `network_discovery.py` to prevent probe sockets from disconnecting active video streams.
  - Verified compilation across `Dev/android`, `Stable/stable_playstore_version`, and `Stable/stable_non_playstore_version` (BUILD SUCCESSFUL across all 3, zero errors). Respected build constraints: zero APKs generated.

## 2026-11-18 23:36:00 IST (UTC+05:30)
- USB / Wi-Fi Auto Switching & Connection Resilience Suite:
  - `Dev/desktop/adb_tunnel.py`: Added `usb_serial()` returning first authorized USB device, `_adb_prefix()` for targeting specific serials, `clear_forward()` to remove stale forwards before binding (`forward --remove tcp:<port>`), and upgraded `setup_forward()` to clear forwards first and return `bool` with captured error diagnostics.
  - `Dev/desktop/cambridge_receiver.py`: Added `self.reforward_cb = None` to `CamBridgeReceiver`. Implemented `_connect_with_retry()` automatically executing `reforward_cb()` before each retry attempt and providing clear timeout diagnostics. Added `--mode auto` (default) which tries USB (ADB tunnel) first and automatically falls back to Wi-Fi.
  - `Dev/desktop/otter_app.py`: Added "Auto (USB -> Wi-Fi)" radio button option (default mode). In `start_stream()`, automatically probes for USB devices via `usb_serial()`; if detected, sets up ADB forwarding and connects over `127.0.0.1` with retry callback; if no USB device is connected or forward fails, seamlessly falls back to Wi-Fi. Updated `_get_active_host()` to track real resolved transport host. Sends `start_stream` and `stop_stream` control commands to Android app to coordinate remote streaming.
  - `Dev/android/.../MainActivity.java`: Added `setReuseAddress(true)` to `videoServerSocket` and `controlServerSocket` to prevent "address already in use" errors on reconnects. Added stale client teardown (`if (activeVideoClient != null) activeVideoClient.close()`) before accepting a new client socket. Added robust IPv6/loopback address detection (`addr.isLoopbackAddress()` or contains `127.0.0.1` -> `adb`, `192.168.42.x` / `192.168.43.x` -> `usb_tether`, otherwise `wifi`). Implemented auto-stop on disconnection: if client socket closes or broken pipe occurs during streaming, Android automatically calls `stopStreaming()` and resets status to prevent hardware stress and battery drain.
  - Synchronized changes across `Dev/`, `Stable/stable_playstore_version/`, `Stable/stable_non_playstore_version/`, and `Stable/Stable_Desktop_Client/`.
  - Re-archived `Stable/Stable_Desktop_Client v1.3.0.0.zip`.
  - Verified compilation across all 3 Android targets (`gradlew.bat compileDebugJavaWithJavac`, BUILD SUCCESSFUL across all, 0 errors).
  - Cross-platform test suite (`test_cross_platform.py`) 5/5 PASSED.
  - Zero secrets detected (`scan_secrets_and_diff.py`). Respected build constraints: zero APKs generated.

## 2026-11-18 23:58:00 IST (UTC+05:30)
- Desktop UI Redesign - Material Design 3 Inspired Control Panel:
  - Redesigned `Dev/desktop/otter_app.py` and `Stable/Stable_Desktop_Client/otter_app.py` into a modern, compact, single-window Material Design 3 control panel based on the reference UI specification without multi-tab scrolling.
  - Implemented custom `MaterialSwitch` (pill track with toggle thumb) for hardware toggles (ISO, Shutter, White Balance, Color FX, Torch, Front Glow, Screen Keep ON).
  - Implemented `SegmentedControl` for transport modes (`Auto`, `USB Tethering`, `ADB USB Tunnel`, `Wi-Fi LAN IP`) and camera lens selection (`Front`, `Rear`) with non-recursive notification guards (`notify=False`).
  - Implemented `CardFrame` dark surface cards (`#161B22`, border `#263040`) in a responsive grid:
    - Header: Otter branding, avatar badge, persistent connection status indicator (`Disconnected` / `Active: <name>`).
    - Connection Panel: Segmented transport mode bar, IP entry with copy button, Auto Detect IP, Connect & Start / Stop Stream actions.
    - Quick Modes: 8 color-coded preset pills (Meetings, Online Class, Streaming, Snapshot, Scan / OCR, Security, Fun Filter, Pro Reset).
    - Camera Card: Live video viewfinder canvas (native 15 FPS PPM decoding without external PIL dependencies) with corner brackets and crosshair standby graphics, Front/Rear lens toggle, rotation, resolution dropdown, frame rate dropdown, zoom controls (+/- buttons and slider), Ultra Photo, and Mirror toggle.
    - Image Controls Card: ISO, Shutter, White Balance, and Color FX switches with parameter dropdowns, AF: Auto, Focus, EV -, EV +, and Sync State controls.
    - Lighting Card: Torch switch, Front Glow switch, Screen Keep ON switch, Brightness slider, and Color Temperature slider.
    - Background Card: Preset pills (Pass-Through, Blur, Green Screen, Select Image, Presets), checkered preview canvas with silhouette avatar, and GPU vs Mobile processing radio options.
    - More Controls Card: 6 clean modal dialog triggers (OBS Setup, Dependencies, OEM Fix, Settings, Diagnostics, Uninstall / About & License).
    - Event Log Card: Scrolled log with Clear button and colored status dots.
  - `cambridge_receiver.py`: Added `on_frame_cb` callback support in `CamBridgeReceiver` to feed decoded BGR video frames directly to GUI preview.
  - Updated `USER_GUIDE.md` with Material Design 3 ASCII layout representation.
  - Repackaged `Stable/Stable_Desktop_Client v1.3.0.0.zip` (520 KB).
  - Verified cross-platform test suite (`test_cross_platform.py` -> 5/5 PASSED).
  - Verified pre-commit secret scan (`scan_secrets_and_diff.py` -> 0 secrets detected).

## 2026-11-19 00:12:00 IST (UTC+05:30)
- Mode-Aware Auto Detect IP & Zero-Terminal Silent Launchers Suite:
  - `network_discovery.py`: Upgraded network discovery engine with full cross-platform adapter enumeration and filtering. Excludes loopback (`127.*`), APIPA (`169.254.*`), virtual adapters (WSL, Hyper-V, Docker, VMware, VirtualBox, Wi-Fi Direct virtual), and VPNs (WireGuard, OpenVPN, Tailscale, ZeroTier, commercial VPNs). Added `detect_tethering_adapter()`, `detect_lan_adapters()`, `is_port_in_use()`, and `find_available_port()`.
  - `adb_tunnel.py`: Added `resolve_forward_ports()` to dynamically detect if local ports (8089, 8090) are in use by another non-ADB process on `127.0.0.1` and automatically allocate the next available local port forwarding to the phone's remote port.
  - `otter_app.py`:
    - Made Auto Detect IP connection-mode aware:
      1. USB Tethering mode: Detects the host IPv4 address of the USB tethering network interface, discovers phone gateway IP (or probes active stream), and reports clear error if USB tethering is not turned on.
      2. USB ADB Tunnel mode: Uses `127.0.0.1`, verifies ADB device connectivity, detects port conflicts, and dynamically maps free local ports if needed.
      3. Wi-Fi LAN mode: Scans filtered physical LAN/Wi-Fi subnets, auto-fills discovered camera IP, and provides clear diagnostic feedback with local PC IP if no camera is active.
      4. Auto mode: Probes ADB USB -> USB Tethering -> Wi-Fi LAN in priority order.
    - Added thread-safe `_post_ui()` message queue preventing `RuntimeError: main thread is not in main loop` across all multi-threaded background workers and preview callbacks.
    - Updated `_toggle_conn_mode` to dynamically update the IP entry field based on the selected mode.
  - Cross-Platform Zero-Terminal Silent Launchers:
    - Windows: Created `run_windows_silent.vbs` launching Otter via `pythonw.exe` without opening a command prompt/console window.
    - Linux: Created `run_linux_silent.sh` and `otter.desktop` application shortcut configured with `Terminal=false`.
    - macOS: Created `run_macos_silent.command` utilizing AppleScript detachment to launch without keeping Terminal.app open.
  - Synchronized verified files to `Stable/Stable_Desktop_Client/` and repackaged `Stable/Stable_Desktop_Client v1.3.0.0.zip`.
  - Updated `USER_GUIDE.md` with Zero-Terminal launcher instructions.
  - Cross-platform test suite (`test_cross_platform.py`): 5/5 PASSED (9/9 shell scripts LF-clean, syntax valid, mock Linux/macOS clean).
  - Pre-commit secret scan (`scan_secrets_and_diff.py`): 0 secrets detected.


## 2026-11-19 00:45:00 IST (UTC+05:30)
- Fixed USB Tethering streaming connection in `Dev/desktop/otter_app.py`:
  - Resolved IP loopback failure where USB Tethering mode previously attempted connecting to `127.0.0.1:8089` without ADB forwarding.
  - Implemented dynamic gateway resolution in `start_stream()`: when in tether mode with empty, loopback, or legacy default IP, automatically detects active RNDIS network adapter gateway (`10.187.247.133`) and updates the UI entry field before connecting.
  - Maintained complete isolation for ADB USB Tunnel and Wi-Fi LAN streaming modes with zero regressions.
  - Verified live H.264 video packet stream reception from connected Android device over USB tether interface.
  - Updated `Dev/docs/bugs/bugs.md` (BUG-016: Tested).
## 2026-11-19 01:08:00 IST (UTC+05:30)
- Fixed Desktop Connection Lifecycle, Device Disconnection Detector & Camera Sensor Orientation:
  - `otter_app.py`:
    - Added connection guards preventing starting the stream when no camera device is connected (checks USB ADB serial, active USB Tethering adapter, and Wi-Fi host before starting).
    - Added bidirectional start/stop RPC synchronization: clicking "Connect & Start" sends `start_stream` to mobile app, and clicking "Stop" sends `stop_stream` to mobile app.
    - Updated connection lifecycle: sets badge to "● Connecting..." on start attempt and promotes to "● Active: {cam_name}" only upon receiving live stream frames.
    - Fixed disconnect reset: on device disconnect, automatically resets UI state (`btn_connect` back to NORMAL, `btn_stop` to DISABLED, and badge to "● Disconnected").
    - Fixed canvas aspect ratio: renders clean unpillarboxed camera frames into viewfinder canvas according to true sensor aspect ratio without black bars.
  - `cambridge_receiver.py`:
    - Added 2.5s socket timeout and disconnect detector in stream demux loop; cleanly terminates on socket drop/timeout instead of blocking indefinitely.
    - Reduced connection retry deadline to 10s for immediate feedback when camera is unreachable.
    - Dispatches clean rotated frames to UI preview callback before virtual camera pillarboxing.
  - `MainActivity.java`:
    - Implemented `calculateSensorRotation()` applying dynamic display rotation matrix to `CameraCharacteristics.SENSOR_ORIENTATION`.
    - Fixed `configureTransform()` on phone viewfinder: eliminated unnecessary 90° clockwise preview rotation in normal portrait mode (`ROTATION_0`), preventing sideways preview in phone TextureView.
    - Added explicit `stopEncoder()` call in `stopStreaming()` to prevent stale encoder input surfaces on Qualcomm hardware.
  - Built and verified Android APK (`assembleDebug` in 28s).
  - Verified cross-platform test suite (5/5 PASSED) and secret scan (0 detected).
  - Updated `Dev/docs/bugs/bugs.md` (BUG-017: Tested, BUG-018: Tested).
## 2026-11-22 00:05:00 IST (UTC+05:30)
## 2026-11-22 00:18:00 IST (UTC+05:30)
- Added Windows Web UI Batch Launcher, QR Code Scanner & Android Chrome Camera Origin Fix (BUG-020):
  - `run_web_ui_windows.bat`: Interactive console launcher with auto-detection of `.venv`, bundled Python, or system Python, keeping errors visible if initialization encounters an exception.
  - `run_web_ui_windows.vbs`: Hardened silent background launcher pointing reliably to `otter_web_server.py`.
  - QR Code Generation: Added client-side QR code generator (`qrcode.min.js`) and API image fallback in `index.html` with a one-click address copy button for instant phone scanning.
  - Chrome Android `getUserMedia` Insecure Origin Fix: Chrome Android disables `navigator.mediaDevices` on plain HTTP non-localhost LAN IPs. Added automatic Secure Context detection in `streamer.html`, diagnostic banner, direct Chrome flag instructions (`chrome://flags/#unsafely-treat-insecure-origin-as-secure`), and recommendation for ADB reverse (`http://localhost:8080`).
  - Passed `test_cross_platform.py` and `scan_secrets_and_diff.py` with 0 errors and 0 leaks.

  - `run_web_ui_windows.vbs`: Launches the Otter Web UI controller in the background with zero command prompt / console windows using `pythonw.exe` and automatically opens Brave Browser.

  - Addressed Tkinter canvas rendering failures on Linux (X11/Wayland) and macOS (Aqua) by replacing mandatory Tkinter GUI with a browser-based web dashboard.
  - `otter_web_server.py`:
    - Embedded zero-dependency HTTP & MJPEG live stream server.
    - Integrated safe dynamic port allocator starting at 8080 with automatic fallback that strictly avoids system-reserved and privileged OS ports (<1024, RPC, SMB, mDNS, etc.).
    - Automated detection and launch of Brave Browser as primary default browser per rule 4, falling back to system default.
  - `web_ui/index.html`: Responsive Dark-themed PC control dashboard with live MJPEG viewfinder, bidirectional camera controls (ISO, AWB, FX, zoom, torch, flip lens, rotation), Virtual Background switcher, and one-click connection modes (Auto, USB ADB, USB Tethering, Wi-Fi LAN).
  - `web_ui/streamer.html`: Zero-install mobile browser streamer (Safari/Chrome) adhering to REQ-023 strict portrait lock and orientation guard.
  - `cambridge_receiver.py`: Added `push_external_frame()` and `start_virtualcam_only()` to allow browser streamer frames to flow seamlessly into native OS virtual webcam drivers (DirectShow UnityCapture / OBS on Windows, v4l2loopback on Linux, pyvirtualcam/OBS on macOS).
  - `run_linux.sh` & `run_macos.sh`: Made Tkinter check optional; launches directly into universal Web UI if Tkinter is not installed.
  - Passed `test_cross_platform.py` and `scan_secrets_and_diff.py` with zero errors and zero leaks.

- Fixed Desktop Client Streaming RPC Sync & Phone Status Synchronization:
  - `cambridge_control.py`: Added explicit `start_stream()` and `stop_stream()` RPC methods sending `{"action": "start_stream"}` and `{"action": "stop_stream"}` over TCP port 8090, resolving an `AttributeError` that previously prevented desktop client button clicks from reaching the Android app.
  - `otter_app.py`:
    - Updated `start_stream()` to send `start_stream` to phone with a 0.3s warm-up delay before receiver connection.
    - Updated `stop_stream()` to send `stop_stream` to phone, cleanly tearing down phone video server and camera session.
    - Enhanced `_apply_synced_status()`: continuously monitors `"streaming"` flag from mobile app status. When the user taps "Stop" on the phone, the desktop client automatically detects it and reverts buttons to Normal/Disconnected.
    - Added canvas aspect ratio viewport centering and border guide.
  - Verified unit tests for RPC start/stop dispatch and bidirectional state synchronization.
  - Verified pre-commit secret scan (`scan_secrets_and_diff.py` -> 0 secrets detected).
