---
name: ui-ux-craft
description: Designs and generates clean, production-grade frontend UI/UX components (Tailwind CSS, React, HTML) avoiding generic AI slop and awkward spacing.
---

# UI/UX Craft Skill

## Purpose
Enforces professional UI/UX standards, modern design tokens, accessible color palettes, and clean responsive layouts. Eliminates ugly AI templates and generic purple gradients.

## 1. Core Visual Principles
- **No Cookie-Cutter Gradients**: Use crisp, deliberate neutral backgrounds (`#0d1117`, `#090d16`, `#ffffff`, `#f8fafc`) with subtle borders (`#30363d` or `slate-200`) instead of blurry multi-color AI gradients.
- **Strict Spacing System**: Use standard 4px/8px multiples (`gap-2`, `gap-4`, `p-4`, `p-6`). Never mix arbitrary pixel padding.
- **Visual Hierarchy**:
  - H1/Titles: Bold, high contrast (`text-slate-900` or `text-slate-100`).
  - Body: Readable neutral (`text-slate-600` or `text-slate-400`).
  - Metadata / Labels: Subdued mono/small text (`text-xs text-slate-500`).

## 2. Interactive Component Rules
- **Buttons**:
  - Primary: High contrast solid button with distinct hover state and active scale (`hover:opacity-90 active:scale-95`).
  - Secondary: Ghost or border button (`border border-slate-700 bg-transparent hover:bg-slate-800`).
- **Cards & Containers**:
  - Subtle borders with soft drop shadows (`border border-slate-800 bg-slate-900/50 shadow-sm rounded-lg`).
  - Content must have breathing room (`p-5` or `p-6`).

## 3. Responsive Layout Standard
- Mobile-first flex and grid layouts (`flex flex-col md:flex-row`).
- All interactive controls must be at least 40px touch-target safe on mobile screens.

