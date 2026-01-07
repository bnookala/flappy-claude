#!/bin/bash
# Stop hook - signals game that Claude has finished work

SIGNAL_FILE="/tmp/flappy-claude-signal"
THRESHOLD_FILE="/tmp/flappy-claude-threshold"
FIRST_TOOL_FILE="/tmp/flappy-claude-first-tool"
TOOL_COUNT_FILE="/tmp/flappy-claude-tool-count"
DEFAULT_THRESHOLD=5
DECLINED_BASE_THRESHOLD=10  # Higher base if user declined this session

# Debug logging
echo "$(date): Stop hook fired" >> /tmp/flappy-claude-hook.log

# Read stdin (JSON input from Claude Code)
cat > /dev/null

# Write "ready" to signal file to notify the game (if game is running)
if [ -d "/tmp/flappy-claude-lock" ]; then
    echo "ready" > "$SIGNAL_FILE"
    echo "$(date): Wrote 'ready' to $SIGNAL_FILE (game running)" >> /tmp/flappy-claude-hook.log
fi

# Reset for next conversation turn
# If threshold was increased (user declined), reset to higher base
# Otherwise reset to default
CURRENT_THRESHOLD=$(cat "$THRESHOLD_FILE" 2>/dev/null || echo "$DEFAULT_THRESHOLD")
if [ "$CURRENT_THRESHOLD" -gt "$DEFAULT_THRESHOLD" ]; then
    # User declined at least once - use higher base for next turn
    echo "$DECLINED_BASE_THRESHOLD" > "$THRESHOLD_FILE"
    echo "$(date): Reset threshold to $DECLINED_BASE_THRESHOLD (user declined previously)" >> /tmp/flappy-claude-hook.log
else
    # User played or never got prompted - reset to default
    echo "$DEFAULT_THRESHOLD" > "$THRESHOLD_FILE"
    echo "$(date): Reset threshold to $DEFAULT_THRESHOLD" >> /tmp/flappy-claude-hook.log
fi

# Reset tool count for next turn
rm -f "$FIRST_TOOL_FILE" "$TOOL_COUNT_FILE"

# Always exit 0 to not block Claude
exit 0
