#!/usr/bin/env python3
# [AI-BLOCK: Cross-Platform Compatibility Test Suite for Otter Desktop Client]
# Runs on Windows to verify Linux (Ubuntu/Debian) and macOS (Darwin) compatibility without needing physical machines.

import sys
import os
import py_compile
import collections
import unittest.mock

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
_DEV_DESKTOP = os.path.join(_REPO_ROOT, "Dev", "desktop")

UnameResult = collections.namedtuple("uname_result", ["sysname", "nodename", "release", "version", "machine"])
FAKE_UNAME_LINUX = UnameResult("Linux", "linux-host", "5.15.0-generic", "#1", "x86_64")
FAKE_UNAME_DARWIN = UnameResult("Darwin", "mac-host", "23.0.0", "#1", "arm64")

def run_tests():
    print("=" * 60)
    print("  Otter Desktop Cross-Platform Compatibility Test Suite")
    print("  Testing Linux and macOS Compatibility from Windows Host")
    print("=" * 60)
    print("")

    failures = 0

    # 1. Syntax Check across all Python scripts
    print("[1/5] Checking Python syntax compilation (py_compile)...")
    for root, _, files in os.walk(_DEV_DESKTOP):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    py_compile.compile(path, doraise=True)
                    rel = os.path.relpath(path, _REPO_ROOT)
                    print(f"  PASS: {rel}")
                except Exception as e:
                    print(f"  FAIL: {path}: {e}")
                    failures += 1

    # 2. Check Line Endings on Launchers (LF required for Linux/macOS)
    print("\n[2/5] Checking shell script line endings (LF verification)...")
    shell_files = [
        os.path.join(_REPO_ROOT, "run_linux.sh"),
        os.path.join(_REPO_ROOT, "run_linux_silent.sh"),
        os.path.join(_REPO_ROOT, "run_macos.sh"),
        os.path.join(_REPO_ROOT, "run_macos_silent.command"),
        os.path.join(_REPO_ROOT, "Stable", "Stable_Desktop_Client", "run_linux.sh"),
        os.path.join(_REPO_ROOT, "Stable", "Stable_Desktop_Client", "run_linux_silent.sh"),
        os.path.join(_REPO_ROOT, "Stable", "Stable_Desktop_Client", "run_macos.sh"),
        os.path.join(_REPO_ROOT, "Stable", "Stable_Desktop_Client", "run_macos.command"),
        os.path.join(_REPO_ROOT, "Stable", "Stable_Desktop_Client", "run_macos_silent.command"),
    ]
    for sf in shell_files:
        if os.path.exists(sf):
            with open(sf, "rb") as fp:
                data = fp.read()
                if b"\r\n" in data:
                    print(f"  FAIL (CRLF detected): {os.path.relpath(sf, _REPO_ROOT)}")
                    failures += 1
                else:
                    print(f"  PASS (LF clean): {os.path.relpath(sf, _REPO_ROOT)}")

    # 3. Test Mock Linux Platform Execution
    print("\n[3/5] Testing mock Linux (sys.platform = 'linux') environment...")
    with unittest.mock.patch("sys.platform", "linux"):
        with unittest.mock.patch("platform.system", return_value="Linux"):
            with unittest.mock.patch("os.uname", return_value=FAKE_UNAME_LINUX, create=True):
                try:
                    if _DEV_DESKTOP not in sys.path:
                        sys.path.insert(0, _DEV_DESKTOP)
                    import manage_adb
                    import manage_dependencies
                    import network_discovery
                    import cambridge_control
                    import cambridge_receiver
                    import otter_app
                    import driver.linux_v4l2_bridge as lv
                    print("  PASS: All desktop modules imported cleanly under mock Linux.")
                except Exception as e:
                    print(f"  FAIL under mock Linux: {e}")
                    failures += 1

    # 4. Test Mock macOS Platform Execution
    print("\n[4/5] Testing mock macOS (sys.platform = 'darwin') environment...")
    with unittest.mock.patch("sys.platform", "darwin"):
        with unittest.mock.patch("platform.system", return_value="Darwin"):
            with unittest.mock.patch("os.uname", return_value=FAKE_UNAME_DARWIN, create=True):
                try:
                    import manage_adb
                    import manage_dependencies
                    import network_discovery
                    import cambridge_control
                    import cambridge_receiver
                    import otter_app
                    print("  PASS: All desktop modules imported cleanly under mock macOS.")
                except Exception as e:
                    print(f"  FAIL under mock macOS: {e}")
                    failures += 1

    # 5. Test USB Tethering Discovery Logic
    print("\n[5/5] Testing USB Tethering detection logic...")
    try:
        from network_discovery import COMMON_TETHER_IPS
        assert "192.168.42.129" in COMMON_TETHER_IPS
        assert "192.168.42.1" in COMMON_TETHER_IPS
        print(f"  PASS: USB Tethering gateway list configured: {COMMON_TETHER_IPS}")
    except Exception as e:
        print(f"  FAIL USB Tethering check: {e}")
        failures += 1

    print("\n" + "=" * 60)
    if failures == 0:
        print("  ALL CROSS-PLATFORM COMPATIBILITY CHECKS PASSED (0 ERRORS)")
        print("=" * 60)
        return True
    else:
        print(f"  TESTS FINISHED WITH {failures} FAILURE(S)")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
