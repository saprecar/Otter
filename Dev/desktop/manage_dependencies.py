import sys
import subprocess
import os

DISCLAIMER = (
    "====================================================================\n"
    "DISCLAIMER & LIABILITY NOTICE:\n"
    "Automated package management runs standard pip commands targeting official\n"
    "PyPI packages (opencv-python, numpy, pyvirtualcam).\n"
    "The software and scripts are provided 'AS IS', WITHOUT WARRANTY OF ANY\n"
    "KIND. Neither the developer ('spacecar') nor Otter is responsible for\n"
    "any system breaks, environment corruption, dependency conflicts, or data loss.\n"
    "You may review requirements and install packages manually if preferred.\n"
    "===================================================================="
)

PACKAGES = ["opencv-python>=4.8.0", "numpy>=1.24.0", "pyvirtualcam>=0.11.0"]
PACKAGE_NAMES = ["opencv-python", "numpy", "pyvirtualcam"]

def check_dependencies():
    status = {}
    for mod_name, pkg_name in [("cv2", "opencv-python"), ("numpy", "numpy"), ("pyvirtualcam", "pyvirtualcam")]:
        try:
            __import__(mod_name)
            status[pkg_name] = True
        except ImportError:
            status[pkg_name] = False
    return status

def install_dependencies(auto_confirm=False):
    print(DISCLAIMER)
    if not auto_confirm:
        resp = input("\nDo you accept and wish to proceed with installation? [y/N]: ").strip().lower()
        if resp not in ["y", "yes"]:
            print("Installation cancelled by user.")
            return False

    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    cmd = [sys.executable, "-m", "pip", "install"]
    if os.path.exists(req_file):
        cmd.extend(["-r", req_file])
    else:
        cmd.extend(PACKAGES)

    print(f"\nExecuting: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\nAll dependencies installed successfully.")
        return True
    else:
        print("\nInstallation encountered errors. Please check your internet connection or install manually.")
        return False

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
    print(f"   {sys.executable} -m pip install -r Dev/desktop/requirements.txt")
    print("\n   OR install packages individually:")
    print("   pip install opencv-python numpy pyvirtualcam")
    print("\n4. To uninstall at any time:")
    print("   pip uninstall -y opencv-python numpy pyvirtualcam\n")

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
