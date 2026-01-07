#!/bin/bash
# PreToolUse hook - prompts user to play Flappy Claude during wait

SIGNAL_FILE="/tmp/flappy-claude-signal"

# Check if game is already running (signal file exists)
if [ -f "$SIGNAL_FILE" ]; then
    exit 0
fi

# Read stdin (JSON input from Claude Code, not used but must be consumed)
read -t 0.1 json_input 2>/dev/null || true

# Prompt user with timeout
echo -n "Would you like to play Flappy Claude? (y)es/(n)o: "

# Read single character with short timeout
read -t 3 -n 1 response

echo  # Newline after input

# Check response
case "$response" in
    [Yy])
        # Create signal file to prevent duplicate prompts
        touch "$SIGNAL_FILE"
        # Launch game in background
        uvx flappy-claude &
        ;;
    *)
        # User declined or timeout - continue normally
        ;;
esac

# Always exit 0 to not block Claude
exit 0
