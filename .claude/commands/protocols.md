# Protocols Command

**Usage:** `/protocols`

**Description:** Load all critical operational protocols and system status for AI operators.

**What it does:**
- Loads the unified AI operator manual
- Reviews current system status and critical alerts
- Injects real-time protocol context
- Provides operational reminders and guidelines

**Files reviewed:**
- `SQUIRT_AI_OPERATOR_MANUAL.md` - Single source of truth for all protocols
- `VALIDATION_CONFLICT_RESOLUTION.md` - Current system status
- `VISUAL_VALIDATION_PROTOCOL.md` - Visual validation requirements
- Real-time system state via protocol injection

**Example:**
```
/protocols
```

This will immediately load all current protocols, system status, and operational guidelines into context.