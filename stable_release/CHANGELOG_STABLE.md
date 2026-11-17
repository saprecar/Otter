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
