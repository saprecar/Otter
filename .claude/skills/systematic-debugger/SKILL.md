---
name: systematic-debugger
description: Enforces a rigorous 4-phase root cause debugging workflow before touching code, eliminating trial-and-error edits and token burn.
---

# Systematic Debugger Skill

## Purpose
Stops hallucinated fixes and churn. Enforces root-cause investigation, reproduction, and strict failure limits.

## 4-Phase Debugging Protocol
1. **Phase 1: Observation & Reproduction**:
   - Inspect the exact error message, traceback, or failing condition.
   - Run a minimal command or script to reproduce the issue consistently.
   - Do NOT edit code yet.
2. **Phase 2: Root-Cause Isolation**:
   - Locate the exact function, line number, or schema mismatch causing the failure.
   - Trace data flow from input to failure point.
3. **Phase 3: Targeted Single-Diff Fix**:
   - Apply the smallest possible reversible change.
   - Do not refactor unrelated surrounding code.
4. **Phase 4: Empirical Verification**:
   - Re-run the reproduction command.
   - Confirm exit code 0 and absence of side effects.

## The 3-Attempt Failure Cap
- If the same bug fix fails after 2-3 attempts, STOP immediately.
- Do not repeat variations of the same broken logic.
- Roll back the failed edits, record current findings in `Dev/docs/bugs/bugs.md`, and report root-cause blockers to the user.

