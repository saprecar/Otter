import os
import sys
import platform
import urllib.request
import zipfile
import shutil
import subprocess

# [AI-BLOCK: Standalone Google Android Platform Tools (ADB) Minimal Downloader & Manager]
# Downloads official lightweight platform-tools directly from Google servers (~15MB)
# without requiring heavy Android Studio (gigabytes).

PLATFORM_TOOLS_URLS = {
    "Windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
    "Darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip", # macOS
    "Linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
}

def get_bin_dir():
    # Store portable platform-tools in Dev/desktop/bin/platform-tools or local bin
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "bin")

def get_platform_tools_dir():
    return os.path.join(get_bin_dir(), "platform-tools")

def get_portable_adb_path():
    system = platform.system()
    adb_name = "adb.exe" if system == "Windows" else "adb"
    target_path = os.path.join(get_platform_tools_dir(), adb_name)
    if os.path.exists(target_path):
        return target_path
    return None

def check_adb_status():
    """
    Checks if ADB is available either globally in system PATH, in Android SDK, or in portable Otter bin.
    Returns: (is_available, adb_path, source_description)
    """
    # 1. Check portable downloaded ADB
    portable = get_portable_adb_path()
    if portable:
        return True, portable, "Otter Minimal Platform-Tools (Portable)"

    # 2. Check system PATH
    which_adb = shutil.which("adb")
    if which_adb:
        return True, which_adb, "System PATH"

    # 3. Check standard Android SDK platform-tools
    sdk_candidates = [
        os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
        r"C:\Android\Sdk\platform-tools\adb.exe",
        r"C:\Program Files (x86)\Android\android-sdk\platform-tools\adb.exe",
        os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
        os.path.expanduser("~/Android/Sdk/platform-tools/adb")
    ]
    for p in sdk_candidates:
        if os.path.exists(p):
            return True, p, "Android SDK"

    return False, None, "Not Found (Install ADB Minimal Tools)"

def download_and_extract_adb(progress_callback=None):
    """
    Downloads and extracts minimal official Android platform-tools from Google (~15MB).
    Runs non-blocking or with progress callback if provided.
    """
    system = platform.system()
    url = PLATFORM_TOOLS_URLS.get(system)
    if not url:
        raise RuntimeError(f"Unsupported operating system: {system}")

    bin_dir = get_bin_dir()
    os.makedirs(bin_dir, exist_ok=True)
    zip_dest = os.path.join(bin_dir, "platform-tools-latest.zip")

    if progress_callback:
        progress_callback("Connecting to dl.google.com for official Android Platform Tools...", 10)

    # Download official zip
    def _reporthook(block_num, block_size, total_size):
        if total_size > 0 and progress_callback:
            percent = int((block_num * block_size * 70) / total_size) + 10
            progress_callback(f"Downloading official Google ADB: {min(80, percent)}%", min(80, percent))

    try:
        urllib.request.urlretrieve(url, zip_dest, reporthook=_reporthook if progress_callback else None)
    except Exception as e:
        raise RuntimeError(f"Failed to download ADB from Google servers: {e}")

    if progress_callback:
        progress_callback("Extracting platform-tools to Otter portable bin...", 85)

    try:
        with zipfile.ZipFile(zip_dest, 'r') as zip_ref:
            zip_ref.extractall(bin_dir)
    except Exception as e:
        raise RuntimeError(f"Failed to extract platform-tools zip: {e}")
    finally:
        if os.path.exists(zip_dest):
            try:
                os.remove(zip_dest)
            except Exception:
                pass

    adb_path = get_portable_adb_path()
    if not adb_path:
        raise RuntimeError("Extraction completed but adb executable was not found.")

    # Make executable on Unix/macOS
    if system != "Windows":
        try:
            os.chmod(adb_path, 0o755)
        except Exception:
            pass

    if progress_callback:
        progress_callback("ADB Minimal Tools ready and verified!", 100)

    return adb_path

def uninstall_adb():
    """Removes the portable platform-tools folder to free up space."""
    pt_dir = get_platform_tools_dir()
    if os.path.exists(pt_dir):
        shutil.rmtree(pt_dir, ignore_errors=True)
        return True
    return False

if __name__ == "__main__":
    avail, path, desc = check_adb_status()
    print(f"ADB Available: {avail}")
    print(f"Path: {path}")
    print(f"Source: {desc}")
    if not avail:
        print("\nStarting download of minimal official Android Platform Tools...")
        download_and_extract_adb(lambda msg, pct: print(f"[{pct}%] {msg}"))
        avail, path, desc = check_adb_status()
        print(f"\nFinal status: {avail} -> {path} ({desc})")
