# Behavior Protocol Enforcer

**Enforce behavior protocols for main and subprocess agents.**

## Description

This skill ensures that all agents (main and subprocesses) follow the defined behavior protocols. It automatically injects protocol rules at session start and provides tools to read and check compliance.

## Activation

- **Auto-load**: This skill is automatically loaded in all sessions (main and subprocess) when the workspace is active.
- **Trigger**: On session start, the skill sends a system event reminding the agent to read the appropriate behavior protocol.

## Protocols

The skill references the following protocol files (located in `memory/long-term/`):

- `BEHAVIOR-PROTOCOL.md` – Main agent (小青)
- `BEHAVIOR-PROTOCOL-PLAN.md` – Plan subprocess
- `BEHAVIOR-PROTOCOL-ARCHITECT.md` – Architect subprocess
- `BEHAVIOR-PROTOCOL-CODER.md` – Coder subprocess
- `BEHAVIOR-PROTOCOL-ENV-ENGINEER.md` – Env-engineer subprocess
- `BEHAVIOR-PROTOCOL-DEBUGGER.md` – Debugger subprocess

## Tools

### `read_behavior_protocol`

Read the behavior protocol file for the current session type.

**Parameters:**
- `protocol` (optional): Specific protocol to read (e.g., "architect"). If omitted, the skill auto-detects based on session label.

**Behavior:**
1. If the session label contains "plan", "architect", "coder", "env-engineer", or "debugger", reads the corresponding subprocess protocol.
2. Otherwise, reads the main protocol (`BEHAVIOR-PROTOCOL.md`).
3. Returns the protocol content as a system message.

**Usage:**
```yaml
- read_behavior_protocol
- read_behavior_protocol protocol="architect"
```

### `check_compliance`

Check if the agent's recent actions comply with the protocol.

**Parameters:**
- `actions` (optional): List of recent actions to check. If omitted, uses the last 10 messages from session history.

**Behavior:**
1. Fetches the relevant protocol.
2. Compares the actions against protocol rules (e.g., "Did the agent read the protocol before acting?").
3. Returns a compliance report.

**Usage:**
```yaml
- check_compliance
- check_compliance actions=["spawn", "edit", "exec"]
```

## System Events

### On session start

The skill injects the following system event:

```
System: Behavior Protocol Enforcer loaded. Please read the appropriate behavior protocol before proceeding.
```

If the session is a subprocess (detected by label), the event includes a hint:

```
System: You are a [role] subprocess. Read BEHAVIOR-PROTOCOL-[ROLE].md before starting.
```

## Configuration

### Skill location
- Workspace: `skills/behavior-protocol-enforcer/`
- Protocol files: `memory/long-term/BEHAVIOR-PROTOCOL*.md`

### Customization
To add a new subprocess protocol:
1. Create `BEHAVIOR-PROTOCOL-<ROLE>.md` in `memory/long-term/`
2. Update the `Protocols` section above.

## Dependencies

- OpenClaw workspace with `memory/long-term/` directory.
- Protocol files must exist (skill will warn if missing).

## Examples

### Main session start
```
System: Behavior Protocol Enforcer loaded. Please read BEHAVIOR-PROTOCOL.md before proceeding.
Agent: (reads protocol via read_behavior_protocol)
```

### Architect subprocess spawn
```
System: You are an architect subprocess. Read BEHAVIOR-PROTOCOL-ARCHITECT.md before starting.
Architect: (reads protocol, then proceeds with design task)
```

## Notes

- This skill does not force compliance; it only reminds and provides tools.
- Agents are expected to voluntarily follow the protocols.
- Protocol files are synchronized via Git across devices.

## Version

1.0 (2026-04-07)
