---
name: claude-coding-mimic
description: Last-resort systematic engineering protocol for deeply stuck agents. Applies rigorous root-cause methodology, surgical fix discipline, and production-grade code standards. Invoke only when standard attempts have failed 2+ times.
---

# Claude Coding Mimic — Engineering Protocol

> [!IMPORTANT]
> Invoke this skill ONLY when the standard approach has failed 2 or more times and the agent is blocked.
> This protocol is token-intensive by design; it trades speed for correctness.

---

## Activation Trigger

Activate when any of the following are true:
- Same fix attempted 2+ times without success.
- Root cause is unclear after initial stack trace read.
- Feature produces wrong output with no visible error.
- Race condition, silent failure, or partial state corruption suspected.

---

## Phase 1: STOP & REPRODUCE

**Never touch code until the failure is reliably reproducible.**

1. Write the minimal reproduction: fewest lines of input that trigger the bug.
2. If reproduction fails: the bug is environment-dependent (env vars, OS, Python version, file state). Isolate that variable first.
3. State clearly: "This input causes this wrong output. Expected output is X."

---

## Phase 2: LOCATE — Root Cause Classification

Read the stack trace **bottom-up** (origin frame is at the bottom).

Classify the root cause into exactly one of:

| Class | Signal | Fix Strategy |
| :--- | :--- | :--- |
| **Logic bug** | Wrong output on a specific input subset | Correct the algorithm; add invariant assertion |
| **Contract violation** | Caller passes unexpected data | Validate at the boundary (entry point), not inside the callee |
| **Race / ordering** | Failure only under concurrency or sequence change | Identify shared mutable state; serialize or eliminate it |
| **Resource leak** | Grows over time; fails after N calls | Wrap acquisition in `with`; check every error exit path |
| **Silent failure** | No exception, wrong result | Binary-search with assertions: confirm state at midpoint, narrow direction |

---

## Phase 3: SURGICAL FIX

Rules — no exceptions:
- Change only the exact lines that are wrong. Zero unrelated edits.
- After the change, manually trace the reproduction case line by line in your head.
- Write a regression test named after the exact scenario (not "test_fix").
- Run the full existing test suite. If none exists, write one for the module first.

---

## Phase 4: PRODUCTION CODE STANDARDS

Apply these when writing any new code as part of a fix or feature:

```
Data flow first: input → transform → output. Code is a consequence.
Layering:        entry point → service/domain → data access → external I/O
Resources:       context managers (with) for every file, socket, connection, lock
Memory:          stream large data; never load unbounded collections into memory
Functions:       one job per function; if name contains "and" = two functions
Types:           type annotations on every public function signature
No placeholders: every written function must be complete and correct
```

---

## Phase 5: FEATURE INTEGRATION (Non-Breaking)

1. **Read the existing module** before writing. Identify conventions, error return style, logging pattern.
2. **Find the seam**: the exact boundary where new behavior inserts without touching existing paths.
3. **Extend, don't modify**: new optional parameter with defaults; new method; new class. Last resort: modify an existing path.
4. **Gate new behavior**: behind a flag or branch until fully wired. Never leave a half-implemented path active.
5. **Verify**: existing tests pass unmodified. New integration test covers the full entry-to-storage path.

---

## Phase 6: AUDIT CHECKLIST (Run Before Declaring Done)

**Security**
- [ ] No string interpolation into SQL, shell commands, or file paths from user input
- [ ] Auth/permission checks at the boundary layer, not buried inside service functions
- [ ] No hard-coded secrets, tokens, passwords, or API keys anywhere in the diff
- [ ] Third-party libraries that touch network/fs on user-supplied input treated as untrusted

**Performance**
- [ ] No DB queries or I/O calls inside loops over unbounded data (N+1 check)
- [ ] No blocking I/O on async paths
- [ ] No O(n²) loops over unbounded collections without justification

**Concurrency**
- [ ] Shared mutable state across threads/tasks has explicit synchronization
- [ ] No assumed ordering of async operations
- [ ] Every background task has an error handler

**Error Paths**
- [ ] Every external I/O call has an explicit timeout
- [ ] Error messages returned to users contain no stack traces, internal paths, or schema info
- [ ] All exception paths release resources before propagating

---

## Core Principles (Always Active)

1. Read first, write second, test third. In that order.
2. Smallest correct change is the best change.
3. Never claim success without running the code and reading the output.
4. If the same fix fails twice: stop, reassess root cause, change approach entirely.
5. Code is communication — write for the next engineer, not the machine.
