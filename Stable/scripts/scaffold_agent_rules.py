#!/usr/bin/env python3
# [AI-BLOCK: Universal Project Agent Rules Scaffolder]
"""
Scaffolds tailored AGENTS.md, NAV_MAP.md, and security checks into any new or existing project.
Auto-detects tech stack (Python, Node/TS, Android/Gradle, Rust, Web).
"""

import os
import sys

# [AI-BLOCK: Detect Project Tech Stack]
def detect_tech_stack(target_dir="."):
    files = set(os.listdir(target_dir)) if os.path.exists(target_dir) else set()
    stack = []
    if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
        stack.append("Python")
    if "package.json" in files:
        stack.append("Node/TypeScript")
    if "build.gradle" in files or "build.gradle.kts" in files:
        stack.append("Android/Kotlin")
    if "Cargo.toml" in files:
        stack.append("Rust")
    if not stack:
        stack.append("General Software")
    return ", ".join(stack)

# [AI-BLOCK: Generate Tailored AGENTS.md]
def generate_agents_md(project_name, tech_stack):
    return f"""# Coding Agent Rules - {project_name}

Canonical configuration and operational rules for AI coding agents working on {project_name} ({tech_stack}).

---

## 1. Core Rules

1. **No Direct Pushing**: Do not push code to GitHub or production/main. Save files and diffs locally for user review and push.
2. **No Emojis**: Do not use emojis in replies, code, commit messages, or documentation.
3. **No Unrequested Refactoring**: Do not refactor existing working code unless explicitly requested.
4. **Architectural Consistency**: Follow existing architecture ({tech_stack}). Prefer reusable, modular code.
5. **Permissive Open-Source Only**: Use only MIT or BSD-2/3-Clause dependencies. No copyleft (GPL/AGPL) or commercial/business restrictions.
6. **Syntax Rigor**: Check syntax carefully before saving (brackets, quotes, types, imports).
7. **Concise Communication**: Keep responses short. Point to file, function, command, or check location.
8. **Clean Replies**: Do not use headers or footers in normal agent replies.
9. **Zero Plain Secrets in Code or Comments**:
   - Never hardcode passwords, API keys, private tokens, or credentials into source code, configs, or logs.
   - Never write secret values or confidential paths into code comments (inline, block, or docstrings).
   - Use environment variables or nonfunctional placeholders (`[REDACTED]`).
10. **Multi-Stage Isolation**: Work and grind exclusively in `Dev/`. Only promote verified items to `Stable/`.

---

## 2. Quick Discovery Roots

Before searching the codebase, consult:
- `NAV_MAP.md`: Fast-lookup table for key variables, ports, and configuration constants.
- `Dev/docs/requirements/`: Feature specifications and requirements tracking.
- `Dev/docs/bugs/`: Bug tracking entries (3-line max).
- `Dev/docs/state/work-state.md`: Active continuation state and rest-mode handoffs.

---

## 3. Safe Execution & Verification

1. Read before editing. Target the smallest relevant file.
2. Verify every change with automated tests or syntax checkers before claiming completion.
3. If a bug fix fails 2-3 times, stop repeating the same approach and reassess root cause with user.
4. Keep responses concise: `Changed -> Tested -> Files -> Next action`.
"""

# [AI-BLOCK: Generate Tailored NAV_MAP.md]
def generate_nav_map_md(project_name, tech_stack):
    return f"""# Quick Navigation Map ({project_name})

Fast-lookup index for AI agents. Identifies where key variables and configurations are defined across the repository.

| Component / Setting | Defining Location | Default / Schema | Description |
| :--- | :--- | :--- | :--- |
| **Agent Rules** | `AGENTS.md` | Markdown | Master operational rules for coding agents |
| **Active Tech Stack** | Root | `{tech_stack}` | Detected runtime architecture |
| **Requirements Log** | `Dev/docs/requirements/requirements.md` | Log | Requirements tracker (REQ-*) |
| **Bug Tracker** | `Dev/docs/bugs/bugs.md` | Log | Bug tracker (BUG-*) |
| **Work State** | `Dev/docs/state/work-state.md` | Markdown | Continuation state & rest mode handoff |
"""

# [AI-BLOCK: Main Scaffolder Routine]
def scaffold_project(target_dir=".", project_name=None):
    if not project_name:
        project_name = os.path.basename(os.path.abspath(target_dir))
    
    tech_stack = detect_tech_stack(target_dir)
    print(f"Scaffolding AI agent rules for: {project_name} [{tech_stack}]...")
    
    # 1. Create docs directory structure
    for sub in ["Dev/docs/requirements", "Dev/docs/bugs", "Dev/docs/features", "Dev/docs/state"]:
        os.makedirs(os.path.join(target_dir, sub), exist_ok=True)
        
    # 2. Write AGENTS.md
    agents_path = os.path.join(target_dir, "AGENTS.md")
    if not os.path.exists(agents_path):
        with open(agents_path, "w", encoding="utf-8") as f:
            f.write(generate_agents_md(project_name, tech_stack))
        print(f"Created: {agents_path}")
    else:
        print(f"Skipped existing: {agents_path}")
        
    # 3. Write NAV_MAP.md
    nav_path = os.path.join(target_dir, "NAV_MAP.md")
    if not os.path.exists(nav_path):
        with open(nav_path, "w", encoding="utf-8") as f:
            f.write(generate_nav_map_md(project_name, tech_stack))
        print(f"Created: {nav_path}")
    else:
        print(f"Skipped existing: {nav_path}")

    print("Agent rules scaffolding complete.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    scaffold_project(target)

