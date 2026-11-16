# Coding Agent Rules

Canonical configuration and operational rules for AI coding agents.

---

## 1. Core Rules

1. **No Direct Pushes**: Do not push code to GitHub or production/main. Save the required files and changes so the user can review and push them.
2. **No Emojis**: Do not use emojis in code, comments, commit messages, or responses.
3. **No Unrequested Refactoring**: Do not refactor existing code unless explicitly requested.
4. **Browser Defaults & Detection**:
   - **Brave Browser is the primary default browser**.
   - If Google Chrome is requested or checked but not available, automatically detect and fall back to Brave Browser.
   - Do not add browser-specific options, flags, or extensions unless explicitly requested.
5. **Architectural Consistency**: Follow the existing engine architecture. Prefer reusable, modular code.
6. **Python Interoperability**: Python integration is permitted where required. Maintain existing engine architecture and clean interoperability.
7. **Permissive Open-Source Licensing Only**: Before adding any library or dependency, ensure it uses MIT, BSD-2/3-Clause, or Apache-2.0 open-source licensing without commercial/business restrictions or copyleft obligations. Confirm with the user before adding new dependencies.
8. **Syntax Rigor**: Check syntax carefully: brackets, braces, parentheses, commas, quotes, imports, and related symbols.
9. **Concise Communication**: Keep responses short. Point to the file, function, command, or check location instead of giving long explanations.
10. **Clean Replies**: Do not use headers or footers in normal agent replies.
11. **API Key & Leak Protection (Zero Hardcoding & Zero Sensitive Comments)**:
    - **Never hardcode** passwords, passphrases, API keys, private tokens, connection secrets, or confidential credentials into source code, configurations, backups, or logs.
    - **Never write sensitive info in comments**: Do not disclose credentials, secret values, real authentication tokens, or confidential paths in inline comments, block comments, docstrings, or TODO notes.
    - When backing up, archiving, exporting, or committing files, never save plain API keys or secrets. If detected, redact immediately (`[REDACTED]`) and inform the user.
12. **Strict Multi-Stage Isolation**: Work and grind exclusively in `Dev/`. External consuming agents use `Stable/` strictly as read-only.

---

## 2. Protected & Prohibited Folders

### Protected Directory: `requirement/Propose`
- Do not access, read, list, search, or edit `requirement/Propose` (and everything inside it).
- Skip it in all searches, globs, greps, and cleanups.
- If a task seems to need it, stop and ask the user.

### Prohibited Directory: `Statement/`
- The root-level `Statement/` directory and all its contents are strictly prohibited from being tracked or uploaded to Git.
- Never commit, track, or stage `Statement/` or any generated, temporary, or archived files originating from it.
- Ensure `git check-ignore -v Statement/` confirms exclusion.

---

## 3. Git Security & Sensitive Data Protection

Never commit, upload, hardcode, or expose the following anywhere in the codebase:
- Passwords, passphrases, and PINs.
- API keys, access tokens, refresh tokens, and authentication credentials.
- Database connection strings with secrets.
- Private keys (`*.pem`, `*.key`, `*.p12`, `*.pfx`), SSH keys, and certificates.
- Cloud provider credentials and service account keys.
- Session tokens, cookies, and authentication data.
- Environment files containing secrets (`.env`, `.env.*`).
- Confidential business documents and personal information.

### Security Implementation Guidelines
- **No Hardcoded Credentials**: Load sensitive configuration from environment variables or an approved secret manager. Use clearly nonfunctional placeholders only when strictly required.
- **No Security Comments**: Never write secrets or confidential paths in inline comments, docstrings, or TODO notes.
- **Pre-Commit Verification**: Run `Dev/scripts/scan_secrets_and_diff.py` before finalizing any changes. Check staged files with `git diff --cached` and `git status --short`.
- **Exposed Secret Remediation**: If a secret is committed, immediately revoke/rotate the credential, redact the current file, and coordinate Git history rewriting if needed.

---

## 4. MCP Server & Local Inference Integration (Ollama & Colibri)

### MCP & Local Engine Detection Protocol
- **Supported Engines**:
  - **Ollama**: `http://127.0.0.1:11434` (standard local models: `qwen3.5:9b`, `qwen2.5-coder:7b`).
  - **Colibri (`JustVugg/colibri`)**: `http://127.0.0.1:8080` (pure C hierarchical inference engine; streams massive MoE models across VRAM, RAM, and NVMe).
- **Graceful Non-Forcing Fallback**:
  - **Check Before Call**: Check if Ollama or Colibri service is reachable before dispatching tasks.
  - **Do NOT Force or Fake**: If neither Ollama nor Colibri is installed or running, **do not attempt to force execution, fake responses, or loop in failure**.
  - Fall back gracefully to cloud models (e.g. Gemini Flash Low) or notify the user that local inference is inactive.
- **Hardware & Adaptive Multi-System Tiering**:
  - The workspace auto-profiles the active host machine via `check_local_llm_guard.py`:
    - **Tier A (Laptop / Constrained GPU - GTX 1050 4GB VRAM, 16GB DDR4)**:
      - Strict context ceiling: `"num_ctx": 2048`, `"num_predict": 512` to prevent CUDA OOM crashes.
      - Recommended models: `gemma2:2b`, `qwen2.5-coder:1.5b`, `qwen2.5-coder:3b`.
    - **Tier B (Workstation Rig - RTX 5070 Ti 16GB VRAM, 32GB DDR5-6000, i7-14700F)**:
      - Extended context: `"num_ctx": 16384` (up to 32768), `"num_predict": 2048`.
      - Recommended models: `qwen2.5-coder:14b`, `qwen2.5-coder:32b (4-bit)`, `deepseek-r1:14b`.
  - For huge MoE models: Use Colibri's hierarchical memory offloading (VRAM $\rightarrow$ RAM $\rightarrow$ NVMe) to prevent VRAM crashes on either system.

### MCP Server Operational Rules
- Use local MCP for small issues (single-file bug, syntax check) and planning/brainstorming.
- Keep output short; pass focused diffs or snippets, never whole projects.
- Consult `NAV_MAP.md` to locate variables and configurations before searching code.

### Free-Tier LLM Proxy Routing (Dev & Testing Only)
- Free-tier routers (OmniRoute, LiteLLM with Groq, Gemini Free, OpenRouter) are strictly restricted to **Development, Testing, and Local MCP tasks**. They are prohibited in production releases.
- **Strict Rate-Limit Adherence**:
  - Groq: Cap to 25 RPM / 1,000 requests/day, max 2048 output tokens.
  - Gemini AI Studio Free: Cap to 15 RPM / 1,500 requests/day; never pass sensitive code or secrets (training policy clause).
  - On HTTP 429: Trigger circuit breaker, pause 5 seconds, and failover immediately to local Ollama (`gemma2:2b`). Do not hammer endpoints in aggressive retry loops.

---

## 5. Requirement, Bug, and Feature Tracking First

Whenever a new requirement, bug, or feature is introduced:
- Check if the corresponding `.md` file and folder exist under `Dev/docs/`:
  - **Requirements**: `Dev/docs/requirements/requirements.md` (or task-specific `REQ-*.md`)
  - **Bugs**: `Dev/docs/bugs/bugs.md` (or issue-specific `BUG-*.md`)
  - **Features**: `Dev/docs/features/features.md` (or feature-specific `FEAT-*.md`)
- If the directory or `.md` file is missing, create it first before taking any coding action.
- Record the entry with date, status, and concise description before writing code.
- Apply strict token optimization:
  - Keep bug entries to max 3 lines (ID/Date, Symptom/File, Fix Attempt).
  - Keep feature entries to max 3 lines (ID/Date, Module, Description).
- Mark status:
  - While active: `WIP`
  - After implementation: `Tested`
  - Final: Mark `Completed` or `Fixed` only after explicit user confirmation.

---

## 6. GitHub State, Version Recovery & Backup Ledger

- Maintain `GITHUB_STATE.md` in the root repository.
- Every release or major change must log:
  - Version code and date.
  - Environment status (Dev, Testing, Stable).
  - Features implemented and bugs confirmed fixed.
  - Known-good file paths and snapshot restore points.
- **Agent Failure Recovery**:
  - If something breaks or a regression occurs, the AI agent must read `GITHUB_STATE.md` first.
  - Identify the last known-good working snapshot for the affected module.
  - Use targeted diff restoration from `Stable/` or git commit points instead of guessing or performing full rewrites.

---

## 7. AI Block Comments & Memory-Efficient Coding

- **AI Block Comments**: Add a compact header comment before every logical unit or function so AI agents instantly know its intent and boundaries (e.g., `# [AI-BLOCK: <purpose>]` or `// [AI-BLOCK: <purpose>]`). Keep comments concise to preserve tokens.
- **Memory Optimization**: Write code optimized for low memory footprint:
  - Stream large datasets; avoid loading entire files into memory at once.
  - Use generators/iterators instead of allocating massive in-memory arrays.
  - Release resources, sockets, and file handles promptly with context managers (`with` blocks).
- **Prompt Isolation**:
  - All prompts MUST remain in `prompts/` (`Dev/prompts/` and `Stable/prompts/`) as individual or grouped `.md` files.
  - Never scatter prompts in source code.
  - Structure prompt files for minimal token overhead (dense instructions, zero boilerplate).

---

## 7. Third-Party Code, GitHub Security & Anti-Slop

### Open-Source License Verification
- Any external repository, dependency, or open-source reference must use an MIT, BSD-2/3-Clause, or Apache-2.0 license.
- Must be free to use without commercial restrictions, subscription walls, or copyleft constraints (e.g., GPL/AGPL).
- Always confirm license compliance before incorporating logic or dependencies.

### Malicious Code & Data Exfiltration Scan
- Before consuming third-party code, packages, or GitHub scripts, inspect for malicious behavior:
  - Outbound telemetry, background analytics, or third-party webhooks.
  - Hardcoded external APIs, external IP pings, or data transmission endpoints.
  - Covert data logging or local credential/token scraping.
  - Unsafe network sockets or arbitrary remote code execution (`eval`, unvetted subprocess calls).
- If any exfiltration pattern is detected, reject the code and report the risk immediately.

### Anti-Slop Directives
- Ruthlessly eliminate boilerplate, single-call wrapper functions, and performative comments.
- Keep UI components headless and minimal (Tailwind CSS, clean primitives).

---

## 8. Integrated Workflow System & Dynamic Skills

- **Workflow Directory**: Look inside `Dev/workflows/` (or `Stable/workflows/`) for structured phase, planning, debugging, and verification workflows.
- **Dynamic Skill Discovery & Execution**:
  - Automatically assess the task domain (development, web engineering, codebase audit, search, security review).
  - Inspect `Stable/skills/` or `Dev/skills/` to select matching single-file skills (`<skillname>_skill.md`).
  - Register newly researched skills into `Dev/skills/` and test before graduating to `Stable/skills/`.

---

## 9. Discovery Roots, Skill Assessment & File Naming

### Skill File Naming Convention
To ensure instant file search, autocomplete, and seamless linking across VS Code, Antigravity IDE, and autonomous agents:
- Every skill folder contains strictly one markdown file named `<skillname>_skill.md` (e.g. `anti-slop-guard_skill.md`, `ai-firewall-guard_skill.md`, `ollama-mcp-controller_skill.md`).
- No duplicate `SKILL.md` is kept.
- This allows direct `@<skillname>_skill.md` invocation in chat and quick-open in editors.

### Discovery Roots Table

| Component Type | Development Root (`Dev/`) | Stable Release Root (`Stable/`) | Reference / Template |
| :--- | :--- | :--- | :--- |
| **Skills** | `Dev/skills/<name>/<name>_skill.md` | `Stable/skills/<name>/<name>_skill.md` | Unified Skills Suite (17 skills) |
| **Agents** | `Dev/agents/<agent-name>.md` | `Stable/agents/<agent-name>.md` | Unified Agent Personas (5 agents) |
| **Workflows** | `Dev/workflows/<workflow-name>.md` | `Stable/workflows/<workflow-name>.md` | Unified Execution Workflows (27 workflows) |
| **Prompts** | `Dev/prompts/` | `Stable/prompts/` | Domain prompt catalogs (`finance`, `email`, `hr`) |
| **Rules & Docs** | `Dev/docs/` | `Stable/docs/` | `Stable/AGENTS.md`, `NAV_MAP.md`, `REPO_MAP.md` |

### Agent Skill Assessment Protocol
1. **Locate**: Inspect the skill directory to list available skills by `<skillname>_skill.md`.
2. **Assess**: Read only the YAML frontmatter and Purpose section in `<skillname>_skill.md` to evaluate fit without wasting tokens.
3. **Select & Apply**: Apply the minimal relevant skill.

---

## 10. Dynamic Model Selection & Complexity Tiers

Recommend and switch models based on task requirements to prevent token burn and maintain high accuracy:

| Model Tier | Target Tasks | Characteristics |
| :--- | :--- | :--- |
| **Local Ollama (`qwen3.5:9b`)** | Single-file syntax fixes, small targeted diffs, quick checks | Zero API token cost, local privacy |
| **Gemini Flash (Low / Medium)** | Routine edits, documentation, lint fixes, repetitive changes | High speed, lowest token cost, lightweight |
| **Gemini Flash (High)** | Standard multi-file features, test authoring, script updates | Balanced speed, larger context, reliable reasoning |
| **Gemini Pro** | Complex architecture design, deep multi-file debugging, security audits | Maximum reasoning depth, deep verification |

*Rule*: If a high-tier model is active for trivial edits or documentation, remind the user to switch to Gemini Flash (Low) to conserve token budget.

---

## 10. Agent Permissions & Stable Immutability

- **Development Agent Permissions**: The active development agent is permitted to edit, test, iterate, and refactor files within `Dev/` and documentation as requested by the user.
- **Stable Release Strict Immutability**:
  - The `Stable/` directory is strictly **READ-ONLY** for external agents.
  - External consuming agents MUST NOT modify, overwrite, delete, or refactor any file in `Stable/`.
  - No file may be added to or modified within `Stable/` without explicit, unambiguous user approval.

---

## 11. Safe Execution, Verification & Change Safety

1. **Read Before Editing**: Inspect the relevant file and existing architecture before making changes.
2. **Smallest-Change Rule**: Modify only what is required. Do not touch unrelated files.
3. **Do Not Guess**: If an API, path, dependency, or requirement is unclear, ask the user.
4. **Verify Every Change**: Test using the smallest relevant script or check. Never claim success without verification.
5. **Failure Cap**: If the same fix fails 2-3 times, stop repeating the same approach and reassess the root cause.
6. **Preserve Working Code**: Keep existing working code intact unless explicitly modified. Prefer reversible changes.
7. **Change Output Format**: After completing a task, keep responses concise:
   `Changed -> Tested -> Files -> Next action`

---

## 12. Documentation & Change Log Workflow

Maintain separate, strictly **append-only** change logs:
- `Dev/docs/changelogs/CHANGELOG_DEV.md`: Daily development changes in the main project directory.
- `testing_release\CHANGELOG_TESTING.md`: Testing builds, test results, failures, and retests.
- `stable_release\CHANGELOG_STABLE.md`: Official stable releases only.
- `Dev/docs/changelogs/CHANGELOG_GUIDE.md`: Instructions for maintaining change logs across release workflows.

### Append-Only Change Log Rules
- All change logs must be append-only across all environments.
- Always append new entries to the end of the file. Never overwrite or delete historical entries.
- If an earlier entry is incorrect, append a dated correction referencing the original entry.
- Record timestamps in `YYYY-MM-DD HH:mm:ss IST (UTC+05:30)` format.
- Only mark a bug fixed after user confirmation.

### Session Handoff & Rest Mode
- After approximately 1 hour of continuous work, remind the user to take a break.
- When entering rest mode, create or update `Dev/docs/state/work-state.md` with:
  - Current date/time and status
  - Last completed task and files changed
  - Current file/function being worked on
  - Remaining steps and important checks
- Keep practical feature notes in `Dev/docs/guides/guide.md` and bug status in `Dev/docs/state/software-log.md`.

---

## 13. Explicit Stable Release Protocol & 4-Digit Versioning

### 4-Digit Versioning Standard
Across all platforms, scripts, and documentation:
- Format: `Major.Minor.Patch.Build` (e.g., `1.1.0.0` for stable, `1.1.1.1` for dev/test builds).
- **Android App `versionCode` Standard**:
  - Represented as a single-digit integer.
  - **Even Numbers** (e.g. 2, 4, 6, 8): Strictly reserved for **Stable and Public Releases**.
  - **Odd Numbers** (e.g. 1, 3, 5, 7, 9): Strictly reserved for **Dev, Alpha, and Testing Releases**.

### Stable Release Trigger & Authorization
- **Default State**: `stableRelease = false`.
- **Restriction**: The system must not assume that packaging, a production version number, or outside build tools mean a Stable Release.
- **Release Trigger**: Stable-release cleanup (clearing logs/caches, disabling developer/test modes, removing dev tools, enforcing production submission) executes **only when explicitly declared by the user**.

```text
BUILD TYPE
├── Development        → No stable-release cleanup
├── Testing            → No stable-release cleanup
├── Beta               → No stable-release cleanup
├── Alpha              → No stable-release cleanup
├── Release Candidate  → No stable-release cleanup
├── Internal/WIP       → No stable-release cleanup
└── Stable Release     → Execute full release cleanup (Requires explicit user declaration)
```

---

## 14. Unified In-Page Log Screen Standard (Logcat Overlay)

All in-page logging overlays across all platforms and environments must use the standard Understory draggable logcat overlay interface (`#understory-debug-overlay`):
- **Visual Design**: Green `#238636` header with "System Logcat & Local Errors", draggable cursor, minimize ('—'), and close ('✖') controls.
- **Controls**: Action bar containing "Copy Log" and "Clear Log" buttons, with live sanitization indicator.
- **Auto-Sanitization Enforcement**:
  - Automatically redact and mask personal usernames, home directory paths (e.g. `C:\Users\<user>` or `/home/<user>`), replacing them with `[USER_HOME]`.
  - Mask external IP addresses, private credentials, and API keys (`[IP_REDACTED]`, `[REDACTED]`).
  - Do not allow raw unsanitized personal info into the logcat view or copied text.
- **Mandatory Server & Error Capture**:
  - Every local server error, software log, or intercepted exception must be piped to this overlay.
- **Persistence & Bounds**:
  - Boundary clamping within the viewport and position persistence in `chrome.storage.local` under `overlayPositions.logPosition`.
  - Synchronized visibility with `overlaySettings.showDebugLogOverlay`.
  - Do not create custom, fixed-position, non-draggable, or distinct UI log windows on individual platforms.

---

## 15. User Guide & UI Mockup Maintenance

- Maintain `USER_GUIDE.md` as the primary token-optimized reference for workflows and steps.
- Because AI agents cannot take visual screenshots, represent UI states directly using pure read-only UI code blocks (HTML/CSS or ASCII layout) with no backend logic attached.
- **Mandatory Update**: Whenever a UI state, workflow step, or tool is changed or deprecated, update `USER_GUIDE.md` immediately in the same edit batch.

---

## 16. Launch Protocol (`LAUNCH.md`) Rule

- **Do NOT create `LAUNCH.md` proactively or automatically**.
- Create `LAUNCH.md` **only when explicitly requested by the user**.
- When requested, `LAUNCH.md` must incorporate:
  1. **Search Console & Webmaster Indexing**: Google Search Console verification, Bing Webmaster Tools, `sitemap.xml`, and `llms.txt` submission.
  2. **Social Previews**: Open Graph meta tags validation for WhatsApp, LinkedIn, and X.
  3. **Launch Platforms & Low-Traffic Optimization**:
     - Product Hunt: Schedule for low-competition days (e.g. weekends/holidays for easier top-5 rankings vs mid-week for maximum traffic).
     - Hacker News (`Show HN`): Direct, no-marketing title format and architecture breakdown.
     - Reddit: `r/SideProject` and niche developer subreddits.
     - Discovery Catalogs: Indie Hackers, Uneed, MicroLaunch.
