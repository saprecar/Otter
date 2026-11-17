import sys
import subprocess
import os

DISCLAIMER = (
    "====================================================================\n"
    "DISCLAIMER & LIABILITY NOTICE:\n"
    "Automated package management runs standard pip commands targeting official\n"
    "PyPI packages (opencv-python, numpy).\n"
    "The software and scripts are provided 'AS IS', WITHOUT WARRANTY OF ANY\n"
    "KIND. Neither the developer ('spacecar') nor Otter is responsible for\n"
    "any system breaks, environment corruption, dependency conflicts, or data loss.\n"
    "You may review requirements and install packages manually if preferred.\n"
    "===================================================================="
)

PACKAGES = ["opencv-python>=4.8.0", "numpy>=1.24.0", "imageio-ffmpeg>=0.4.8"]
PACKAGE_NAMES = ["opencv-python", "numpy", "imageio-ffmpeg"]

def check_dependencies():
    status = {}
    for mod_name, pkg_name in [("cv2", "opencv-python"), ("numpy", "numpy"), ("imageio_ffmpeg", "imageio-ffmpeg")]:
        try:
            __import__(mod_name)
            status[pkg_name] = True
        except ImportError:
            status[pkg_name] = False
    return status

def install_dependencies(auto_confirm=False, log_callback=None):
    if log_callback:
        log_callback("Installing required Python packages (opencv-python, numpy)...")

    cmd = [sys.executable, "-m", "pip", "install"] + PACKAGES
    if log_callback:
        log_callback(f"Executing: {' '.join(cmd)}")
    print(f"\nExecuting: {' '.join(cmd)}")
    res = subprocess.run(cmd)

    if res.returncode == 0:
        msg = "All required Python dependencies (opencv-python, numpy) are installed and ready!"
        if log_callback:
            log_callback(msg)
        return True, msg
    else:
        err = "Failed to install Python packages. Please verify your internet connection or install manually."
        if log_callback:
            log_callback(err)
        return False, err

def uninstall_dependencies(auto_confirm=False):
    print(DISCLAIMER)
    if not auto_confirm:
        resp = input("\nAre you sure you want to uninstall Otter dependencies? [y/N]: ").strip().lower()
        if resp not in ["y", "yes"]:
            print("Uninstall cancelled.")
            return False

    cmd = [sys.executable, "-m", "pip", "uninstall", "-y"] + PACKAGE_NAMES
    print(f"\nExecuting: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\nDependencies uninstalled cleanly.")
        return True
    else:
        print("\nUninstall completed with warnings.")
        return False

def print_manual_instructions():
    print(DISCLAIMER)
    print("\n--- Manual Installation Instructions ---")
    print("1. Open your terminal or Command Prompt.")
    print("2. Ensure Python 3.8+ and pip are installed.")
    print("3. Run the following command:\n")
    print(f"   {sys.executable} -m pip install -r requirements.txt")
    print("\n   OR install packages individually:")
    print("   pip install opencv-python numpy")
    print("\n4. To uninstall at any time:")
    print("   pip uninstall -y opencv-python numpy\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Otter Desktop Dependency Manager")
    parser.add_argument("action", choices=["check", "install", "uninstall", "manual"], default="check", nargs="?")
    parser.add_argument("--yes", action="store_true", help="Accept disclaimer and auto-confirm")
    args = parser.parse_args()

    if args.action == "check":
        status = check_dependencies()
        print("Otter Dependency Status:")
        for pkg, installed in status.items():
            print(f"  - {pkg}: {'INSTALLED' if installed else 'MISSING'}")
    elif args.action == "install":
        install_dependencies(auto_confirm=args.yes)
    elif args.action == "uninstall":
        uninstall_dependencies(auto_confirm=args.yes)
    elif args.action == "manual":
        print_manual_instructions()
