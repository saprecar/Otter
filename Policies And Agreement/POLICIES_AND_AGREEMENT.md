# Universal Consolidated Policies, Terms & User Agreement

**Project**: Otter Virtual Camera & Remote Control Suite  
**Developer**: spacecar  
**Repository**: https://github.com/saprecar/Otter  
**Contact Email**: getspacecar@gmail.com  
**Governing Law**: Republic of India (Information Technology Act, 2000 & Indian Contract Act, 1872)  
**Jurisdiction**: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005)  
**Effective Date**: November 17, 2026  
**Last Updated**: November 17, 2026  

---

## 1. Scope & Unified Acceptance
This document serves as the sole, consolidated Master Policy governing the use of the Otter Camera software suite ("Otter", "the Application", "the Software") across all distributions (Google Play Store version, GitHub standalone release, Android APK/AAB packages, and PC Desktop Client for Windows, Linux, and macOS).

By downloading, installing, launching, or using any component of Otter, you explicitly agree to be bound by all terms, disclaimers, and conditions set forth herein. If you do not agree to every clause, you must immediately decline and terminate use.

---

## 2. Mandatory Attribution Clause
Otter is open-source software created by spacecar. Any distribution, modification, fork, derivation, packaging, or integration of Otter (or any of its source code, assets, UI designs, or network architecture), whether for non-commercial or commercial purposes, is strictly conditional upon retaining full attribution:

1. **Original Copyright & Credit**: The original copyright notice and explicit credit to developer **spacecar** must remain prominent and intact in all source files, about screens, and documentation.
2. **Project Identity**: The application name **Otter** must be referenced as the underlying technology.
3. **Repository Link**: A direct, clickable link to the official repository (**https://github.com/saprecar/Otter**) must be included in user-accessible documentation and application information screens.

---

## 3. Privacy Policy & Zero Developer Data Retention
Otter operates strictly on a **100% Local Peer-to-Peer (P2P)** architecture:

1. **Zero Developer Data Ingestion**:
   - The developer does NOT operate cloud servers, relay databases, or central tracking endpoints.
   - The developer does NOT collect, harvest, log, monitor, monetize, or sell any personal data, biometric records, camera feeds, photos, IP addresses, or device identifiers.
2. **Local Frame Encoding & Socket Transmission**:
   - Camera video is encoded in real-time directly on hardware (`MediaCodec` on Android) and transmitted directly to your paired computer via local USB reverse tethering (`adb reverse`) or a local Wi-Fi subnet socket (Port 8089 for video, Port 8090/8081 for control RPC).
   - No audio, video, or still capture data is ever routed through external developer servers.
3. **Data Deletion Inapplicability**:
   - Because the developer ingests and retains ZERO user data on developer infrastructure, user data deletion requests cannot be executed on developer servers, as no data exists to be deleted.
   - All local application cache, settings, and still captures are entirely under the user's direct custody and can be cleared instantly via standard device file managers or Android Settings -> Apps -> Otter -> Clear Data.

---

## 4. Third-Party Platform, Store & OEM Disclaimers
Otter contains zero developer analytics SDKs or advertising trackers. However, when using third-party operating systems and distribution channels:

1. **Google Play Store & Android OS Diagnostics**:
   - If installed via Google Play, Google LLC may collect standard device telemetry, installation metrics, and platform crash logs via Google Play Services in accordance with the [Google Privacy Policy](https://policies.google.com/privacy). This telemetry is processed exclusively by Google and is entirely outside the custody, knowledge, or liability of Otter developers.
2. **Device Manufacturer (OEM) Telemetry & Battery Restrictions**:
   - Android original equipment manufacturers (including but not limited to Xiaomi MIUI/HyperOS, Oppo/Realme ColorOS, Vivo/iQOO Funtouch OS, and Samsung One UI) operate proprietary system managers that monitor background battery consumption, memory usage, and autostart permissions.
   - Otter provides user guidance to prevent premature service termination, but the developer holds no responsibility or liability for how OEM operating systems collect diagnostics, throttle background tasks, or terminate sockets.

---

## 5. Absolute Disclaimer of Warranties & Limitation of Liability
TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW:

1. **"AS-IS" Provision**:
   - The Software is provided strictly "AS IS", "AS AVAILABLE", and "WITH ALL FAULTS", without warranty of any kind, whether express, implied, statutory, or otherwise.
2. **Zero Liability for Data Leakage or Transmission Interception**:
   - Video streaming occurs across local transmission channels chosen and configured by the user. The developer shall have ZERO liability for any unauthorized network sniffing, man-in-the-middle interception, data leakage, or security breach occurring over unsecured local networks, open public Wi-Fi, or compromised personal computers.
3. **Zero Liability for Software Bugs & Hardware Stress**:
   - The developer shall NOT be liable for application crashes, encoding glitches, camera sensor lockups, system freezes, device heating, battery degradation, or data corruption resulting from continuous high-resolution camera streaming.
4. **Indemnification**:
   - You agree to indemnify, defend, and hold harmless developer spacecar and contributors from any claims, damages, liabilities, or expenses arising out of your operation or misuse of the Software.

---

## 6. Prohibited Surveillance & Misuse
In accordance with Section 66E and Section 67 of the Indian Information Technology Act, 2000, you are strictly prohibited from using Otter:
- To conduct clandestine, unauthorized surveillance, voyeurism, or recording of any person without their explicit knowledge and affirmative consent.
- In life-support, emergency response, hazardous, or mission-critical environments where software failure could lead to personal injury or property damage.

---

## 7. Governing Law & Exclusive Jurisdiction
This Agreement, Privacy Policy, and any disputes, controversies, or claims arising out of or in connection with Otter shall be governed by, interpreted, and enforced in accordance with the **Laws of the Republic of India**, including the Information Technology Act, 2000, and the Indian Contract Act, 1872.

Any legal suit, action, or proceeding arising out of or related to Otter shall be instituted exclusively in the **Competent Courts located at Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005)**.

---

## 8. Official Contact Protocol
To ensure secure and prioritized handling, official inquiries, legal notices, or feedback must follow this protocol:

- **Primary Contact Channel**: Official GitHub Repository Issues & Discussions at **https://github.com/saprecar/Otter**
- **Email Contact**: **getspacecar@gmail.com**
- **Mandatory Email Subject Line**: Any email inquiry MUST begin with one of the following exact tags in the subject line:
  - `[Otter-Legal]`
  - `[Otter-Policy]`
  - `[Otter-Inquiry]`
  - `[Otter-Support]`
  *Inquiries submitted without the designated subject tag are subject to automated filtering.*
