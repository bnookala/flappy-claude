#!/bin/bash
# Stop hook - signals game that Claude has finished work
# Also increments conversation turn counter

SIGNAL_FILE="/tmp/flappy-claude-signal"
TOOL_COUNT_FILE="/tmp/flappy-claude-tool-count"
TURN_COUNT_FILE="/tmp/flappy-claude-turns"

# Read stdin (JSON input from Claude Code)
cat > /dev/null

# Write "ready" to signal file to notify the game (if game is running)
if [ -d "/tmp/flappy-claude-lock" ]; then
    echo "ready" > "$SIGNAL_FILE"
    echo "$(date): Wrote 'ready' to $SIGNAL_FILE (game running)" >> /tmp/flappy-claude-hook.log
fi

# Increment conversation turn counter
CURRENT_TURN=$(cat "$TURN_COUNT_FILE" 2>/dev/null || echo "0")
NEW_TURN=$((CURRENT_TURN + 1))
echo "$NEW_TURN" > "$TURN_COUNT_FILE"

# Reset tool count for next turn
rm -f "$TOOL_COUNT_FILE"

echo "$(date): Stop hook - turn $NEW_TURN complete" >> /tmp/flappy-claude-hook.log

# Always exit 0 to not block Claude
exit 0
