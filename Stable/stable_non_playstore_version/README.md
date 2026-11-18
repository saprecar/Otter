# Otter - GitHub & Sideload Release Package (v1.1.0.0)

Standalone Android APK release packages designed for direct GitHub releases, sideloading, and independent distribution without Google Play Store dependencies.

---

## 1. Included Binaries
1. **`Otter-v1.1.0.0-signed.apk`**:
   - Ready-to-install APK signed with default Android release signing.
   - Recommended for direct sideloading, testing, and standard users.
   - Install command:
     ```bash
     adb install -r Otter-v1.1.0.0-signed.apk
     ```

2. **`Otter-v1.1.0.0-unsigned.apk`**:
   - Unsigned release binary containing pure compiled bytecode and resources.
   - Intended for developers and enterprises wanting to sign with their own official keystore or F-Droid builders.

---

## 2. Signing the Unsigned APK (Custom Keystore)
To sign `Otter-v1.1.0.0-unsigned.apk` with your own keystore using `apksigner`:

```bash
apksigner sign --ks your-keystore.jks --ks-key-alias your-alias --out Otter-custom-signed.apk Otter-v1.1.0.0-unsigned.apk
```

---

## 3. F-Droid Distribution & Metadata
Otter is open-source (MIT) and ready for F-Droid and IzzyOnDroid distribution:
- **F-Droid Metadata Recipe**: [org.understory.cambridge.yml](org.understory.cambridge.yml)
- **F-Droid Submission Guide**: [FDROID_SUBMISSION_GUIDE.md](FDROID_SUBMISSION_GUIDE.md)

---

## 3. Building From Source
```bash
# Windows
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.21.21-hotspot
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
gradlew.bat assembleRelease

# Linux / macOS
export JAVA_HOME=/path/to/jdk-17
export ANDROID_HOME=$HOME/Android/Sdk
./gradlew assembleRelease
```

---

## 4. Privacy & Legal Terms (Indian Law)
- **100% Local Peer-to-Peer**: No data, videos, or photos leave your local network. Zero developer data retention or cloud storage.
- **Data Deletion & Liability**: The developer retains zero user data, so server deletion is not applicable. The developer holds zero liability for local network packet loss, interception, or software bugs.
- **Mandatory Attribution**: All reuse or forks must credit original developer **spacecar**, name the project **Otter**, and link to **https://github.com/saprecar/Otter**.
- **Governing Law**: Republic of India (Information Technology Act, 2000 & Indian Contract Act, 1872).
- **Exclusive Jurisdiction**: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).
- **Contact**: `getspacecar@gmail.com` (Subject: `[Otter-Legal]`).
- **Master Consolidated Policy**: [`Policies And Agreement/POLICIES_AND_AGREEMENT.md`](../../Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md).
