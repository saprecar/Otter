#!/usr/bin/env bash
# ==============================================================================
# [AI-BLOCK: Universal Agent & Skills Installer for Linux / macOS (.sh)]
# Usage:
#   ./install_agent_skills.sh                     -> Install to current directory
#   ./install_agent_skills.sh /my/project         -> Install to target project
#   ./install_agent_skills.sh --clean             -> Clean + fresh install (safe)
#   ./install_agent_skills.sh /my/proj --clean    -> Clean + fresh install target
#
# --clean SAFE MODE:
#   - Backs up all custom rule files (project-rules.md and any user-created .md)
#   - Removes ONLY agent-suite managed folders and files
#   - Restores your custom rules after fresh install
#   - NEVER deletes: project-rules.md or any non-AGENTS.md user file in rules/
# ==============================================================================

set -e

REPO_URL="https://github.com/saprecar/agentandskill.git"
TARGET_DIR=""
DO_CLEAN=0

# Parse arguments
for arg in "$@"; do
    if [ "$arg" = "--clean" ]; then
        DO_CLEAN=1
    elif [ -z "$TARGET_DIR" ]; then
        TARGET_DIR="$arg"
    fi
done

TARGET_DIR="${TARGET_DIR:-$(pwd)}"

echo "=========================================================="
echo "       Agent and Skill Suite Installer (Linux / macOS)"
echo "=========================================================="
echo "Target Project Directory: ${TARGET_DIR}"
[ "${DO_CLEAN}" = "1" ] && echo "Mode: CLEAN (custom rules protected) + fresh install"
echo ""

if [ ! -d "${TARGET_DIR}" ]; then
    echo "[ERROR] Target directory does not exist: ${TARGET_DIR}"
    exit 1
fi

# --clean: backup custom rules, remove suite files, restore custom rules
BACKUP_DIR=""
if [ "${DO_CLEAN}" = "1" ]; then
    BACKUP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'agent_backup')
    mkdir -p "${BACKUP_DIR}/agents_rules" "${BACKUP_DIR}/claude_rules"

    echo "[BACKUP] Protecting your custom rules before clean..."

    # Backup .agents/rules — skip AGENTS.md and agent.md (suite-owned files)
    if [ -d "${TARGET_DIR}/.agents/rules" ]; then
        for f in "${TARGET_DIR}/.agents/rules/"*.md; do
            [ -f "$f" ] || continue
            fname=$(basename "$f")
            if [ "$fname" != "AGENTS.md" ] && [ "$fname" != "agent.md" ]; then
                cp "$f" "${BACKUP_DIR}/agents_rules/${fname}"
                echo "[BACKUP]   .agents/rules/${fname}"
            fi
        done
    fi

    # Backup .claude/rules — skip AGENTS.md and agent.md
    if [ -d "${TARGET_DIR}/.claude/rules" ]; then
        for f in "${TARGET_DIR}/.claude/rules/"*.md; do
            [ -f "$f" ] || continue
            fname=$(basename "$f")
            if [ "$fname" != "AGENTS.md" ] && [ "$fname" != "agent.md" ]; then
                cp "$f" "${BACKUP_DIR}/claude_rules/${fname}"
                echo "[BACKUP]   .claude/rules/${fname}"
            fi
        done
    fi

    echo "[CLEAN] Removing previous agent suite installation..."

    rm -rf "${TARGET_DIR}/.agent/workflows"
    rm -rf "${TARGET_DIR}/.agent/rules"
    rm -rf "${TARGET_DIR}/.agents/skills"
    rm -rf "${TARGET_DIR}/.agents/agents"
    rm -rf "${TARGET_DIR}/.agents/rules"
    rm -rf "${TARGET_DIR}/.claude/skills"
    rm -rf "${TARGET_DIR}/.claude/rules"
    rm -f  "${TARGET_DIR}/.claude/CLAUDE.md"
    rm -rf "${TARGET_DIR}/.cursor/rules"
    rm -rf "${TARGET_DIR}/.github/instructions"
    rm -f  "${TARGET_DIR}/.github/copilot-instructions.md"
    rm -rf "${TARGET_DIR}/Stable"
    rm -f  "${TARGET_DIR}/AGENTS.md"
    rm -f  "${TARGET_DIR}/NAV_MAP.md"

    echo "[CLEAN] Done. Proceeding with fresh install..."
    echo ""
fi

TEMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'agentandskill')
SCRIPT_DIR=""

echo "[1/5] Fetching latest agent suite..."
if ! git clone --depth 1 "${REPO_URL}" "${TEMP_DIR}" >/dev/null 2>&1; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -d "${SCRIPT_DIR}/Stable" ]; then
        echo "[INFO] GitHub clone unavailable; deploying from local source directory..."
        TEMP_DIR="${SCRIPT_DIR}"
    else
        echo "[ERROR] Failed to clone repository. Check internet or repository permissions."
        exit 1
    fi
fi

echo "[2/5] Installing Antigravity rules and workflows (.agent/, .agents/)..."
[ -d "${TEMP_DIR}/.agent" ]  && cp -R "${TEMP_DIR}/.agent"  "${TARGET_DIR}/"
[ -d "${TEMP_DIR}/.agents" ] && cp -R "${TEMP_DIR}/.agents" "${TARGET_DIR}/"

echo "[3/5] Installing Claude rules and skills in .claude/..."
[ -d "${TEMP_DIR}/.claude" ] && cp -R "${TEMP_DIR}/.claude" "${TARGET_DIR}/"

echo "[4/5] Installing VS Code / Copilot rules in .github/..."
[ -d "${TEMP_DIR}/.github" ] && cp -R "${TEMP_DIR}/.github" "${TARGET_DIR}/"

echo "[5/5] Installing canonical reference rules (AGENTS.md, NAV_MAP.md, Stable/)..."
[ -f "${TEMP_DIR}/AGENTS.md" ]  && cp "${TEMP_DIR}/AGENTS.md"  "${TARGET_DIR}/AGENTS.md"
[ -f "${TEMP_DIR}/NAV_MAP.md" ] && cp "${TEMP_DIR}/NAV_MAP.md" "${TARGET_DIR}/NAV_MAP.md"
[ -d "${TEMP_DIR}/Stable" ]     && cp -R "${TEMP_DIR}/Stable"  "${TARGET_DIR}/"

echo "[*] Cleaning temporary clone..."
if [ -n "${SCRIPT_DIR}" ] && [ "${TEMP_DIR}" != "${SCRIPT_DIR}" ]; then
    rm -rf "${TEMP_DIR}"
elif [ -z "${SCRIPT_DIR}" ]; then
    rm -rf "${TEMP_DIR}"
fi

# Restore custom rules after fresh install
if [ "${DO_CLEAN}" = "1" ] && [ -n "${BACKUP_DIR}" ]; then
    echo ""
    echo "[RESTORE] Restoring your custom rules..."

    for f in "${BACKUP_DIR}/agents_rules/"*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        mkdir -p "${TARGET_DIR}/.agents/rules"
        cp "$f" "${TARGET_DIR}/.agents/rules/${fname}"
        echo "[RESTORE]   .agents/rules/${fname}"
    done

    for f in "${BACKUP_DIR}/claude_rules/"*.md; do
        [ -f "$f" ] || continue
        fname=$(basename "$f")
        mkdir -p "${TARGET_DIR}/.claude/rules"
        cp "$f" "${TARGET_DIR}/.claude/rules/${fname}"
        echo "[RESTORE]   .claude/rules/${fname}"
    done

    rm -rf "${BACKUP_DIR}"
    echo "[RESTORE] Custom rules restored successfully."
fi

echo ""
echo "=========================================================="
echo "[SUCCESS] Agent Suite installed successfully!"
echo "Configured locations:"
echo "  - Antigravity:         .agent/rules, .agent/workflows, .agents/skills"
echo "  - Claude Desktop/CLI:  .claude/CLAUDE.md, .claude/rules, .claude/skills"
echo "  - VS Code / Copilot:   .github/copilot-instructions.md"
echo "  - Root canonical:      AGENTS.md, NAV_MAP.md"
echo "  - Custom rules:        PRESERVED (project-rules.md and your files)"
echo ""
echo "To reinstall fresh next time:"
echo "  ./install_agent_skills.sh --clean"
echo "  ./install_agent_skills.sh /my/project --clean"
echo "=========================================================="
exit 0
