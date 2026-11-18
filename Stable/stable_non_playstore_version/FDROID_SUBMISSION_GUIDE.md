# F-Droid & IzzyOnDroid Publication Guide

Step-by-step instructions and ready-to-copy submission templates to publish Otter to both the official F-Droid Main Repository and the IzzyOnDroid F-Droid Repository.

---

## Part 1: Prerequisites on GitHub

Before submitting to either repository, you need to push your code and create a tagged GitHub Release:

### Step 1.1: Push Commits & Create Tag
Run these commands in PowerShell or terminal:
```bash
git tag -a v1.2.0.0 -m "Otter Release v1.2.0.0"
git push origin main
git push origin v1.2.0.0
```

### Step 1.2: Publish GitHub Release
1. Open [https://github.com/saprecar/Otter/releases/new](https://github.com/saprecar/Otter/releases/new).
2. Choose existing tag: `v1.2.0.0`.
3. Release title: `Otter v1.2.0.0`
4. Attach binary: [Otter_Non_Playstore_Signed.apk](app/release/Otter_Non_Playstore_Signed.apk)
5. Paste Release Description:
```markdown
### Otter v1.2.0.0

High-definition virtual webcam and remote camera controller for PC over USB and Wi-Fi.

#### What's New
- Extended legacy device support: Android 5.0 (API Level 21, Lollipop) up to Android 16 (API Level 36, Baklava).
- USB Tethering Mode: Direct wired streaming without requiring ADB or Developer Options.
- Dual Virtual Background Engine: Real-time background replacement with PC GPU/CPU offload.
- Smart Power Management: Keep Screen On toggle (`FLAG_KEEP_SCREEN_ON`) and Dim Display mode.
- Pro Manual Camera Controls: Manual ISO, Shutter Speed, Focus distance, and EV steppers.
- Full-Resolution Ultra Photo capture (uncompressed raw sensor capture).
- 100% Peer-to-Peer, Zero-Cloud, Zero-Telemetry architecture.

#### Downloads & Integrity
- APK: `Otter_Non_Playstore_Signed.apk` (Signed Release)
- License: MIT License
- Source Code: https://github.com/saprecar/Otter
```
6. Click **Publish release**.

---

## Part 2: Submit to IzzyOnDroid (Direct APK from GitHub)

IzzyOnDroid indexes APKs directly from your GitHub Releases page without compiling from source.

### Submission Steps:
1. Open the IzzyOnDroid Inclusion Tracker:
   [https://gitlab.com/IzzyOnDroid/repo/-/issues/new?issuable_template=Inclusion](https://gitlab.com/IzzyOnDroid/repo/-/issues/new?issuable_template=Inclusion)
2. Fill out the issue form:

```text
Issue Title:
Inclusion request: Otter (org.understory.cambridge)

Issue Body:
- Application Name: Otter
- Package Name: org.understory.cambridge
- License: MIT
- Source Code Repository: https://github.com/saprecar/Otter
- Issue Tracker: https://github.com/saprecar/Otter/issues
- Release Tag Pattern: v1.2.0.0 (or v*)
- APK Download URL: https://github.com/saprecar/Otter/releases/download/v1.2.0.0/Otter_Non_Playstore_Signed.apk
- Summary: High-definition PC webcam and remote camera controller over USB or Wi-Fi
- Description: Otter turns your Android smartphone into a studio-grade PC webcam streaming up to 1080p 60 FPS over USB (ADB non-root) or local Wi-Fi with 100% private P2P sockets, Pro manual optics, dual virtual background engine, and battery saver display dimming.
- Fastlane Metadata: Present in repository at fastlane/metadata/android/en-US/ (icon, feature graphic, and screenshots).
```
3. Submit the issue. IzzyOnDroid typically approves and adds your repository within 24 to 48 hours.

---

## Part 3: Submit to Official F-Droid Main Repository (f-droid.org)

The official F-Droid repository builds Otter from source on their isolated build servers.

### Submission Steps:
1. Log in to GitLab at [https://gitlab.com](https://gitlab.com).
2. Fork the official `fdroiddata` repository: [https://gitlab.com/fdroid/fdroiddata](https://gitlab.com/fdroid/fdroiddata).
3. In your fork, navigate to the `metadata/` directory.
4. Click **(+) > New file** and name it:
   `metadata/org.understory.cambridge.yml`
5. Paste the entire content of [org.understory.cambridge.yml](org.understory.cambridge.yml):

```yaml
Categories:
  - Multimedia
  - System
License: MIT
AuthorName: spacecar
AuthorEmail: getspacecar@gmail.com
SourceCode: https://github.com/saprecar/Otter
IssueTracker: https://github.com/saprecar/Otter/issues
Changelog: https://github.com/saprecar/Otter/blob/main/stable_release/CHANGELOG_STABLE.md

Name: Otter
Summary: High-definition PC webcam and remote camera controller over USB or Wi-Fi

Description: |-
  Otter turns your Android device into a high-performance, studio-grade PC webcam.
  Stream up to 1080p 60 FPS video directly to Zoom, Microsoft Teams, Google Meet,
  OBS Studio, and Discord with ultra-low latency over USB or local Wi-Fi.

  Key Features:
  - 1080p 60 FPS hardware-accelerated H.264 streaming
  - Low-latency USB ADB auto-tunneling and local Wi-Fi mode
  - Pro Manual Optics: ISO, Shutter, Manual Focus distance, EV compensation, White Balance
  - Dual Virtual Background Engine with PC GPU/CPU Offload
  - Keep Screen On toggle and Dim Display power saver
  - Full-resolution uncompressed Ultra Photo capture
  - 100% Peer-to-Peer, Zero-Cloud, Zero-Telemetry architecture

RepoType: git
Repo: https://github.com/saprecar/Otter.git

Builds:
  - versionName: 1.1.0.0
    versionCode: 2
    commit: v1.1.0.0
    subdir: Stable/stable_non_playstore_version/app
    gradle:
      - yes

  - versionName: 1.2.0.0
    versionCode: 4
    commit: v1.2.0.0
    subdir: Stable/stable_non_playstore_version/app
    gradle:
      - yes

AutoUpdateMode: Version
UpdateCheckMode: Tags
CurrentVersion: 1.2.0.0
CurrentVersionCode: 4
```

6. Commit the file with message: `Add org.understory.cambridge (Otter)`.
7. Open a Merge Request against `fdroid/fdroiddata:master`:
   - Title: `New app: org.understory.cambridge (Otter)`
   - Description:
```markdown
### Package: org.understory.cambridge (Otter)

- [x] The source repository exists and is publicly accessible.
- [x] Released under approved open source license (MIT).
- [x] No proprietary blobs, tracking SDKs, or remote analytics.
- [x] Pure open-source dependencies (AndroidX).
- [x] Source build instructions verified with Gradle.

**App Name**: Otter
**Summary**: High-definition PC webcam and remote camera controller over USB or Wi-Fi
**Source Code**: https://github.com/saprecar/Otter
**License**: MIT
```
8. The F-Droid automated check bot (`fdroid lint` and CI build runner) will verify the recipe. Once approved by F-Droid maintainers, Otter will be indexed in the official F-Droid store.
