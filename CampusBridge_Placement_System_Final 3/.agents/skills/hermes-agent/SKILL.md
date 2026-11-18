---
name: hermes-agent
description: >-
  Connect, prompt, and collaborate with the local Hermes Agent running in the background.
  Use this skill when the user asks to communicate with, prompt, or delegate tasks to Hermes,
  or when executing workflows requiring Hermes's real Chrome profile, gateway, or session management.
---

# Hermes Agent Integration Skill

This skill enables Antigravity to communicate with the local **Hermes Agent** running on your system, start and resume shared sessions, and delegate tasks (such as real Chrome profile navigation, messaging gateway actions, or code execution) on an agent-to-agent level.

---

## Capabilities & Architecture

- **Agent-to-Agent Communication**: Send instructions and receive structured responses from Hermes.
- **Session Continuity**: Resume or create named conversation threads (`--continue <name> --create-if-missing`) so context is preserved between turns.
- **Real Profile Automation**: Hermes can interact directly with your active Chrome profile or background services via its running Gateway (PID tracked).
- **Clean Output Filtering**: Uses `--oneshot -Q --format text --source tool` with ANSI stripping to provide parseable output.

---

## Quick Reference Commands

All helper actions are managed via `scripts/hermes_bridge.py`:

### 1. Check Hermes & Gateway Status
```bash
python3 .agents/skills/hermes-agent/scripts/hermes_bridge.py status
```

### 2. Send an Agentic Prompt (Single Turn)
```bash
python3 .agents/skills/hermes-agent/scripts/hermes_bridge.py query "Your instruction here"
```

### 3. Continue or Start a Named Session (Multi-turn Collaboration)
```bash
python3 .agents/skills/hermes-agent/scripts/hermes_bridge.py query "Follow-up question" --session "campusbridge-audit"
```

### 4. List Recent Sessions
```bash
python3 .agents/skills/hermes-agent/scripts/hermes_bridge.py sessions
```

---

## Agentic Guidelines

1. **Task Delegation**:
   - For real browser profile actions (accessing authenticated tabs or user Chrome sessions), delegate to Hermes using `--session "browser-task"`.
   - For standalone project audits or second-opinion reviews, pass the specific files and concise instructions.
2. **Timeouts**:
   - Large models (like Nemotron 550B) may take 15–30 seconds to generate deep reasoning. Default timeout is 120s; adjust with `--timeout <seconds>` if executing long tasks.
3. **Session Re-use**:
   - Always group related task requests under a named `--session` so Hermes retains memory of previous turns.
