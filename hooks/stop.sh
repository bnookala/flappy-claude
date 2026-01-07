#!/bin/bash
# Stop hook - signals game that Claude has finished work

SIGNAL_FILE="/tmp/flappy-claude-signal"

# Read stdin (JSON input from Claude Code, not used but must be consumed)
read -t 0.1 json_input 2>/dev/null || true

# Write "ready" to signal file to notify the game
echo "ready" > "$SIGNAL_FILE"

# Always exit 0 to not block Claude
exit 0
