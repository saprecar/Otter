# Otter User Guide & Operational Reference

## Overview
**Otter** turns any Android phone (Android 7.0 / API 24+) into a low-latency virtual webcam streaming directly to your PC (Linux, macOS, and Windows) over USB (ADB non-root) or Wi-Fi.

- **Developer**: spacecar
- **Repository**: [https://github.com/saprecar/Otter](https://github.com/saprecar/Otter)
- **License**: MIT License (Open and free for all; requires app name, repository link, and developer attribution in derivative works).

---

## 1. Android Mobile App (Otter)

### Modern Dark Glassmorphic UI Layout
```text
+-------------------------------------------------------------+
| [O] Otter Cam                     [Settings] [Fullscreen]   |
|     Camera for Every Purpose                                |
+-------------------------------------------------------------+
| +---------------------------------------------------------+ |
| | [● Live]      [4K / 1080p v]     [60 FPS v]             | |
| |                                                         | |
| |                  CAMERA VIEWPORT             [ + ] Zoom | |
| |             (Live Camera2 / Virtual Feed)    | 1.0x|    | |
| |                                              [ - ] Zoom | |
| |                                                         | |
| +---------------------------------------------------------+ |
| [Cam Connected]  |  Lens: 0 (BACK)  |  [ H.264 ]            |
+-------------------------------------------------------------+
| Quick Modes                              Choose a purpose   |
| +-------------+ +-------------+ +-------------+ +---------+ |
| | [Meetings]  | | [Online Cl] | | [Streaming] | |[Snapshot| |
| |    Green    | |    Blue     | |   Purple    | | Orange  | |
| +-------------+ +-------------+ +-------------+ +---------+ |
| +-------------+ +-------------+ +-------------+ +---------+ |
| | [Scan/OCR]  | | [Security]  | |[Fun Filter] | | [Pro Man| |
| |    Cyan     | |  Slate Blue | |   Emerald   | |  Pink   | |
| +-------------+ +-------------+ +-------------+ +---------+ |
+-------------------------------------------------------------+
| Camera Settings                              More Options v |
|  [ EV - ] [--------------o--------------] [ EV + ]   +0.0   |
|  [ AF: Auto ] [----------o--------------]            Auto   |
|  [ Flip: OFF ]  [ Rotate: 0 deg ]  [ Torch: OFF ]  [ Glow: OFF]|
|  Pro: [ ISO: Auto ] [ Shutter: Auto ] [ WB: Auto ] [ FX: Col|
|  Pro: [ Virtual BG: PC GPU Offload (Recommended)          ] |
+-------------------------------------------------------------+
| [ Start Stream ]  [ Pause ]  [ Stop ]  [ Switch Lens ]      |
| [ Ultra Photo (Full Res) ]  [ Lock Mode: ON ]  [ Battery ]  |
| [ Screen: Keep ON ]  [ Dim Display (Save Power)           ] |
+-------------------------------------------------------------+
| ● Otter: Ready                          Port: 8089 | v1.1.0 |
+-------------------------------------------------------------+
```

### Controls & Features
- **Pinch-To-Zoom & Steppers**: Smooth two-finger pinch-to-zoom on the viewfinder or tap floating `[ + ]` and `[ - ]` buttons (0.2x steps).
- **Exposure Compensation**: Dedicated `[ EV - ]` and `[ EV + ]` stepper buttons with real-time SeekBar and EV label (`+0.5 EV`).
- **Auto / Manual Focus**: Seamless toggle between continuous Auto Focus (`AF: Auto`) and precision Manual Focus distance slider from Macro (`0.1m`) to Infinity (`Inf`).
- **Pro Manual Mode (ISO, Shutter, AWB, FX)**:
  - `ISO`: Auto, 100, 200, 400, 800, 1600.
  - `Shutter`: Auto, 1/1000s, 1/500s, 1/250s, 1/125s, 1/60s, 1/30s.
  - `White Balance`: Auto, Daylight, Cloudy, Fluorescent, Tungsten.
  - `Color Effects`: Color, Black & White (Mono), Negative, Sepia.
- **Dynamic 4K & High FPS Detection**: Auto-detects supported video resolutions (up to 4K `3840x2160`) and sensor FPS ranges (up to 60 FPS) directly from device hardware.
- **Ultra Photo Capture**: Captures uncompressed still images at the camera sensor's maximum hardware resolution (e.g. 64MP / 48MP / 16MP) and saves directly to disk.
- **Virtual Background & AI Offload**: Select between PC GPU/CPU Offload (preserves phone thermals, saves battery, smooth 60fps) and On-Device Mobile processing. Supports custom background images, light bokeh blur, heavy privacy blur, and chroma key (green screen). Recommended wallpaper size: 16:9 ratio (1920x1080 FHD / 1280x720 HD) in PNG, JPG, or WEBP (<15MB). Includes 4 built-in sample wallpapers in `wallpapers/`.
- **Live Camera Active Notification**: Displays an ongoing, non-dismissible Android notification (`Otter Camera: LIVE`) while streaming is active, showing current port, resolution, and a one-tap `[Stop Stream]` action button.
- **Keep Screen On Toggle & Display Dim**: User-configurable toggle between keeping the phone screen awake during streams (`FLAG_KEEP_SCREEN_ON`) or allowing auto-sleep to save battery. "Dim Display" mode minimizes screen brightness by 70% while streaming.
- **Quick Modes (8 Purpose Presets)**: One-tap profiles for Meetings, Online Class, Streaming, Snapshot, Scan/OCR, Security, Fun Filter, and Pro Manual.
- **Fullscreen Mode & Floating Overlay**: Tap Fullscreen `[ ]` to expand the camera viewport to 100% full screen with a collapsible floating action menu.

### Multi-Screen & Responsive Device Support
- **Smartphones (Portrait)**: Full-bleed viewfinder on top with scroll-protected action controls below.
- **Landscape Mode & Foldables (Tabletop)**: Side-by-side split view with full-height viewfinder on the left and scrollable action bar on the right.
- **Tablets (7-inch & 10-inch, 600dp+)**: Spacious layout with enlarged 48dp touch targets and generous padding.
- **Foldables & Desktop Mode**: Fully compatible with `resizeableActivity="true"`, dynamic split-screen, and Samsung DeX.

---

## 2. Universal Web UI & Desktop Controller (Windows, Linux, macOS)

Otter provides a zero-driver cross-platform Web UI dashboard (`otter_web_server.py`) that runs natively in your browser (Brave, Chrome, Firefox, Edge, Safari), completely bypassing Tkinter/X11/Wayland/Aqua rendering issues.

### 1-Click Desktop Launchers
- **Windows**: Double-click `run_web_ui_windows.bat` (Interactive console with live status and auto-browser launch).
- **Linux**: Execute `./run_linux.sh` (or `./run_linux_silent.sh` for windowless background execution).
- **macOS**: Double-click `run_macos.command` (or execute `./run_macos.sh`).

### Connecting with Video Conference & Streaming Apps
- **Zoom, Teams, Meet & Discord**: Select `Unity Video Capture` or `OBS Virtual Camera` on Windows, `Otter Camera` on Linux, and `OBS Virtual Camera` on macOS.
- **OBS Studio (Zero Drivers via Browser Source)**: In OBS, add a **Browser Source** pointing to the dynamic loopback URL shown on the Web UI header: `http://localhost:<PORT>/mjpeg` (e.g. `http://localhost:8080/mjpeg`).

### Zero-Install Mobile Web Streamer (Apple iOS & Android)
Stream high-definition camera video directly from mobile browsers with zero app installation:
- **Apple Devices**: iPhone and iPad running **Safari** (iOS 11+).
- **Android Devices**: Phones and Tablets running **Chrome**, **Brave**, **Samsung Internet**, or **Firefox**.

#### Pairing & Camera Permissions
1. Scan the QR code displayed on the desktop Web UI (or type the local streamer address).
2. **Apple Safari (iPhone/iPad)**: Tap **Allow** when prompted for camera access.
3. **Android Chrome / Brave / Samsung Internet (Secure Context Fix)**:
   - Modern Chromium browsers require a Secure Context for camera access over plain HTTP LAN IPs.
   - If prompted with *"Cannot read properties of undefined (reading 'getUserMedia')"*, open `chrome://flags/#unsafely-treat-insecure-origin-as-secure` on your mobile browser, enable the flag, add your desktop IP origin (e.g. `http://192.168.1.50:8080`), and tap **Relaunch**.
   - *Alternative*: Connect over USB with USB debugging and run `adb reverse tcp:8080 tcp:8080` to open `http://localhost:8080/streamer` natively.
4. Tap **Start Stream** on your mobile screen. Video flows instantly into your PC's virtual camera and OBS!

---

## 3. Desktop Controller GUI (`otter_app.py` - Legacy Tkinter Fallback)

### Material Design 3 Control Panel Layout
```text
+-------------------------------------------------------------------------------------------------------------------+
| [Otter] Otter - Virtual Webcam & Remote Controller                                                 [Disconnected] |
+-------------------------------------------------------------------------------------------------------------------+
| Connection                                                                                                        |
| [USB Tethering]  [ADB USB Tunnel]  [Wi-Fi LAN IP]  | IP: [ 127.0.0.1  ] [Copy]  [Auto Detect IP]  [ Connect & Start ] |
+-------------------------------------------------------------------------------------------------------------------+
| Quick Modes (One-Click Presets)                                                                                   |
| [Meetings] [Online Class] [Streaming] [Snapshot] [Scan / OCR] [Security] [Fun Filter] [Pro Reset]                 |
+--------------------------------+---------------------------------------+------------------------------------------+
| Camera                         | Image Controls                        | Lighting                                 |
| +----------------------------+ | ISO:           [Auto v] [Switch: ON ] | Torch:               [Off] [Switch: OFF]  |
| | ⌜                        ⌝ | | Shutter:       [Auto v] [Switch: ON ] | Front Glow:          [Off] [Switch: OFF]  |
| |       CAMERA PREVIEW       | | White Balance: [Auto v] [Switch: ON ] | Screen Keep ON:       [On] [Switch: ON ]  |
| |       (Live Viewfinder)    | | Color FX:    [Normal v] [Switch: OFF] | Brightness:   [==|==============]   75%    |
| | ⌞                        ⌟ | |                                       | Color Temp:   [====|============] 5500K    |
| +----------------------------+ | [AF: Auto]  [Focus]  [EV -]  [EV +]   +------------------------------------------+
| [Front | Rear]  [Rotate]       | [Sync State]                          | More Controls                            |
| Resolution: [ 720p (1280x720) v]---------------------------------------+ [OBS Setup]   [Dependencies] [OEM Fix]   |
| Frame Rate: [ 30 FPS          v] Background                            | [Settings]    [Diagnostics]  [Uninstall] |
| Zoom: [-] [===|==============] [+] | [Pass-Through] [Blur] [Green Screen]   +------------------------------------------+
| [Ultra Photo]     [Mirror: OFF]| [Select Image] [Presets]              | Event Log                        [Clear] |
|                                | Workload: (o) GPU  ( ) Mobile         | [12:00:00] Otter Controller ready.       |
|                                |                                       | [12:00:01] USB Tunnel active on port 8089|
+--------------------------------+---------------------------------------+------------------------------------------+
```

### Launching the Desktop UI (One-Click Launchers)

#### Standard Launchers (With Console Logs)
- **Windows**: Double-click `run_windows.bat`
- **Linux**: Run `./run_linux.sh` (or `bash run_linux.sh`)
- **macOS**: Double-click `run_macos.command` in Finder (or `./run_macos.sh`)

#### Zero-Terminal Silent Launchers (No Command Prompt or Terminal Window)
- **Windows**: Double-click `run_windows_silent.vbs` (uses `pythonw.exe` without opening `cmd.exe`).
- **Linux**: Run `./run_linux_silent.sh` or double-click `otter.desktop` (uses freedesktop `Terminal=false`).
- **macOS**: Double-click `run_macos_silent.command` (detaches via AppleScript, closing Terminal.app immediately).

Or launch directly via Python:
```bash
python Dev/desktop/otter_app.py
# Or launch without terminal on Windows:
pythonw Dev/desktop/otter_app.py
```

---

## 3. How to Connect: USB Tethering vs. ADB vs. Wi-Fi (Step-by-Step)

### Method A: USB Tethering Connection (Recommended - Zero ADB / No Developer Mode Required)
USB Tethering uses Android's native hardware USB Ethernet driver (RNDIS / CDC-NCM) to create a direct high-speed wired connection between your phone and PC without requiring Developer Options, USB debugging, or ADB platform-tools:

1. **Connect USB Cable**:
   - Plug your phone into your PC using a standard USB data cable.
2. **Turn ON USB Tethering**:
   - On Android: Open **Settings** -> **Network & Internet** -> **Hotspot & Tethering** -> toggle ON **USB Tethering**.
   - *Shortcut*: In the Otter mobile app, tap or long-press the network status label to open Tethering settings directly.
3. **Start Mobile Stream**:
   - Tap **Start Stream** in the Otter mobile app. The top status bar will display `USB Tether: 192.168.42.129`.
4. **Connect on Desktop**:
   - In the Otter desktop controller, select **USB Tethering (No ADB)**.
   - Click **Connect & Start** (or **Auto Detect IP**).
   - Your studio-grade wired stream is live instantly with 0-latency.

### Method B: USB Cable via ADB (Alternative Wired Mode with Port Forwarding)
For users who prefer standard ADB port forwarding over USB:

1. **Enable Developer Options on Android**:
   - Open your phone's **Settings** -> **About Phone**.
   - Tap **Build Number** 7 times rapidly until you see the message *"You are now a developer!"*.
2. **Turn on USB Debugging**:
   - Navigate to **Settings** -> **System / Additional Settings** -> **Developer Options**.
   - Turn ON the toggle for **USB Debugging**.
3. **Connect USB Cable**:
   - Plug your phone into your PC using a standard USB data cable.
4. **Authorize Computer**:
   - A dialog will appear on your phone screen: *"Allow USB debugging?"*.
   - Check the box **"Always allow from this computer"** and tap **OK / Allow**.
5. **Start Otter Mobile App**:
   - Open Otter on your phone and tap the green **Start** button.
6. **Launch & Connect Desktop App**:
   - On PC, double-click `run_windows.bat` (or Linux `./run_linux.sh` / macOS `run_macos.command`).
   - Select **USB (ADB Tunnel)** and click **Connect & Start**.
   - The stream will initialize immediately and virtual camera feed is broadcast.

### Method C: Wi-Fi Connection (Wireless Convenience)
Allows wireless streaming over your local network without any cables attached.

1. **Connect to Same Network**:
   - Ensure your phone and PC are connected to the **SAME Wi-Fi router**.
   - *Tip*: Connect both to the **5GHz band** for maximum bitrate and lowest latency.
2. **Note IP Address on Phone**:
   - Open Otter on your phone.
   - Look at the top status text: it displays your phone's local network IP (e.g. `IP: 192.168.1.50`).
3. **Start on Mobile**:
   - Tap the green **Start** button on your phone.
4. **Configure Desktop Receiver**:
   - Launch Otter Desktop on PC.
   - Select the **Wi-Fi (LAN IP)** radio button.
   - Type your phone's IP address into the IP field.
   - Click **Connect & Start**.
5. **Ready**:
   - Virtual camera is now broadcasting wirelessly to all video applications.

### Method C: Android 14+ Native Hardware USB Webcam (Supported Devices)
On devices running Android 14 QPR1+ where the manufacturer included UVC gadget support (e.g. Google Pixel, Motorola):
1. Connect via USB cable with USB Debugging enabled.
2. In Otter Desktop under Tab 3 ("Dependencies & Setup"), click **Activate Android 14 USB Webcam**.
3. If supported by your ROM, the phone switches directly into a hardware USB Video Class (UVC) webcam without requiring receiver streaming.
4. If your OEM locked or stripped the driver (e.g. Vivo/iQOO, Samsung), Otter automatically notifies you and uses low-latency ADB tunnel mode instead.

---

## 4. How to Use with Streaming & Video Conferencing Apps

### OBS Studio
1. Open OBS Studio.
2. Under **Sources**, click `+` -> **Video Capture Device**.
3. Create a new source named `Otter Camera`.
4. Under **Device**, select `Unity Video Capture` OR `OBS Virtual Camera` (both receive the live Otter stream simultaneously).
5. Set Resolution/FPS Type to **Device Default** and click OK.

### Discord
1. Open Discord Settings (gear icon) -> **Voice & Video**.
2. Scroll to **Video Settings**.
3. In the **Camera** dropdown, select `OBS Virtual Camera` or `Unity Video Capture`.
4. Click **Test Video** to preview.

### Google Meet, Zoom & Microsoft Teams
1. In meeting settings (or before entering a call), open **Settings** -> **Video** -> **Camera**.
2. Select `OBS Virtual Camera` or `Unity Video Capture`.

### Web Browsers (Brave, Chrome, Firefox)
1. Go to `chrome://settings/content/camera` (or `brave://settings/content/camera`).
2. Set default camera to `OBS Virtual Camera` or `Unity Video Capture`.

---

## 4. Background Streaming & OEM Anti-Kill Fixes

Otter includes a dedicated Android `ForegroundService` with `PARTIAL_WAKE_LOCK` (`Lock Mode: ON`). When enabled, your phone screen can be locked or powered off and streaming will continue uninterrupted.

### OEM Specific Setup to Prevent Auto-Kill
Many Android manufacturers aggressively terminate background camera and network processes unless exempted:

- **Xiaomi (MIUI & HyperOS)**:
  1. Open **Settings** -> **Apps** -> **Manage Apps** -> **Otter**.
  2. Enable **Autostart**.
  3. Under **Battery Saver**, select **No restrictions**.
  4. In the app switcher, long-press Otter and tap the **Lock** (padlock) icon.

- **Samsung (One UI)**:
  1. Open **Settings** -> **Battery** -> **Background usage limits** -> **Never sleeping apps**.
  2. Tap `+` and add **Otter**.
  3. In **Settings** -> **Apps** -> **Otter** -> **Battery**, set to **Unrestricted**.

- **OPPO, OnePlus & Realme (ColorOS & OxygenOS)**:
  1. Long-press the Otter app icon -> **App info** -> **Battery usage**.
  2. Enable **Allow background activity** and **Allow auto-launch**.
  3. In the Recent Apps screen, tap the three dots on Otter and select **Lock**.

- **Vivo & iQOO (FuntouchOS)**:
  1. Open **Settings** -> **Battery** -> **High background power consumption**.
  2. Turn ON the toggle for **Otter**.

---

## 5. Python Desktop Dependencies & Installation

Otter provides both graphical and command-line package management with zero external dependencies required to launch the controller UI.

### Automated Installation via CLI
```bash
python Dev/desktop/manage_dependencies.py install
```

### Manual Installation
```bash
pip install -r Dev/desktop/requirements.txt
# OR
pip install opencv-python numpy pyvirtualcam
```

### Uninstallation
```bash
python Dev/desktop/manage_dependencies.py uninstall
# OR
pip uninstall -y opencv-python numpy pyvirtualcam
```

### Disclaimer & Liability Notice
> Automated package management runs standard pip commands targeting official PyPI packages (`opencv-python`, `numpy`, `pyvirtualcam`). The software and scripts are provided "AS IS", without warranty of any kind. Neither developer `spacecar` nor Otter is responsible for any system breaks, environment corruption, dependency conflicts, or data loss. Users may inspect requirements and install manually if preferred.

---

## 6. Lighting Controls: Hardware Flashlight & Front Screen Glow

Otter features adaptive lighting controls to maintain video visibility in dark environments:

### Hardware Flashlight / Torch (Rear Camera)
- **Automatic Capability Detection**: The mobile app inspects `CameraCharacteristics.FLASH_INFO_AVAILABLE`. If the active camera does not have an LED flash (or when flipped to the front camera), the button is disabled and displays `Torch: N/A`.
- **Strength / Brightness Tiers**:
  - On devices running Android 13+ (API 33+) supporting multi-level flash strength, tapping cycles through: `OFF` -> `Low` (33% strength) -> `High` (100% max hardware strength).
  - On older Android versions or binary-only flash devices, tapping toggles between `OFF` and `ON`.
- **Stream Persistence**: Hardware torch mode stays active throughout live video encoding using Camera2 `CaptureRequest.FLASH_MODE_TORCH`.
- **Remote Desktop Trigger**: The desktop controller includes a `Torch: Cycle` button to control the rear torch remotely over ADB / Wi-Fi.

### Front Screen Glow Ring Light (Front Camera)
- **Color Temperature & Tint**: When front camera is active in dim lighting, tapping `Glow` overlays a soft ring border around the viewfinder with adjustable color tones:
  - `OFF` -> `Warm` (soft incandescent 3000K) -> `Daylight` (cool blue 6500K) -> `Sunset` (amber golden hour) -> `White` (clean neutral studio light).
- **Auto Screen Brightness Boost**: When glow is activated, the app overrides window brightness to 100% (`BRIGHTNESS_OVERRIDE_FULL`), illuminating the user's face, and restores original brightness when turned off.
- **Remote Desktop Trigger**: The desktop controller includes a `Front Glow: Cycle` button to change color tones remotely.

---

## 7. Real-Time Focus & Manual Controls (Phone & Desktop Sync)

Otter provides pro-grade camera optics controls synced bidirectionally between the phone and the desktop controller:

### Auto Focus (AF) & Manual Focus (MF)
- **Auto Focus**: Continuous picture auto-focus (`CONTROL_AF_MODE_CONTINUOUS_PICTURE`) tracks subjects automatically.
- **Manual Focus**: Toggle `AF: Auto` to `AF: Manual` to lock focus distance.
- **Focus Distance Steps**: Tapping `Focus` cycles optical focus distance from `Focus: Inf` (infinity, diopters 0) through intermediate distances (macro and close-up) based on hardware `LENS_INFO_MINIMUM_FOCUS_DISTANCE`.
- **Desktop Sync**: The desktop app includes `AF: Auto/Manual` and `Focus: Inf/Macro` buttons. Changing settings on either device updates the other in real-time.

### Exposure Value Compensation (EV)
- **Step Adjustment**: Adjust brightness balance in challenging back-lit situations via `CONTROL_AE_EXPOSURE_COMPENSATION`.
- **Bidirectional Sync**: Real-time EV value (e.g., `-2.0`, `0.0`, `+2.0`) is updated across both phone and desktop interface simultaneously.

---

## 8. Virtual Background, Bokeh Blur, Chroma Green Screen & Wallpapers

Otter features an advanced dual-engine Virtual Background system providing privacy and professional streaming backdrops across both the Android app and the Desktop Client:

### Workload Routing: PC GPU/CPU Offload vs Mobile
- **PC GPU/CPU Offload (Recommended)**: The phone streams unadulterated high-definition video at 60 FPS while your desktop or laptop GPU handles background segmentation and compositing. Your phone stays cool with minimal battery consumption.
- **Mobile Device Processing**: Background processing is handled entirely on the mobile processor for standalone setups.

### Background Modes & Effects
1. **Pass-Through (Off)**: Raw, unaltered camera feed.
2. **Light Bokeh Blur (Portrait)**: Elegant portrait depth-of-field blur keeping the subject sharp while softly defocusing the room.
3. **Heavy Privacy Blur**: Maximum privacy blur obscuring confidential backgrounds, documents, and messy rooms.
4. **Solid Green Screen (Chroma Key)**: Replaces background with pure Chroma Key Green `(RGB 0, 255, 0)` for seamless keying inside OBS Studio, Zoom, Discord, or vMix.
5. **Custom Wallpaper Image**: Upload or select your own custom image from your phone gallery (`ACTION_GET_CONTENT`) or PC file browser (`.png`, `.jpg`, `.jpeg`, `.webp`).
6. **Built-in Presets**: Quick one-click wallpapers included in `wallpapers/`:
   - `Modern Office`: Contemporary executive open-office backdrop.
   - `Studio Bokeh`: Warm studio light spheres and clean depth.
   - `Minimalist Bookshelf`: Professional academic library look.
   - `Cozy Coffee Shop`: Warm café ambiance.

### Recommended Wallpaper Specifications
- **Aspect Ratio**: `16:9` widescreen (matches standard camera video output).
- **Resolutions**: `1920x1080` (1080p FHD) or `1280x720` (720p HD).
- **Supported Formats**: PNG, JPG, JPEG, WEBP.
- **Maximum File Size**: Under 15 MB.
- **Automatic Scaling**: Custom wallpapers are automatically scaled, cropped, and centered to match your stream resolution without distortion.


