# Otter - Google Play Store Release Package (v1.2.0.0)

Production Android package structured and compliant with the latest Google Play Store policies and Indian IT laws.

---

## 1. How the Play Store Version Differs from GitHub / Sideload Version

| Feature / Requirement | Google Play Store Version | GitHub / Sideload Version |
| :--- | :--- | :--- |
| **Package Format** | Android App Bundle (`.aab`) | Standalone APKs (Signed & Unsigned) |
| **Signing Mechanism** | Google Play App Signing (Upload Key / Keystore) | Self-signed or developer signed |
| **Target SDK** | Target SDK 36 (Android 16, Baklava) | Target SDK 36 (Android 16, Baklava) |
| **Privacy Compliance** | In-App Privacy Policy Link + Public URL Required | Embedded Offline Policy |
| **Data Safety Section** | Mandatory Play Console Data Safety Submission | Not required |
| **Foreground Service Declaration** | Explicit `FOREGROUND_SERVICE_CAMERA` Justification | Local AndroidManifest declaration |
| **Updates & Distribution** | Google Play Developer Console | GitHub Releases / Direct APK Download |

---

## 2. Google Play Policy & Legal Compliance

1. **Zero Developer Data Collection**:
   - Otter does NOT collect, store, transmit, or sell any user data, biometric identifiers, camera feeds, or recordings.
   - All video encoding and RPC control occurs strictly over direct local peer-to-peer channels (USB cable via ADB or direct local Wi-Fi subnet).

2. **Operating System & Store Analytics Disclosure**:
   - Google LLC may collect standard device telemetry and crash reports through Google Play Services in accordance with Google's Privacy Policy. Otter contains zero proprietary tracking SDKs.

3. **Indian Law & Exclusive Jurisdiction**:
   - Governed by the Laws of the Republic of India (Information Technology Act, 2000 & Indian Contract Act, 1872).
   - Exclusive jurisdiction: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).

4. **Disclaimer of Liability & Data Loss**:
   - The software is provided "AS-IS" with all faults. Zero developer data is ingested, so server deletion is not applicable. Developers bear zero liability for data in transit, local network packet loss, hardware overheating, or software bugs.
   - Contact: `getspacecar@gmail.com` (Subject: `[Otter-Legal]`).

---

## 3. Master Consolidated Policy Reference
All legal policies, terms, and Play Store declarations are located in the universal repository folder:
- Master Policy: [`Policies And Agreement/POLICIES_AND_AGREEMENT.md`](../../Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md)
- Data Safety Guide: [`Policies And Agreement/GOOGLE_PLAY_DATA_SAFETY.md`](../../Policies%20And%20Agreement/GOOGLE_PLAY_DATA_SAFETY.md)
- Attribution: [`Policies And Agreement/ATTRIBUTION_AND_LICENSES.md`](../../Policies%20And%20Agreement/ATTRIBUTION_AND_LICENSES.md)

---

## 4. Building the Android App Bundle (`.aab`)

To generate the `.aab` bundle for Google Play Console submission:

```bash
# On Windows
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.21.21-hotspot
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
gradlew.bat bundleRelease

# On Linux / macOS
export JAVA_HOME=/path/to/jdk-17
export ANDROID_HOME=$HOME/Android/Sdk
./gradlew bundleRelease
```

The output bundle will be located at:
`app/build/outputs/bundle/release/app-release.aab`
