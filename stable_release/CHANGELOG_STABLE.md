# Official Stable Changelog

All notable official stable releases of Otter Virtual Camera and Remote Controller System.

---

## [1.1.0.0] - 2026-11-17 09:35:00 IST (UTC+05:30)

### Production Deliverables
- **Desktop Client**: `Stable/Stable_Desktop_Client/`
  - Self-contained, multi-platform desktop client (Windows, macOS, Linux).
  - One-click launcher scripts (`run_windows.bat`, `run_linux.sh`, `run_macos.command`, `run_macos.sh`) designed to run directly from the client directory as root.
  - Complete manual camera control sliders: ISO (100-3200), Shutter (1/2000s-1/15s), White Balance, Color FX, each with independent Auto mode interlocks.
  - Zoom controls: dedicated Zoom In/Out (+/-) buttons and 1.0x - 8.0x digital zoom slider.
  - 8 Quick Mode presets (Meetings, Online Class, Streaming, Snapshot, Scan/OCR, Security, Fun Filter, Pro Manual).
  - Ultra Photo capture button with timestamped saving.
  - Integrated Google ADB minimal tools automated downloader and manager for zero-config USB streaming.
  - Windows DirectShow virtual camera driver installer/uninstaller (`driver/`).

- **Android App**: `Stable/Stable_android_app/`
  - Standalone Gradle project source code with `versionCode 2` and `versionName "1.1.0.0"`.
  - Pre-built signed release APK: `Otter-v1.1.0.0.apk`.
  - OpenCamera-style sensor orientation math ensuring stream and preview stay upright in landscape mode.
  - Viewfinder layout locked to portrait orientation to eliminate screen squishing.
  - MediaCodec H.264 encoder lifecycle guard preventing state mismatch crashes.
  - Dedicated PC Desktop Client guide card in About & Guide with one-click clipboard copying.

## [1.1.0.0-Rev1] - 2026-11-17 09:42:00 IST (UTC+05:30)

### Distribution Separation & Legal Compliance
- **Google Play Store Version**: `Stable/stable_playstore_version/`
  - Compliant with Google Play Store policies and target SDK 34 (Android 14).
  - Built pre-compiled Android App Bundle `Otter-v1.1.0.0.aab` (625 KB) for Google Play App Signing.
  - Added in-app Privacy Policy and User Agreement dialog/browser triggers in `AboutActivity.java`.
  - Added `GOOGLE_PLAY_DATA_SAFETY.md` detailing exact answers for Google Play Console submission.
  - Added `PRIVACY_POLICY.md` and `USER_AGREEMENT.md` governed by the Laws of the Republic of India (Information Technology Act, 2000).
- **GitHub / Sideload Version**: `Stable/stable_non_playstore_version/`
  - `Otter-v1.1.0.0-signed.apk` (619 KB) for immediate 1-click ADB sideloading and testing.
  - `Otter-v1.1.0.0-unsigned.apk` (611 KB) for developers and custom keystore signers.
  - Standalone documentation and custom signing guide.
- **GitHub Hosted Legal Assets**: `docs/`
  - Created web-accessible HTML and Markdown policies (`docs/privacy_policy.html`, `docs/user_agreement.html`, `docs/PRIVACY_POLICY.md`, `docs/USER_AGREEMENT.md`) ready for Google Play Store URL verification.

## [1.1.0.0-Rev2] - 2026-11-17 10:15:00 IST (UTC+05:30)

### Universal Master Policies & Legal Jurisdiction
- **Consolidated Policy Suite**: Created universal `Policies And Agreement/` directory containing all master terms, privacy disclosures, attribution requirements, and Play Store guides strictly in Markdown (`.md` only, zero HTML).
- **Consolidated Master Policy**: Created `Policies And Agreement/POLICIES_AND_AGREEMENT.md` as the sole master policy document governing Android (Play Store & Sideload) and PC Desktop Clients.
- **Jurisdiction & Governing Law**: Formally specified exclusive jurisdiction in the Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005) under the Information Technology Act, 2000, and Indian Contract Act, 1872.
- **Zero Developer Data Retention & Disclaimers**: Added explicit clauses stating developers retain zero user data (server deletion is inoperative), hold zero liability for local network packet interception or data loss, and separate OS/store/OEM telemetry (Google Play Services, MIUI/HyperOS, ColorOS, Funtouch OS, One UI) from developer liability.
- **Mandatory Attribution**: Added explicit clause requiring all reuses, forks, or derivations to prominently credit developer `spacecar`, name `Otter`, and link to `https://github.com/saprecar/Otter`.
- **Contact Protocol**: Configured `getspacecar@gmail.com` with mandatory subject prefix (`[Otter-Legal]` / `[Otter-Inquiry]`) and official GitHub issues.
- **Application & Desktop Client Updates**: Updated in-app consent dialogs and About screens on both Android and PC to link dynamically to `Policies And Agreement/` documents. Zero APK generation executed.

## [1.1.0.0-Rev3] - 2026-11-17 11:25:00 IST (UTC+05:30)

### Dual Virtual Background, Screen Wake & Master Guidebook
- **Dual Virtual Background Engine**:
  - Implemented real-time background compositing in `Stable/Stable_Desktop_Client/cambridge_receiver.py` supporting: Off/Pass-Through, Custom Image Background, Light Bokeh Blur, Heavy Privacy Blur, and Green Screen Chroma Keying.
  - Added Workload Routing selector: PC GPU/CPU Offload (preserves phone thermals, prevents thermal throttling at 1080p/60fps, saves battery) vs On-Device Mobile processing.
  - Automatic detection of MediaPipe AI selfie segmentation with built-in zero-dependency OpenCV bokeh / chroma key fallback.
- **Screen Wake & Power Management**:
  - Added Keep Screen On user toggle (`FLAG_KEEP_SCREEN_ON`) in `Stable/stable_playstore_version` and `Stable/stable_non_playstore_version` with persistent preference.
  - Added Display Dimming mode (`Dim Display (Save Power)`) reducing screen backlight to minimum during multi-hour streams to preserve power.
  - Added remote screen wake toggle and status sync to Desktop Client (`otter_app.py`, `cambridge_control.py`).
- **Master Guidebook**: Published comprehensive `GUIDEBOOK.md` in repository root with setup guides, architecture breakdowns, virtual camera driver guides, OEM anti-kill tips, and legal disclaimers.
- **Verification**: Verified syntax with `py_compile` and `compileDebugJavaWithJavac` across all modules. Respected build constraints: zero APK builds generated.

## [1.1.0.0-Rev4] - 2026-11-17 11:35:00 IST (UTC+05:30)

### Android 16 (API 36) & Play Store Audit Compliance
- **Target SDK Upgrade**: Upgraded `targetSdk` and `compileSdk` to 36 (Android 16, Baklava) across all stable Android modules (`stable_playstore_version` and `stable_non_playstore_version`). Suppressed compileSdk warnings with `android.suppressUnsupportedCompileSdk=35,36`.
- **Restricted Permission Removal**: Removed `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` from `AndroidManifest.xml` across all packages to eliminate risk of Play Store policy rejections, while keeping safe in-app guidance via standard settings intents.
- **Data Safety Accuracy**: Truthfully declared "Encrypted in transit: No" in `GOOGLE_PLAY_DATA_SAFETY.md` reflecting local raw TCP socket streaming without application-layer TLS certificate encapsulation.
- **Legal Citation Accuracy**: Corrected Section 6 of `POLICIES_AND_AGREEMENT.md` to cite Section 66E (Violation of Privacy) for clandestine recording and surveillance, and Section 67 for transmitting obscene material under the Indian IT Act, 2000.
- **Package ID vs App Name**: Documented package identifier `org.understory.cambridge` alongside public app name `Otter`.
- **Verification**: Verified compilation using `compileDebugJavaWithJavac` across all packages (0 errors, 0 APKs generated).

## [1.1.0.0-Rev5] - 2026-11-17 12:10:00 IST (UTC+05:30)

### Google Play Store Visual Assets, Metadata & 10-Inch Tablet Screenshots
- **Play Store Metadata & Translations**:
  - Published `store_listing_translations.csv` and `STORE_LISTING.md` with multi-language listings for English (`en-US`), Hindi (`hi-IN`), and Spanish (`es-ES`) adhering strictly to Google Play character limits (Title <= 30, Short Description <= 80, Full Description <= 4000).
  - High-resolution 512x512 app icon (`playstore_icon_512x512.png`).
  - 1024x500 Feature Graphic (`playstore_feature_graphic_1024x500.png` and `playstore_feature_graphic_1024x500.jpg`).
- **10-Inch Tablet Screenshots**:
  - Generated eight 1920x1080 (16:9 landscape, < 8 MB) high-definition tablet screenshots adhering to Google Play Console 10-inch tablet specifications:
    1. `playstore_tablet_10inch_screenshot_1.png`: 1080p 60 FPS Ultra-Low Latency Streaming
    2. `playstore_tablet_10inch_screenshot_2.png`: Pro Manual Optics & Camera2 Controls
    3. `playstore_tablet_10inch_screenshot_3.png`: Dual Virtual Background Engine (PC GPU Offload)
    4. `playstore_tablet_10inch_screenshot_4.png`: 8 One-Touch Purpose Presets
    5. `playstore_tablet_10inch_screenshot_5.png`: Smart Power & Battery Protection (Screen Keep-ON & Dimming)
    6. `playstore_tablet_10inch_screenshot_6.png`: 100% Private Zero-Cloud Architecture
    7. `playstore_tablet_10inch_screenshot_7.png`: Multi-Lens Switching & 4K Ultra Photo
    8. `playstore_tablet_10inch_screenshot_8.png`: Universal Compatibility for OBS Studio, Zoom, and Teams
  - Visual assets synchronized to `Stable/stable_playstore_version/` and `Dev/android/app/src/main/`.

## [1.1.0.0-Rev6] - 2026-11-17 13:28:00 IST (UTC+05:30)

### GitHub Documentation Visual Showcase
- **README.md Overhaul**: Embedded 512x512 app logo, 1024x500 Feature Graphic header banner, and 2-column screenshot gallery displaying all 8 tablet console screenshots.
- **GUIDEBOOK.md Visual Enhancements**: Embedded high-resolution architectural diagrams and feature screenshots directly into operational sections (Dual Virtual Background Engine, Power Management, Pro Manual Optics, Presets).
- **Strict Zero-Emoji Sanitization**: Replaced non-standard unicode characters in documentation codeblocks with clean ASCII symbols.
- **Build Safety**: Verified zero APK builds generated.

## [1.1.0.0-Rev7] - 2026-11-17 14:10:00 IST (UTC+05:30)

### Google Play Automatic Protection (minSdkVersion 24)
- **Minimum SDK Upgrade**: Upgraded `minSdk` to 24 (Android 7.0 Nougat) across all stable Android build configurations (`stable_playstore_version` and `stable_non_playstore_version`), fully satisfying Google Play Automatic Protection requirements.
- **AAB Re-Packaging**: Re-generated `Otter-v1.1.0.0.aab` via `bundleRelease` with targetSdk 36 and minSdk 24 baked into the app bundle manifest.
- **Build Safety**: Verified zero APK builds generated.

## [1.1.0.0-Rev8] - 2026-11-17 14:15:00 IST (UTC+05:30)

### F-Droid & IzzyOnDroid Distribution Specification
- **Official F-Droid Recipe**: Authored `Stable/stable_non_playstore_version/org.understory.cambridge.yml` defining package categories, MIT licensing, upstream Git repository, and reproducible build instructions.
- **F-Droid & IzzyOnDroid Submission Guide**: Published `Stable/stable_non_playstore_version/FDROID_SUBMISSION_GUIDE.md` covering GitLab Merge Requests, IzzyOnDroid GitHub APK tracking, and self-hosted `fdroidserver` options.
- **Build Safety**: Verified zero APK builds generated.

## [1.1.0.0-Rev9] - 2026-11-17 14:55:00 IST (UTC+05:30)

### Virtual Background Wallpapers & Live Camera Notification
- **Virtual Background Wallpapers & Sizing**: Included four 1920x1080 (16:9) sample wallpapers in `Stable/Stable_Desktop_Client/wallpapers/`. Documented wallpaper sizing specs (16:9 widescreen, 1920x1080 FHD, PNG/JPG/WEBP < 15MB, automatic aspect scaling) and updated controller UI file dialogs.
- **Live Camera Active Notification**: Implemented persistent ongoing notification (`Otter Camera: LIVE`) in `OtterStreamService.java` displaying live port 8089, resolution, and native one-tap `[Stop Stream]` notification action. Added `POST_NOTIFICATIONS` runtime check on Android 13+.
- **Build Safety**: Re-bundled `Otter-v1.1.0.0.aab` and verified compilation with zero errors across all packages. Zero APKs generated.

## [1.2.0.0] - 2026-11-17 15:05:00 IST (UTC+05:30)

### Play Store Version Bump & Bundle Re-Packaging
- **Version Bump**: Incremented `versionCode` to `4` (even integer for public/stable release per Rule 13) and `versionName` to `1.2.0.0` in `Stable/stable_playstore_version/app/build.gradle` and `Stable/stable_non_playstore_version/app/build.gradle`.
- **App Bundle Re-Packaging**: Generated production Android App Bundle `Otter-v1.2.0.0.aab` via `bundleRelease` with `versionCode 4`, `versionName 1.2.0.0`, `minSdk 24`, and `targetSdk 36` verified in binary manifest.
- **Distribution Metadata**: Updated `org.understory.cambridge.yml`, `output-metadata.json`, and `FDROID_SUBMISSION_GUIDE.md` to reflect `v1.2.0.0`.
- **Build Safety**: Verified zero APK builds generated.

## [1.2.0.0-Rev1] - 2026-11-18 16:29:00 IST (UTC+05:30)

### Non-Play Store Android 5.0 (API Level 21) Support
- **F-Droid / Sideload MinSDK**: Lowered `minSdkVersion` to `21` (Android 5.0 Lollipop) in `Stable/stable_non_playstore_version/app/build.gradle` to provide support for older Android hardware.
- **Play Store Isolation**: Left `Stable/stable_playstore_version/app/build.gradle` unchanged with `minSdkVersion 24` to satisfy Google Play Automatic Protection.
- **Verification**: Verified compilation via `compileDebugJavaWithJavac` (BUILD SUCCESSFUL, zero errors).
- **Build Safety**: Verified zero APK builds generated.

## [1.2.0.0-Rev2] - 2026-11-18 16:55:00 IST (UTC+05:30)

### Virtual Background & Green Screen Selection Suite
- **Android Wallpaper & Background Selection**: Added interactive in-app dialog to `MainActivity.java` enabling selection of Light Bokeh Portrait Blur, Heavy Privacy Blur, Solid Green Screen (Chroma Key), custom wallpaper upload from device gallery (`ACTION_GET_CONTENT`), and four preset wallpapers.
- **Desktop Background Quick Controls**: Added Quick Effects toolbar (`[Blur Background]`, `[Green Screen]`, `[Upload/Select Image...]`, `[Pass-Through]`) and Preset BG buttons (`[Modern Office]`, `[Studio Bokeh]`, `[Bookshelf]`, `[Coffee Shop]`) to `otter_app.py`. Added pure chroma key green rendering to `cambridge_receiver.py`.
- **Wallpaper Sizing Guidance**: Documented wallpaper guidelines (16:9 aspect ratio, 1920x1080 FHD / 1280x720 HD, PNG/JPG/WEBP < 15MB, automatic aspect scaling) across Android dialog, PC UI, `GUIDEBOOK.md`, and `USER_GUIDE.md`.
- **Verification**: Verified `compileDebugJavaWithJavac` across all packages and validated desktop suite via `test_cross_platform.py`.
- **Build Safety**: Verified zero APK builds generated.

## [1.2.0.0-Rev3] - 2026-11-18 17:15:00 IST (UTC+05:30)

### High-Res Quad-Bayer Detection, 60 FPS Range Negotiation & Foreground Toggle
- **High-Res Quad-Bayer Detection**: Resolved hardware resolution reporting on Poco F6 / iQOO Z7 devices by detecting physical sensor megapixels (`SENSOR_INFO_PIXEL_ARRAY_SIZE`) and handling 4:1 pixel binning vs Android 12+ maximum resolution stream configuration maps (`SCALER_STREAM_CONFIGURATION_MAP_MAXIMUM_RESOLUTION`). Button dynamically labels `★ Ultra (64MP Full)` or `★ Ultra (64MP/16MP Bin)`.
- **Dynamic 60 FPS Range Adaptation**: Negotiated HAL target FPS ranges through `getBestFpsRange()` to select exact `[60, 60]` or flexible `[30, 60]` ranges, preventing HAL crashes while boosting MediaCodec bitrate to 8 Mbps for high-framerate streaming.
- **User-Controlled Foreground Service**: Added on/off toggle for Foreground Service (`btnBackgroundLock`), allowing users to choose whether to stream with ongoing background notification & wake lock or run strictly as a foreground app with zero notification clutter.
- **Verification**: Verified compilation across all Android packages via `compileDebugJavaWithJavac` (BUILD SUCCESSFUL, zero errors).
- **Build Safety**: Verified zero APK builds generated.

## [1.3.0.0] - 2026-11-18 18:10:00 IST (UTC+05:30)

### Video Pipeline Stabilization, Connection Mode Dynamic Labeling & Version Sync
- **Green Screen Resolution & Stream Decoupling**:
  - Eliminated green screen failure on USB Tethering and ADB connections by isolating `createCaptureSession` targets strictly to `previewSurface` and `encoderInputSurface`.
  - Removed 50MP/64MP high-resolution still capture ImageReader surface from regular streaming sessions, preventing camera HAL `onConfigureFailed` on constrained ISP architectures (Poco F6, Xiaomi, Samsung).
  - Added `MediaFormat.KEY_PREPEND_HEADER_TO_SYNC_FRAMES` on Android 10+ (API 29+) to prepend SPS/PPS parameter sets directly to sync frames.
  - Added `requestSyncFrame()` triggering `MediaCodec.PARAMETER_KEY_REQUEST_SYNC_FRAME` on client connection so receivers receive immediate IDR keyframes without waiting for frame interval cycles.
- **Dynamic Connection Mode Labeling**:
  - Replaced static "Wi-Fi IP" label on phone status bar with dynamic mode inspection based on remote client IP: `ADB USB Tunnel | Port: 8089` for localhost tunneling, `USB Tether: <ip> | Port: 8089` for wired RNDIS tethering, and `Wi-Fi IP: <ip> | Port: 8089` for local wireless connections.
  - Added `set_connection_mode` RPC command in `cambridge_control.py` and `MainActivity.java` allowing desktop client to explicitly notify the phone of the active connection transport.
- **Settings Version Synchronization**:
  - Replaced hardcoded `Otter (v1.0.0.1)` in `activity_about.xml` with dynamic runtime lookup via `PackageManager.getPackageInfo()` in `AboutActivity.java`.
  - Incremented `versionCode` to `6` and `versionName` to `1.3.0.0` across all `build.gradle` configurations.
- **Desktop Client ADB & Network Hardening**:
  - Resolved `AttributeError: 'ADBTunnel' object has no attribute 'adb_cmd'` in `otter_app.py` by referencing `tunnel.adb_bin`.
  - Hardened `network_discovery.py` to probe control port (8090) during auto-discovery scans to avoid disrupting active video streaming sockets on port 8089.
  - Repackaged `Stable/Stable_Desktop_Client v1.3.0.0.zip` containing all verified desktop client code.
- **Verification**:
  - Verified compilation via `compileDebugJavaWithJavac` across `Dev/android`, `Stable/stable_playstore_version`, and `Stable/stable_non_playstore_version` (BUILD SUCCESSFUL across all 3, zero errors).
  - Verified desktop cross-platform compatibility via `Dev/scripts/test_cross_platform.py` (5/5 PASS).
  - Verified secret scanner via `Dev/scripts/scan_secrets_and_diff.py` (0 secrets detected).
- **Build Safety**: Verified zero APK builds generated. User compiles and signs production binaries in Android Studio.

## [1.3.0.0-Rev1] - 2026-11-18 23:36:00 IST (UTC+05:30)

### USB / Wi-Fi Auto Switching & Connection Resilience Suite
- **ADB Tunnel Enhancements (`adb_tunnel.py`)**:
  - Added `usb_serial()` returning first authorized USB debugging device serial.
  - Added `_adb_prefix()` for targeting specific serials (`-s <serial>`).
  - Added `clear_forward()` to remove stale forwards before binding (`forward --remove tcp:<port>`), preventing "port in use" conflicts.
  - Overhauled `setup_forward()` to clear stale forwards first, bind both ports (`8089`, `8090`), capture errors, and return `bool`.
- **Receiver Re-forwarding & Retry Loop (`cambridge_receiver.py`)**:
  - Added `self.reforward_cb = None` to `CamBridgeReceiver`.
  - Added `_connect_with_retry()` method automatically re-running ADB port forwarding before each connection retry and displaying clear checklist diagnostics on timeout.
  - Added `--mode auto` (default) which tries USB (ADB tunnel) first and automatically falls back to Wi-Fi.
- **Desktop Auto Mode & State Tracking (`otter_app.py`)**:
  - Added "Auto (USB -> Wi-Fi)" radio button option set as the default connection mode.
  - In `start_stream()`, automatically probes for USB devices via `usb_serial()`; if detected, sets up ADB forwarding and connects over `127.0.0.1` with retry callback; if no USB device is connected or forward fails, seamlessly falls back to Wi-Fi.
  - Updated `_get_active_host()` to follow the real resolved transport host (`127.0.0.1` for USB, or entered IP for Wi-Fi).
  - Sends `start_stream` and `stop_stream` control commands to Android app to coordinate remote streaming.
- **Android Socket Reuse & Client Isolation (`MainActivity.java`)**:
  - Added `setReuseAddress(true)` to `videoServerSocket` and `controlServerSocket` to prevent "address already in use" errors on reconnects.
  - Added stale client teardown (`if (activeVideoClient != null) activeVideoClient.close()`) before accepting a new client socket.
  - Added robust IPv6/loopback address detection (`addr.isLoopbackAddress()` or contains `127.0.0.1` -> `adb`, `192.168.42.x` / `192.168.43.x` -> `usb_tether`, otherwise `wifi`).
  - Implemented auto-stop on disconnection: if client socket closes or broken pipe occurs during streaming, Android automatically calls `stopStreaming()` and resets status to prevent hardware stress and battery drain.
- **Stable Packaging & Verification**:
  - Repackaged `Stable/Stable_Desktop_Client v1.3.0.0.zip`.
  - Verified compilation across `Dev/android`, `Stable/stable_playstore_version`, and `Stable/stable_non_playstore_version` (`gradlew.bat compileDebugJavaWithJavac`, BUILD SUCCESSFUL across all 3, 0 errors).
  - Verified desktop cross-platform compatibility via `Dev/scripts/test_cross_platform.py` (5/5 PASS).
  - Verified secret scanner via `Dev/scripts/scan_secrets_and_diff.py` (0 secrets detected).
- **Build Safety**: Verified zero APK builds generated. User compiles and signs production binaries in Android Studio.

## 2026-11-18 23:58:00 IST (UTC+05:30) - Version 1.3.0.0 (Material Design 3 Desktop UI)
- **Desktop UI Redesign (Material Design 3 Control Panel)**:
  - Redesigned `Stable/Stable_Desktop_Client/otter_app.py` into a modern, compact, single-window Material Design 3 control panel based on the reference UI specification without multi-tab scrolling.
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

## 2026-11-19 00:12:00 IST (UTC+05:30) - Version 1.3.0.0 (Mode-Aware Auto Detect IP & Silent Launchers)
- **Mode-Aware Auto Detect IP**:
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
- **Cross-Platform Zero-Terminal Silent Launchers**:
  - Windows: Added `run_windows_silent.vbs` launching Otter via `pythonw.exe` without opening a command prompt/console window.
  - Linux: Added `run_linux_silent.sh` and `otter.desktop` application shortcut configured with `Terminal=false`.
  - macOS: Added `run_macos_silent.command` utilizing AppleScript detachment to launch without keeping Terminal.app open.
- **Stable Packaging & Verification**:
  - Repackaged `Stable/Stable_Desktop_Client v1.3.0.0.zip` (528 KB).
  - Verified cross-platform test suite (`test_cross_platform.py` -> 5/5 PASSED, 9/9 shell scripts LF-clean).
  - Verified pre-commit secret scan (`scan_secrets_and_diff.py` -> 0 secrets detected).


## 2026-11-22 00:30:00 IST (UTC+05:30) - Version 1.5.0.0 Desktop (Universal Web UI Controller & Zero-Install Browser Streamer)
- **Universal Cross-Platform Web UI Controller**:
  - Addressed GUI rendering inconsistencies on Linux (Wayland/X11) and macOS (Aqua) by replacing mandatory Tkinter desktop GUI with a modern, responsive Web UI dashboard.
  - Developed `otter_web_server.py`: embedded zero-dependency HTTP and MJPEG stream server serving the control interface and live video viewfinder.
  - Implemented safe port auto-allocation: dynamically finds available ports starting from `8080`, strictly excluding privileged and system/OS-reserved ports (<1024, RPC, SMB, mDNS).
  - Automated Brave Browser launch as primary default browser, with seamless fallback to system default.
- **Zero-Install Mobile Browser Streamer (REQ-023)**:
  - Enabled mobile Safari (iOS) and Chrome (Android) camera streaming to PC virtual webcams without installing any APKs or native apps.
  - Added integrated scannable QR code generator and address copy button in `web_ui/index.html`.
  - Resolved Chrome Android `getUserMedia` Insecure Context restriction: provides in-page diagnosis and instructions for `chrome://flags/#unsafely-treat-insecure-origin-as-secure` or ADB reverse.
- **Dual-Input Virtual Camera Receiver**:
  - Enhanced `cambridge_receiver.py` with `push_external_frame()` and `start_virtualcam_only()` to seamlessly multiplex between native Android H.264 streams and WebRTC/HTML5 browser streams.
- **Launchers & Packaging**:
  - Added `run_web_ui_windows.bat` for interactive console launching with error persistence.
  - Packaged standalone release `Stable/Stable_Desktop_Client v1.5.0.0.zip` (585 KB).
  - Verified cross-platform test suite (`test_cross_platform.py` -> 5/5 PASSED).
  - Verified pre-commit secret scan (`scan_secrets_and_diff.py` -> 0 secrets detected).

## 2026-11-19 01:25:00 IST (UTC+05:30) - Version 1.4.0.0 (USB Tethering, Upright Orientation & Stream Sync)
- **Version Bump**:
  - Incremented `versionCode` to `8` (even single-digit integer for stable release per Rule 13) and `versionName` to `1.4.0.0` across `Dev/android/app/build.gradle`, `Stable/stable_playstore_version/app/build.gradle`, and `Stable/stable_non_playstore_version/app/build.gradle`.
- **USB Tethering Auto-Gateway Resolution (`otter_app.py`)**:
  - Resolved dynamic subnet assignment on modern Android (Google Mainline Tethering / RNDIS assigns `10.x.x.x` subnets).
  - Enhanced `start_stream()`: when USB Tethering mode is selected with empty, loopback `127.0.0.1`, or legacy default IP, the desktop client automatically queries the active RNDIS network adapter gateway IP (`10.187.247.133`) and updates the UI entry field before connecting.
  - Added connection pre-flight guards: halts execution and displays clear dialog if no USB debugging device, active tethering interface, or reachable host exists, preventing invalid streaming state.
- **Bidirectional Streaming RPC & State Synchronization**:
  - `cambridge_control.py`: Added explicit `start_stream()` and `stop_stream()` RPC methods sending `{"action": "start_stream"}` and `{"action": "stop_stream"}` over TCP port 8090, resolving an `AttributeError` that previously prevented desktop client button clicks from reaching the Android app.
  - `otter_app.py`: Clicking "Connect & Start" sends `start_stream` with a 0.3s warm-up pause, and clicking "Stop" dispatches `stop_stream` to cleanly stop the camera, encoder, and background service on Android.
  - Enhanced `_apply_synced_status()`: monitors the `"streaming"` field in phone status reports. When "Stop" is tapped on the phone, the desktop client automatically detects it and reverts its buttons and status badge back to normal/disconnected.
  - Added 2.5s socket read timeout and disconnect detection logic to the demux loop in `cambridge_receiver.py`; detects lost socket connections immediately instead of hanging indefinitely.
- **Camera Sensor Orientation & Upright Viewfinder Fix**:
  - `MainActivity.java`: Implemented `calculateSensorRotation()` applying dynamic display rotation matrix to `CameraCharacteristics.SENSOR_ORIENTATION` for front and back camera streams.
  - Fixed `configureTransform()` on phone viewfinder: eliminated unnecessary 90° clockwise preview rotation in normal portrait mode (`ROTATION_0`), restoring upright viewfinder rendering on the phone screen.
  - Added explicit `stopEncoder()` cleanup in `stopStreaming()` to release the hardware `MediaCodec` input surface on disconnects, preventing stale surfaces on Qualcomm hardware.
  - Canvas Aspect Ratio Fix (`otter_app.py` / `cambridge_receiver.py`): Dispatches clean rotated camera frames to UI preview callback before virtual camera pillarboxing, rendering the live viewfinder according to true sensor aspect ratio without black bars.
- **Stable Packaging & Verification**:
  - Synchronized all verified source files to `Stable/Stable_Desktop_Client/`, `Stable/stable_playstore_version/`, and `Stable/stable_non_playstore_version/`.
  - Packaged `Stable/Stable_Desktop_Client v1.4.0.0.zip` (529 KB).
  - Verified cross-platform test suite (`test_cross_platform.py` -> 5/5 PASSED).
  - Verified pre-commit secret scan (`scan_secrets_and_diff.py` -> 0 secrets detected).
