# [AI-BLOCK: Project-Specific Custom Rules & Overrides]
# Target Location: .agents/rules/project-rules.md (also recognized in .claude/rules/ and .github/instructions/)

# Project Custom Rules & Domain Policies

This file contains human-authored instructions, constraints, and operational preferences specific to this project. 
All AI agents (Google Antigravity, Claude Code, VS Code Copilot, Cursor) will read, respect, and enforce the rules below.

---

## 1. Project Overview & Boundaries
<!-- Describe what this project does and what technologies are allowed or prohibited. -->

- **Primary Stack**: [e.g., Python 3.11+, FastAPI, SQLite, Tailwind CSS, Next.js]
- **Target OS / Environment**: [e.g., Windows 10/11, Ubuntu 22.04, Docker]
- **Strictly Prohibited Libraries**: [e.g., Do not install pandas; use built-in csv/sqlite3 instead]
- **Forbidden Directories**: [e.g., Never modify or search `Statement/`, `data/raw/`, `credentials/`]

---

## 2. Coding & Architectural Standards
<!-- Define how code should be written in this specific project. -->

- **Architecture Style**: [e.g., Layered architecture: routers -> services -> models -> db]
- **State & Storage**: [e.g., All database queries must use parameterized SQL with context managers]
- **Error Handling**: [e.g., Catch specific exceptions; never use bare `except:`; log errors with timestamp]
- **Type Annotations**: [e.g., Mandatory type hints on all public function signatures]

---

## 3. UI, Frontend & Design Guidelines
<!-- If the project has a frontend or UI components, define styling and behavioral preferences. -->

- **Design System / Theme**: [e.g., Minimalist dark mode, Tailwind CSS utility classes]
- **No UI Slop**: Keep components headless, lean, and responsive. No excessive empty cards or bloated layouts.
- **Default Browser**: Brave Browser (Fallback: Chrome).

---

## 4. Testing, Verification & Tooling
<!-- How agents should test their changes before marking tasks complete. -->

- **Unit Test Runner**: [e.g., `pytest tests/ -v` or `npm test`]
- **Lint / Syntax Check**: [e.g., `ruff check .` or `python -m py_compile <file>`]
- **Smallest Change Rule**: Modify only what is strictly required for the feature or fix.

---

## 5. Security & Sensitive Data Invariants
<!-- Critical safety rules that the AI must never violate. -->

- **Zero Hardcoded Secrets**: Load all API keys and tokens from environment variables (`.env`).
- **Sanitized Outputs**: Never print user personal paths (e.g. `C:\Users\<user>`) in logs or UI.
- **No External Pushes**: Never push directly to git remotes or execute destructive database drops.

---

## Instructions for Human Developers (How to Edit This File)
1. **Be Concise**: Agents process instructions faster and more accurately when rules are bulleted and direct.
2. **Use Clear Negations**: If something should never be done, prefix with `NEVER:` or `PROHIBITED:`.
3. **Keep Outdated Rules Cleaned Up**: Remove obsolete instructions as the project evolves to prevent conflicting guidelines.

