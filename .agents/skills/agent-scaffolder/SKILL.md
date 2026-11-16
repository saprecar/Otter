---
name: agent-scaffolder
description: Scaffolds and updates tailored AGENTS.md, NAV_MAP.md, and tracking documentation into any new or existing external software project.
---

# Agent Scaffolder Skill

## Purpose
Initializes, adapts, and standardizes AI coding agent environments across new or existing repositories. Ensures any project you create inherits strict security, token optimization, and structured navigation rules.

## Scaffolding Capabilities
1. **Tech Stack Detection**:
   - Detects whether target project is Python, Node/TypeScript, Android/Gradle, Rust, or generic web.
2. **Standard Asset Generation**:
   - Scaffolds a project-tailored `AGENTS.md` with non-negotiable core rules (no direct pushing, no emojis, MIT/BSD licenses only, zero secrets in code/comments).
   - Scaffolds a project-tailored `NAV_MAP.md` mapping global constants and directory pointers.
   - Creates the unified tracking structure (`Dev/docs/requirements/`, `Dev/docs/bugs/`, `Dev/docs/state/`).
3. **Execution Command**:
   ```bash
   # Scaffold rules into target directory:
   python Stable/scripts/scaffold_agent_rules.py /path/to/target-project
   ```
4. **Maintenance & Updates**:
   - When project architecture evolves, running `agent-scaffolder` updates `NAV_MAP.md` and appends new variable definitions without overwriting custom developer rules.

