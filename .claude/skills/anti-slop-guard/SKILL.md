---
name: anti-slop-guard
description: Eliminates redundant boilerplate, over-engineering, verbose conversational slop, and trivial comments from code and UI output.
---

# Anti-Slop Guard Skill

## Purpose
Enforces ruthless simplicity, concise syntax, and zero-slop generation across backend logic, web UI, mobile app UI, and technical documentation. Incorporates patterns from `dabit3/deslop` and `petergyang/no-ai-slop`.

## Anti-Slop Directives

### 1. Code & UI Slop Elimination
- **Zero Redundancy**: Do not generate single-call wrapper functions or premature abstraction layers.
- **No Obvious Comments**: Do not write comments stating the obvious (e.g. `// set count to 0`). Only state non-obvious architecture reasons.
- **Flat Hierarchy**: Favor straightforward procedural or standard component composition over deep inheritance and premature factory designs.
- **No Placeholder Stubs**: Reject empty `TODO` stubs or fake unlinked handlers.
- **UI Minimalism**:
  - Web/App UI: Output standard Tailwind / Headless tokens.
  - Avoid excessive inline wrapper divs, multi-level styling wrappers, and fake placeholder mockups.

### 2. Prose, Docs & Conversational Slop Elimination (`petergyang/no-ai-slop`)
- **No Throat-Clearing Openers**: Ban introductory filler phrases (e.g., *"Sure, I can help you with that"*, *"Let me be clear"*, *"Here is the thing"*). Get straight to the answer.
- **No Binary Contrasts**: Eliminate synthetic LLM phrasing like *"It’s not X. It’s Y."* or *"Not just a tool, but an ecosystem."*
- **No Fake-Profound Endings**: Ban generic clichés (e.g., *"The future isn't coming, it's already here"*).
- **Voice Protection**: Keep explanations dense, direct, practical, and devoid of corporate fluff.
