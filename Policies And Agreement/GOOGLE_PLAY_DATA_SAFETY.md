# Google Play Console Data Safety & Declaration Guide (Otter)

**Developer**: spacecar  
**Repository**: https://github.com/saprecar/Otter  
**Contact**: getspacecar@gmail.com (Subject: `[Otter-Legal]`)  
**Jurisdiction**: Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005)  

---

## 1. Data Safety Questionnaire Answers

### Data Collection & Sharing
- **Does your app collect or share any user data?**: **NO**
- **Explanation**: Otter does not collect, record, process on remote developer servers, or share any personal data, user identifiers, device IDs, or media files.

### Data in Transit & Storage
- **Is all user data encrypted in transit?**: **Not Applicable / Yes** (Zero data is transmitted to developer servers; local Wi-Fi traffic travels across the user's private encrypted local area network or direct USB cable via ADB reverse tunnel).
- **Does your app provide a way for users to request data deletion?**: **Not Applicable / No data stored** (Because developer infrastructure retains zero user data, deletion on developer servers is not applicable. All local cache and recordings are managed and deleted directly on the user's local device).

---

## 2. Permissions Declarations & Play Console Justifications

### A. Camera (`android.permission.CAMERA`)
- **Category**: Core Functionality
- **Justification Statement**:
  > "Otter is a dedicated webcam and remote camera utility. Camera hardware access is the primary core feature of the application, required exclusively to preview and encode live video frames (H.264) and transmit them directly to the user's paired personal computer over local USB or Wi-Fi. No video or image data is retained or transmitted to any developer or third-party server."

### B. Foreground Service - Camera (`FOREGROUND_SERVICE_CAMERA`)
- **Target SDK**: Android 14 (API 34)
- **Service Type**: `camera`
- **Justification Statement**:
  > "Otter uses a foreground service of type 'camera' with an active, visible status-bar notification to ensure that user-initiated video streaming to their PC remains uninterrupted when switching applications or when the screen is locked. The service runs strictly while active streaming is enabled by the user and terminates immediately upon tapping Stop."

### C. Network State & Sockets (`INTERNET`, `ACCESS_NETWORK_STATE`)
- **Category**: Local Socket Communication
- **Justification Statement**:
  > "Used exclusively to bind and establish local peer-to-peer TCP/IP socket connections (Port 8089 for video and Port 8090/8081 for control RPC) between the Android device and the desktop client on the same local network subnet or via ADB reverse port forwarding. The app initiates zero connections to external public servers."

---

## 3. Play Store Listing Privacy Policy URL
Use the official consolidated markdown policy on GitHub:
`https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md`
