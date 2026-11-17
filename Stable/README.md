# Otter Stable Release (v1.1.0.0)

Production-ready release packages for the Otter Virtual Camera and Remote Controller System, separated into dedicated distributions for Google Play Store compliance, GitHub / Sideloading, and Desktop Clients.

---

## 1. Directory Structure

```text
Stable/
├── Stable_Desktop_Client/            # Standalone desktop controller (Windows, macOS, Linux)
│   ├── driver/                       # DirectShow virtual webcam drivers and bridges
│   ├── otter_app.py                  # Main desktop GUI application (Pro sliders & Auto locks)
│   ├── cambridge_control.py          # Camera2 remote control TCP client
│   ├── cambridge_receiver.py         # Real-time H.264 video decoder & virtual cam feeder
│   ├── manage_adb.py                 # Portable Google ADB minimal tools manager
│   ├── manage_dependencies.py        # Auto-dependency installer
│   ├── network_discovery.py          # LAN camera discovery
│   ├── requirements.txt              # Python dependencies
│   ├── run_windows.bat               # 1-click Windows launcher (runs as root)
│   ├── run_linux.sh                  # 1-click Linux launcher (runs as root)
│   ├── run_macos.command             # 1-click macOS launcher (runs as root)
│   ├── run_macos.sh                  # Terminal macOS launcher
│   └── README.md                     # Desktop client guide
│
├── stable_playstore_version/         # Google Play Store Distribution Package
│   ├── app/                          # Android source tree (versionCode 2, versionName 1.1.0.0)
│   ├── gradle/                       # Gradle wrapper
│   ├── Otter-v1.1.0.0.aab            # Pre-compiled Android App Bundle for Play Store
│   └── README.md                     # Google Play build and submission guide
│
└── stable_non_playstore_version/     # GitHub / Sideload Distribution Package
    ├── app/                          # Android source tree (versionCode 2, versionName 1.1.0.0)
    ├── gradle/                       # Gradle wrapper
    ├── Otter-v1.1.0.0-signed.apk     # Pre-signed release APK for instant sideloading
    ├── Otter-v1.1.0.0-unsigned.apk   # Pure unsigned release APK for custom signing
    └── README.md                     # Sideload installation & custom signing guide
```

All legal policies, terms of service, user agreements, and Google Play Data Safety declarations are consolidated in the universal [`Policies And Agreement/`](../Policies%20And%20Agreement/) folder.

---

## 2. Quick Start

### A. Desktop Client
Run the launcher script corresponding to your operating system directly from `Stable_Desktop_Client/`:
- **Windows**: Double-click `run_windows.bat`
- **Linux**: Execute `./run_linux.sh`
- **macOS**: Double-click `run_macos.command` or run `./run_macos.sh`

### B. Play Store Version
Follow `Stable/stable_playstore_version/README.md` to upload `Otter-v1.1.0.0.aab` to Google Play Console, declaring zero data collection and linking the consolidated policy.

### C. GitHub Sideload Version
Install `Otter-v1.1.0.0-signed.apk` directly via ADB:
```bash
adb install -r Stable/stable_non_playstore_version/Otter-v1.1.0.0-signed.apk
```
Or transfer `Otter-v1.1.0.0-signed.apk` to phone storage and install via file manager.

---

## 3. Legal and Policy Disclaimers (Indian Law)
- **Local Peer-to-Peer Operation**: Otter does not operate cloud servers. All video and RPC controls remain on the user's local network (USB ADB or local Wi-Fi). Zero developer data retention.
- **Data Deletion & Liability**: The developer retains zero user data, so server deletion is not applicable. The developer holds zero liability for local network packet loss, interception, or software bugs.
- **Mandatory Attribution**: All reuse or forks must credit original developer **spacecar**, name the project **Otter**, and link to **https://github.com/saprecar/Otter**.
- **Governing Law**: Republic of India (Information Technology Act, 2000 & Indian Contract Act, 1872).
- **Exclusive Jurisdiction**: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).
- **Contact**: **getspacecar@gmail.com** (Mandatory subject line: `[Otter-Legal]` or `[Otter-Inquiry]`).
