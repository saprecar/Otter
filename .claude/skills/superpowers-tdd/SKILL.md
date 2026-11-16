---
name: superpowers-tdd
description: Enforces strict red-green Test-Driven Development (TDD), write failing tests first, minimum implementation to pass, and regression guards.
---

# Superpowers TDD Skill

## Purpose
Prevents premature coding and untested logic. Guarantees that every new feature or bugfix is backed by verified automated tests before merging.

## Core Directives
1. **Red First**: Write a small, targeted test that reproduces the bug or asserts the new requirement. Run it and verify that it fails with the expected error.
2. **Minimal Green**: Write the absolute minimum code required to make the test pass. Do not add speculative features or defensive wrappers.
3. **Refactor & Keep Green**: Clean up syntax and ensure AI block comments are added (`# [AI-BLOCK: ...]`). Re-verify that all tests pass.
4. **Never Mock What You Can Test Directly**: Use real isolated environments or native fixtures. Avoid brittle triple-mocked mocks.
5. **Zero Assumptions**: Do not claim success until test execution command exits with code 0.

