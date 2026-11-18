# Google Play Console Data Safety & Declaration Guide (Otter)

**Developer**: spacecar  
**Repository**: https://github.com/saprecar/Otter  
**Contact**: getspacecar@gmail.com (Subject: `[Otter-Legal]`)  
**Jurisdiction**: Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005)  

---

- **App Public Name**: Otter
- **Application ID / Package Name**: `org.understory.cambridge` (Note: internal package name retained for backwards compatibility and keystore signature continuity)
- **Target SDK**: Android 16 (API Level 36)
- **Minimum SDK**: Android 5.0 (API Level 21)

---

## 1. Data Safety Questionnaire Answers

### Data Collection & Sharing
- **Does your app collect or share any user data?**: **NO**
- **Explanation**: Otter does not collect, record, process on remote developer servers, or share any personal data, user identifiers, device IDs, or media files.

### Data in Transit & Storage
- **Is all user data encrypted in transit?**: **NO**
- **Play Console Truthful Explanation**: Video frames travel strictly over local peer-to-peer physical USB cable (via ADB reverse tunnel) or local Wi-Fi router subnet using raw local TCP/IP sockets without an application-layer TLS certificate wrapper. Under Google Play Console's strict Data Safety definitions, local network socket communication without TLS must be answered as **No** for "encrypted in transit". No data is ever transmitted to external developer or cloud servers.
- **Does your app provide a way for users to request data deletion?**: **Not Applicable / No data stored** (Because developer infrastructure retains zero user data, deletion on developer servers is not applicable. All local cache, settings, and captures are managed directly on the user's local device).

---

## 2. Permissions Declarations & Play Console Justifications

### A. Camera (`android.permission.CAMERA`)
- **Category**: Core Functionality
- **Justification Statement**:
  > "Otter is a dedicated webcam and remote camera utility. Camera hardware access is the primary core feature of the application, required exclusively to preview and encode live video frames (H.264) and transmit them directly to the user's paired personal computer over local USB or Wi-Fi. No video or image data is retained or transmitted to any developer or third-party server."

### B. Foreground Service - Camera (`FOREGROUND_SERVICE_CAMERA`)
- **Target SDK**: Android 16 (API 36)
- **Service Type**: `camera` (`android:foregroundServiceType="camera"`)
- **Justification Statement**:
  > "Otter uses a foreground service of type 'camera' with an active, visible status-bar notification to ensure that user-initiated video streaming to their PC remains uninterrupted when switching applications or when the screen is dimmed/locked to save device power. The service runs strictly while active streaming is enabled by the user and terminates immediately upon tapping Stop."

### C. Network State & Sockets (`INTERNET`, `ACCESS_NETWORK_STATE`, `ACCESS_WIFI_STATE`)
- **Category**: Local Socket Communication
- **Justification Statement**:
  > "Used exclusively to bind and establish local peer-to-peer TCP/IP socket connections (Port 8089 for video and Port 8090/8081 for control RPC) between the Android device and the desktop client on the same local network subnet or via ADB reverse port forwarding. The app initiates zero connections to external public servers."

### D. Restricted Permissions Compliance (`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`)
- **Status**: **REMOVED from AndroidManifest.xml**
- **Policy Compliance**: To strictly adhere to Google Play's Restricted Permissions Policy, `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` is not requested in the manifest. The app guides the user to standard system settings via `Settings.ACTION_APPLICATION_DETAILS_SETTINGS` without triggering Play Store permission rejection.

---

## 3. Play Store Listing Privacy Policy URL
Use the official consolidated markdown policy on GitHub:
`https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md`
