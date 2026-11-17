# Privacy Policy (Otter Camera App)

**Effective Date:** November 17, 2026  
**Developer:** spacecar | **Repository:** https://github.com/saprecar/Otter  
**Contact Email:** getspacecar@gmail.com (Mandatory Subject Line: `[Otter-Policy]`)  
**Governing Law:** Republic of India (Information Technology Act, 2000 & SPDI Rules)  
**Jurisdiction:** Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005)  

---

> [!NOTE]
> This Privacy Policy forms an integral section of the Master Consolidated Policy available at [`POLICIES_AND_AGREEMENT.md`](POLICIES_AND_AGREEMENT.md) and [`policies_and_agreement.html`](policies_and_agreement.html).

---

## 1. Zero Developer Data Collection (100% Local P2P)
- **Zero Cloud Ingestion**: The developer does not operate servers, databases, or analytics services for Otter.
- **Zero Personal Data**: We do not collect, store, monetize, or transmit your name, email, phone number, location, contacts, or device identifiers.
- **Local Video Streams**: Video frames are encoded on your local device (`MediaCodec`) and sent directly to your paired computer via USB (`adb reverse`) or your local Wi-Fi subnet. No video or still photos are ever uploaded to developer servers.
- **Data Deletion Inapplicability**: Because the developer ingests and retains ZERO data, data deletion requests cannot be executed on developer servers. Local app cache and recordings are managed and deleted directly on the user's local device.

---

## 2. Device Permissions
1. **Camera (`android.permission.CAMERA`)**: Core functionality. Accesses hardware camera sensors to display live viewfinders, encode H.264 video streams, and capture high-resolution photos upon user command. Never activated covertly in the background.
2. **Foreground Service (`FOREGROUND_SERVICE_CAMERA`)**: Required on Android 14+ with an active notification to maintain persistent video streaming while the screen is locked or switching tasks.
3. **Local Sockets (`INTERNET`, `ACCESS_NETWORK_STATE`)**: Used exclusively to establish local peer-to-peer TCP/IP sockets (Port 8089 for video, Port 8090/8081 for control RPC) between your phone and your paired PC.
4. **Notifications (`POST_NOTIFICATIONS`)**: Displays status-bar indicator while streaming is active.

---

## 3. Third-Party Platform, Store & OEM Disclaimers
- **Google Play Store / Android OS Telemetry**: Google LLC may collect standard operating system diagnostics in accordance with Google's Privacy Policy. Otter contains zero developer tracking SDKs.
- **Device Manufacturer (OEM) Telemetry**: Device vendors (MIUI, HyperOS, ColorOS, Funtouch OS, One UI) collect their own system diagnostics, which are entirely outside developer control.

---

## 4. Limitation of Liability
The software is provided "AS IS" without warranties. The developer bears zero liability for data leakage occurring over unsecured local networks, hardware overheating, or software bugs.

---

## 5. Contact & Grievance Protocol
- **Primary Channel**: Official GitHub Repository Issues at https://github.com/saprecar/Otter/issues
- **Email**: getspacecar@gmail.com with mandatory subject tag: `[Otter-Policy]` or `[Otter-Legal]`.
- **Grievance Jurisdiction**: Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).
