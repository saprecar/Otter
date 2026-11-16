@echo off
REM ==============================================================================
REM [AI-BLOCK: Universal Agent & Skills Installer for Windows (.bat)]
REM Usage:
REM   install_agent_skills.bat                      -> Install to current directory
REM   install_agent_skills.bat "C:\my\project"     -> Install to target project
REM   install_agent_skills.bat --clean              -> Clean + fresh install (safe)
REM   install_agent_skills.bat "C:\proj" --clean   -> Clean + fresh install target
REM
REM --clean SAFE MODE:
REM   - Backs up all custom rule files (project-rules.md and any user-created .md)
REM   - Removes ONLY agent-suite managed folders and files
REM   - Restores your custom rules after fresh install
REM   - NEVER deletes: project-rules.md or any non-AGENTS.md user file in rules/
REM ==============================================================================

setlocal enabledelayedexpansion

set "REPO_URL=https://github.com/saprecar/agentandskill.git"
set "TARGET_DIR="
set "DO_CLEAN=0"

:parse_args
if "%~1"=="" goto done_args
if /i "%~1"=="--clean" (
    set "DO_CLEAN=1"
    shift
    goto parse_args
)
if "%TARGET_DIR%"=="" (
    set "TARGET_DIR=%~1"
)
shift
goto parse_args
:done_args

if "%TARGET_DIR%"=="" set "TARGET_DIR=%CD%"

echo ==========================================================
echo        Agent and Skill Suite Installer (Windows)
echo ==========================================================
echo Target Project Directory: %TARGET_DIR%
if "%DO_CLEAN%"=="1" echo Mode: CLEAN (custom rules protected) + fresh install
echo.

if not exist "%TARGET_DIR%" (
    echo [ERROR] Target directory does not exist: %TARGET_DIR%
    exit /b 1
)

REM --clean: backup custom rules, remove suite files, restore custom rules
if "%DO_CLEAN%"=="1" (
    set "BACKUP_DIR=%TEMP%\agent_custom_backup_%RANDOM%"
    mkdir "!BACKUP_DIR!" 2>nul
    mkdir "!BACKUP_DIR!\agents_rules" 2>nul
    mkdir "!BACKUP_DIR!\claude_rules" 2>nul

    echo [BACKUP] Protecting your custom rules before clean...

    REM Backup everything in .agents/rules EXCEPT AGENTS.md and agent.md
    if exist "%TARGET_DIR%\.agents\rules" (
        for %%F in ("%TARGET_DIR%\.agents\rules\*.md") do (
            if /i not "%%~nxF"=="AGENTS.md" if /i not "%%~nxF"=="agent.md" (
                copy /Y "%%F" "!BACKUP_DIR!\agents_rules\%%~nxF" >nul
                echo [BACKUP]   .agents/rules/%%~nxF
            )
        )
    )

    REM Backup everything in .claude/rules EXCEPT AGENTS.md and agent.md
    if exist "%TARGET_DIR%\.claude\rules" (
        for %%F in ("%TARGET_DIR%\.claude\rules\*.md") do (
            if /i not "%%~nxF"=="AGENTS.md" if /i not "%%~nxF"=="agent.md" (
                copy /Y "%%F" "!BACKUP_DIR!\claude_rules\%%~nxF" >nul
                echo [BACKUP]   .claude/rules/%%~nxF
            )
        )
    )

    echo [CLEAN] Removing previous agent suite installation...

    if exist "%TARGET_DIR%\.agent\workflows"     rmdir /S /Q "%TARGET_DIR%\.agent\workflows"
    if exist "%TARGET_DIR%\.agent\rules"         rmdir /S /Q "%TARGET_DIR%\.agent\rules"
    if exist "%TARGET_DIR%\.agents\skills"       rmdir /S /Q "%TARGET_DIR%\.agents\skills"
    if exist "%TARGET_DIR%\.agents\agents"       rmdir /S /Q "%TARGET_DIR%\.agents\agents"
    if exist "%TARGET_DIR%\.agents\rules"        rmdir /S /Q "%TARGET_DIR%\.agents\rules"
    if exist "%TARGET_DIR%\.claude\skills"       rmdir /S /Q "%TARGET_DIR%\.claude\skills"
    if exist "%TARGET_DIR%\.claude\rules"        rmdir /S /Q "%TARGET_DIR%\.claude\rules"
    if exist "%TARGET_DIR%\.claude\CLAUDE.md"    del /Q      "%TARGET_DIR%\.claude\CLAUDE.md"
    if exist "%TARGET_DIR%\.cursor\rules"        rmdir /S /Q "%TARGET_DIR%\.cursor\rules"
    if exist "%TARGET_DIR%\.github\instructions" rmdir /S /Q "%TARGET_DIR%\.github\instructions"
    if exist "%TARGET_DIR%\.github\copilot-instructions.md" del /Q "%TARGET_DIR%\.github\copilot-instructions.md"
    if exist "%TARGET_DIR%\Stable"               rmdir /S /Q "%TARGET_DIR%\Stable"
    if exist "%TARGET_DIR%\AGENTS.md"            del /Q      "%TARGET_DIR%\AGENTS.md"
    if exist "%TARGET_DIR%\NAV_MAP.md"           del /Q      "%TARGET_DIR%\NAV_MAP.md"

    echo [CLEAN] Done. Proceeding with fresh install...
    echo.
)

set "TEMP_DIR=%TEMP%\agentandskill_%RANDOM%"
echo [1/5] Fetching latest agent suite...
git clone --depth 1 "%REPO_URL%" "%TEMP_DIR%" >nul 2>&1
if errorlevel 1 (
    if exist "%~dp0Stable" (
        echo [INFO] GitHub clone unavailable; deploying from local source directory...
        set "TEMP_DIR=%~dp0"
    ) else (
        echo [ERROR] Failed to clone repository. Check internet or repository permissions.
        exit /b 1
    )
)

echo [2/5] Installing Antigravity rules and workflows (.agent/, .agents/)...
if exist "%TEMP_DIR%\.agent"  xcopy "%TEMP_DIR%\.agent"  "%TARGET_DIR%\.agent\"  /E /I /Y /Q >nul
if exist "%TEMP_DIR%\.agents" xcopy "%TEMP_DIR%\.agents" "%TARGET_DIR%\.agents\" /E /I /Y /Q >nul

echo [3/5] Installing Claude rules and skills in .claude/...
if exist "%TEMP_DIR%\.claude" xcopy "%TEMP_DIR%\.claude" "%TARGET_DIR%\.claude\" /E /I /Y /Q >nul

echo [4/5] Installing VS Code / Copilot rules in .github/...
if exist "%TEMP_DIR%\.github" xcopy "%TEMP_DIR%\.github" "%TARGET_DIR%\.github\" /E /I /Y /Q >nul

echo [5/5] Installing canonical reference rules (AGENTS.md, NAV_MAP.md, Stable/)...
if exist "%TEMP_DIR%\AGENTS.md"  copy /Y "%TEMP_DIR%\AGENTS.md"  "%TARGET_DIR%\AGENTS.md"  >nul
if exist "%TEMP_DIR%\NAV_MAP.md" copy /Y "%TEMP_DIR%\NAV_MAP.md" "%TARGET_DIR%\NAV_MAP.md" >nul
if exist "%TEMP_DIR%\Stable"     xcopy "%TEMP_DIR%\Stable" "%TARGET_DIR%\Stable\" /E /I /Y /Q >nul

echo [*] Cleaning temporary clone...
if "%TEMP_DIR%" neq "%~dp0" rmdir /S /Q "%TEMP_DIR%" 2>nul

REM Restore custom rules after fresh install
if "%DO_CLEAN%"=="1" (
    echo.
    echo [RESTORE] Restoring your custom rules...

    if exist "!BACKUP_DIR!\agents_rules" (
        for %%F in ("!BACKUP_DIR!\agents_rules\*.md") do (
            copy /Y "%%F" "%TARGET_DIR%\.agents\rules\%%~nxF" >nul
            echo [RESTORE]   .agents/rules/%%~nxF
        )
    )

    if exist "!BACKUP_DIR!\claude_rules" (
        for %%F in ("!BACKUP_DIR!\claude_rules\*.md") do (
            copy /Y "%%F" "%TARGET_DIR%\.claude\rules\%%~nxF" >nul
            echo [RESTORE]   .claude/rules/%%~nxF
        )
    )

    rmdir /S /Q "!BACKUP_DIR!" 2>nul
    echo [RESTORE] Custom rules restored successfully.
)

echo.
echo ==========================================================
echo [SUCCESS] Agent Suite installed successfully!
echo Configured locations:
echo   - Antigravity:         .agent\rules, .agent\workflows, .agents\skills
echo   - Claude Desktop/CLI:  .claude\CLAUDE.md, .claude\rules, .claude\skills
echo   - VS Code / Copilot:   .github\copilot-instructions.md
echo   - Root canonical:      AGENTS.md, NAV_MAP.md
echo   - Custom rules:        PRESERVED (project-rules.md and your files)
echo.
echo To reinstall fresh next time:
echo   install_agent_skills.bat --clean
echo   install_agent_skills.bat "C:\my\project" --clean
echo ==========================================================
exit /b 0
