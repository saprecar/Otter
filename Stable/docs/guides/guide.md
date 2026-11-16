# Guide

Short, practical reference on how to run, test, and verify features in this repository.

---

## 1. Local Verification Workflow
1. **Security & Diff Scan**:
   ```bash
   python Stable/scripts/scan_secrets_and_diff.py
   ```
2. **Local Ollama MCP Connection**:
   - URL: `http://127.0.0.1:11434`
   - Test command: `npx -y ollama-mcp-server`

## 2. Managing Requirements, Bugs & Features
- Requirements: `Dev/docs/requirements/requirements.md`
- Bugs: `Dev/docs/bugs/bugs.md`
- Features: `Dev/docs/features/features.md`
- Continuation State: `Dev/docs/state/work-state.md`

