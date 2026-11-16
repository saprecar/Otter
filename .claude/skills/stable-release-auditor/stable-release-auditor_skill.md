---
name: stable-release-auditor
description: Production-readiness audit skill verifying security, zero-leaks, build hygiene, VRAM hardware bounds, and release mechanics before graduation to Stable.
---

# Stable Release Auditor Skill

## Purpose
Enforces an automated, 5-gate production readiness audit on any codebase before code is allowed to promote from `Dev` to `Stable` or be published publicly.

## Gate 1: Security & Zero-Leak Audit
- [ ] Run secret scanner: Ensure 0 exposed API keys, tokens, or credentials exist in git diffs or files.
- [ ] Verify prohibited folders (`Statement/`, `requirement/Propose`, `.env`) are ignored in `.gitignore`.
- [ ] Verify zero credentials, confidential paths, or tokens are written in comments or docstrings.
- [ ] License Compliance: Verify all dependencies strictly adhere to permissive licenses (MIT, BSD-2/3-Clause, Apache-2.0).

## Gate 2: Code Hygiene & Anti-Slop
- [ ] Ensure syntax checks exit with code 0 across all modified scripts and source files.
- [ ] Eliminate AI boilerplate, single-call wrappers, and empty `TODO` stubs.
- [ ] Verify memory-safe data processing (line streaming for files, generators for large data).
- [ ] Confirm all logical units feature `# [AI-BLOCK: <purpose>]` header comments.

## Gate 3: Hardware & Runtime Resilience
- [ ] Ensure local inference enforces VRAM-safe context ceilings (`num_ctx: 2048` on 4GB GPUs).
- [ ] Verify graceful fallback: If Ollama or Colibri is unreachable, code falls back cleanly without faking data or infinite error loops.
- [ ] Ensure default browser fallback is respected (Brave Browser default, Chrome fallback).

## Gate 4: Environment Isolation & Diagnostics
- [ ] Verify `stableRelease = false` default behavior. Do not perform release cleanup during dev builds.
- [ ] Verify in-page logcat overlay (`#understory-debug-overlay`) is active with real-time auto-sanitization (`[USER_HOME]`, `[IP_REDACTED]`).
- [ ] Ensure developer test bypasses and temporary debugging hooks are deactivated.

## Gate 5: Versioning & Rollback Strategy
- [ ] Verify 4-digit version standard: `Major.Minor.Patch.Build` (e.g. `1.2.0.0`).
- [ ] For Android applications: Ensure single-digit `versionCode` is an **EVEN integer** (e.g. `2`, `4`, `6`, `8`).
- [ ] Append release entry to `stable_release/CHANGELOG_STABLE.md` and `GITHUB_STATE.md`.
- [ ] Verify rollback command is documented to recover previous known-good working state if needed.

