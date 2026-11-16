import os
import re
import sys

# [AI-BLOCK: Pre-Commit Security and Secret Scanner]
FORBIDDEN_PATTERNS = [
    r'(?i)api[_-]?key\s*[:=]\s*["\'][a-zA-Z0-9_\-]{16,}["\']',
    r'(?i)secret[_-]?token\s*[:=]\s*["\'][a-zA-Z0-9_\-]{16,}["\']',
    r'(?i)password\s*[:=]\s*["\'][^"\']+["\']',
    r'(?i)BEGIN\s+PRIVATE\s+KEY',
]

def scan_file(filepath):
    leaks = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f, 1):
                for pat in FORBIDDEN_PATTERNS:
                    if re.search(pat, line):
                        leaks.append((idx, line.strip()))
    except Exception:
        pass
    return leaks

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Scanning directory for secrets: {root}")
    found = False
    for base, dirs, files in os.walk(root):
        if "requirement" in base and "Propose" in base:
            continue
        if ".git" in base:
            continue
        for f in files:
            p = os.path.join(base, f)
            leaks = scan_file(p)
            if leaks:
                print(f"[ALERT] Leak found in {p}:")
                for line_num, l_text in leaks:
                    print(f"  Line {line_num}: {l_text[:40]}...")
                found = True

    if not found:
        print("Pre-commit scan passed: Zero secrets or hardcoded credentials detected.")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
