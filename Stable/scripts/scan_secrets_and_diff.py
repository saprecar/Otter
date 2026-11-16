#!/usr/bin/env python3
# [AI-BLOCK: Module Docstring & Imports]
"""
Scan code for secrets, API tokens, credentials, and protected directory access.
Checks git status to ensure only revised files are processed.
"""

import os
import re
import sys
import subprocess

# [AI-BLOCK: Detection Patterns & Forbidden Paths]
SUSPICIOUS_PATTERNS = [
    (r"(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer\s+[a-z0-9_\-\.]+)", "Possible API/Auth Token"),
    (r"ghp_[0-9a-zA-Z]{36}", "GitHub Personal Access Token"),
    (r"gho_[0-9a-zA-Z]{36}", "GitHub OAuth Access Token"),
    (r"sk-[a-zA-Z0-9]{32,}", "OpenAI/Generic Secret Key"),
    (r"AIza[0-9A-Za-z\\-_]{35}", "Google API Key"),
    (r"-----BEGIN (RSA|EC|DSA|OPENSSH|PRIVATE) KEY-----", "Private Key Header"),
    (r"(?i)password\s*[:=]\s*['\"][^'\"]+['\"]", "Hardcoded Password")
]

PROTECTED_PATHS = [
    "requirement/Propose",
    "requirement\\Propose",
    "Statement",
    "Statement\\",
    "Statement/"
]

# [AI-BLOCK: Check Protected Directory Violations]
def check_protected_paths():
    violations = []
    for root, dirs, files in os.walk("."):
        for protected in PROTECTED_PATHS:
            if protected in root:
                violations.append(f"Protected path accessed/present: {root}")
    return violations

# [AI-BLOCK: Fetch Git Revised Files (Memory-Safe Streaming)]
def get_revised_files():
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        files = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                files.append(parts[1])
        return files
    except Exception as e:
        print(f"Warning: git command failed ({e}), checking all text files in Dev/")
        dev_files = []
        for root, _, fs in os.walk("Dev"):
            for f in fs:
                dev_files.append(os.path.join(root, f))
        return dev_files

# [AI-BLOCK: Stream Scan Single File Line-By-Line to Conserve Memory]
def scan_file(filepath):
    findings = []
    if not os.path.exists(filepath) or os.path.isdir(filepath):
        return findings

    try:
        # Stream line-by-line using iterator to prevent large allocations in memory
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, 1):
                for pattern, desc in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, line):
                        findings.append(f"{filepath}:{idx} - [{desc}]")
    except Exception as err:
        findings.append(f"{filepath} - Error reading file: {err}")

    return findings

# [AI-BLOCK: CLI Execution Flow]
def main():
    print("--- Starting Security & Incremental AI Scan ---")
    
    # 1. Check protected directories
    protected_issues = check_protected_paths()
    if protected_issues:
        print("ERROR: Strict policy violation detected:")
        for issue in protected_issues:
            print(f"  {issue}")
        sys.exit(1)

    # 2. Check revised files only
    revised = get_revised_files()
    if not revised:
        print("No revised files found to scan.")
        print("Scan complete: Clean.")
        return

    print(f"Scanning {len(revised)} revised file(s)...")
    total_findings = []
    for f in revised:
        issues = scan_file(f)
        total_findings.extend(issues)

    if total_findings:
        print("WARNING: Sensitive data or security pattern detected:")
        for item in total_findings:
            print(f"  {item}")
        print("Aborting. Please sanitize sensitive information before committing.")
        sys.exit(1)
    else:
        print("Scan passed: No secrets detected, only revised files reviewed.")

if __name__ == "__main__":
    main()

