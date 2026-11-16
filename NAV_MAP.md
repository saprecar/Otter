# Quick Navigation Map (NAV_MAP.md)

Fast-lookup index for AI agents. Identifies where key variables, configuration constants, server endpoints, and rules are defined across the repository. **Consult this file first to avoid searching the entire codebase.**

---

## 1. Key Configuration & Global Variables

| Variable / Constant | Defining Location | Default / Schema | Description |
| :--- | :--- | :--- | :--- |
| `OLLAMA_ENDPOINT` | `Stable/AGENTS.md`, `Stable/skills/ollama-mcp-controller/` | `http://127.0.0.1:11434` | Local Ollama REST/MCP port |
| `SAFE_NUM_CTX` | `Stable/AGENTS.md` (Sec 4), `ollama-mcp-controller` | `2048` (Laptop 4GB) / `16384` (RTX 5070 Ti 16GB) | Context token ceiling to prevent CUDA OOM crash |
| `SAFE_NUM_PREDICT` | `Stable/AGENTS.md` (Sec 4), `ollama-mcp-controller` | `512` (Laptop 4GB) / `2048` (RTX 5070 Ti 16GB) | Max generated token ceiling for local LLM |
| `COLIBRI_ENDPOINT` | `Stable/AGENTS.md`, `REPO_MAP.md` | `http://127.0.0.1:8080` (or local socket) | Hierarchical MoE engine for large local models |
| `SUSPICIOUS_PATTERNS` | `Stable/scripts/scan_secrets_and_diff.py` | Regex tuples | Secret & API token scanning patterns |
| `PROTECTED_PATHS` | `Stable/scripts/scan_secrets_and_diff.py`, `.gitignore` | `["requirement/Propose", "Statement"]` | Strictly quarantined / unversioned directories |
| `overlayPositions.logPosition` | `Stable/ui/overlay.html`, `USER_GUIDE.md` | Chrome local storage | Draggable logcat persistent coordinate |
| `FREE_FOR_DEV_GUIDE` | `Stable/docs/guides/free-tier-bootstrap.md` | Free Tier Index | Zero-cost infrastructure, DB, & hosting guide |
| `FREE_LLM_ROUTER` | `Stable/skills/free-llm-router/` | Proxy Router Skill | Dev/testing free-tier router with rate-limit boundaries |
| `UI_UX_CRAFT` | `Stable/skills/ui-ux-craft/` | Design Skill | Production frontend UI/UX, tokens, & anti-slop layouts |
| `RESUME_BUILDER` | `Stable/skills/resume-career-builder/` | Career Skill | ATS resume, Google XYZ bullet re-engineering, cover letters |
| `STABLE_RELEASE_AUDITOR` | `Stable/skills/stable-release-auditor/` | 5-Gate Checklist | Production audit skill before promotion |
| `AGENT_SCAFFOLDER` | `Stable/skills/agent-scaffolder/`, `Stable/scripts/` | CLI & Skill | Auto-scaffold AGENTS.md/NAV_MAP into any project |
| `INSTALLER_WINDOWS` | `install_agent_skills.bat` | Batch Script | 1-Click setup for any Windows project |
| `INSTALLER_POSIX` | `install_agent_skills.sh` | Bash Script | 1-Click setup for Linux & macOS projects |
| `overlaySettings.showDebugLogOverlay` | `Stable/ui/overlay.html`, `Stable/AGENTS.md` | Boolean | Visibility toggle for `#understory-debug-overlay` |
| `DEFAULT_BROWSER` | `Stable/AGENTS.md` (Core Rule 4) | `Brave Browser` (fallback from Chrome) | Primary browser environment |
| `VERSION_FORMAT` | `Stable/AGENTS.md` (Sec 13), `GITHUB_STATE.md` | `Major.Minor.Patch.Build` (e.g. `1.1.0.0`) | 4-digit cross-platform version scheme |
| `SITEMAP_INDEX` | `sitemap.xml` | XML Sitemap 0.9 | Web search engine indexing endpoints |
| `LLMS_TXT` | `llms.txt` | LLMs.txt Standard | LLM crawler & agent index |
| `AGENT_MANIFEST` | `agent.xml` | Agent Manifest 1.0 | AI agent discovery and skill registry |
| `SCRAPING_POLICY` | `robots.txt` | Robots Standard | Allow search/AI retrieval, disallow mass harvesting |
| `ANDROID_VERSION_CODE` | `Stable/AGENTS.md` (Sec 13), `GITHUB_STATE.md` | Single digit: Even=Stable, Odd=Dev/Test | Android release classification integer |
| `stableRelease` | `Stable/AGENTS.md` (Sec 13) | `false` | Gate authorizing production cleanup |

---

## 2. Directory Navigation Quick-Reference

| Component Type | Canonical Production Location | Active Development Location |
| :--- | :--- | :--- |
| **Agent Master Rules** | `Stable/AGENTS.md` | `Dev/AGENTS.md` |
| **Quick Variable Navigation** | `NAV_MAP.md` | `NAV_MAP.md` |
| **Repo Index & Upstreams** | `REPO_MAP.md` | `REPO_MAP.md` |
| **Snapshot State Ledger** | `GITHUB_STATE.md` | `GITHUB_STATE.md` |
| **User & UI Manual** | `USER_GUIDE.md` | `USER_GUIDE.md` |
| **Skill Packages** | `Stable/skills/<name>/<name>_skill.md` | `Dev/skills/<name>/<name>_skill.md` |
| **Agent Personas** | `Stable/agents/<name>.md` | `Dev/agents/<name>.md` |
| **Execution Workflows** | `Stable/workflows/<name>.md` | `Dev/workflows/<name>.md` |
| **Antigravity Workflows** | `.agent/workflows/<name>.md` | `.agent/workflows/<name>.md` |
| **Antigravity Skills & Agents** | `.agents/skills/`, `.agents/agents/` | `.agents/skills/`, `.agents/agents/` |
| **Claude Code Skills** | `.claude/skills/<name>/` | `.claude/skills/<name>/` |
| **Claude Code Directives** | `CLAUDE.md` | `CLAUDE.md` |
| **Reusable Prompts** | `Stable/prompts/README.md` | `Dev/prompts/README.md` |
| **Logcat Overlay UI** | `Stable/ui/overlay.html` | `Dev/ui/logcat/overlay.html` |
| **Work State & Rest Mode** | `Dev/docs/state/work-state.md` | `Dev/docs/state/work-state.md` |
| **Bug Tracker** | `Dev/docs/bugs/bugs.md` | `Dev/docs/bugs/bugs.md` |
| **Feature Requests** | `Dev/docs/features/features.md` | `Dev/docs/features/features.md` |
| **Requirements Log** | `Dev/docs/requirements/requirements.md` | `Dev/docs/requirements/requirements.md` |
| **Stable Changelog** | `stable_release/CHANGELOG_STABLE.md` | `stable_release/CHANGELOG_STABLE.md` |

