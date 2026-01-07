#!/bin/bash
# PreToolUse hook - prompts user to play Flappy Claude during wait
# IMPORTANT: This hook exits immediately so Claude isn't blocked.
# All user interaction happens in a background process.

# Configuration
DEFAULT_TOOL_THRESHOLD=5    # Initial tool calls before first prompt
BACKOFF_MULTIPLIER=4        # Multiply threshold by this when user declines
MAX_TOOL_THRESHOLD=100      # Maximum threshold (don't ask after this many declines)
MIN_SECONDS=30              # OR minimum seconds since first tool call

# File paths
SIGNAL_FILE="/tmp/flappy-claude-signal"
LOCK_DIR="/tmp/flappy-claude-lock"
FIRST_TOOL_FILE="/tmp/flappy-claude-first-tool"
TOOL_COUNT_FILE="/tmp/flappy-claude-tool-count"
THRESHOLD_FILE="/tmp/flappy-claude-threshold"  # Current threshold (increases on decline)
FLAPPY_CLAUDE_DIR="${FLAPPY_CLAUDE_DIR:-$HOME/code/flappy-claude}"
TERM_PROG="$TERM_PROGRAM"  # Capture before backgrounding

# Consume stdin immediately so we don't block
cat > /dev/null &

# Check if game/prompt is already running
if [ -d "$LOCK_DIR" ]; then
    exit 0
fi

# Track first tool call timestamp
if [ ! -f "$FIRST_TOOL_FILE" ]; then
    date +%s > "$FIRST_TOOL_FILE"
fi

# Increment tool count (with file locking to prevent race conditions)
(
    flock -x 200
    if [ -f "$TOOL_COUNT_FILE" ]; then
        COUNT=$(cat "$TOOL_COUNT_FILE")
        COUNT=$((COUNT + 1))
    else
        COUNT=1
    fi
    echo "$COUNT" > "$TOOL_COUNT_FILE"
) 200>/tmp/flappy-claude-count.lock

COUNT=$(cat "$TOOL_COUNT_FILE" 2>/dev/null || echo "0")
FIRST_TOOL_TIME=$(cat "$FIRST_TOOL_FILE" 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
ELAPSED=$((CURRENT_TIME - FIRST_TOOL_TIME))

# Get current threshold (or use default)
CURRENT_THRESHOLD=$(cat "$THRESHOLD_FILE" 2>/dev/null || echo "$DEFAULT_TOOL_THRESHOLD")

# Only proceed if threshold met
if [ "$COUNT" -lt "$CURRENT_THRESHOLD" ] && [ "$ELAPSED" -lt "$MIN_SECONDS" ]; then
    exit 0
fi

# Atomic lock to prevent multiple prompts
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    exit 0
fi

# Create a detached launcher script and run it completely independently
LAUNCHER="/tmp/flappy-claude-launcher-$$.sh"
cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/bin/bash
SIGNAL_FILE="$1"
LOCK_DIR="$2"
FIRST_TOOL_FILE="$3"
TOOL_COUNT_FILE="$4"
FLAPPY_CLAUDE_DIR="$5"
TERM_PROG="$6"
THRESHOLD_FILE="$7"
BACKOFF_MULTIPLIER="$8"
MAX_TOOL_THRESHOLD="$9"
LOG="/tmp/flappy-claude-hook.log"

echo "$(date): Showing dialog (detached)" >> "$LOG"

# Ask user with a macOS dialog
RESPONSE=$(osascript -e 'display dialog "Play Flappy Claude while Claude works?" buttons {"No", "Yes"} default button "Yes" giving up after 15' 2>/dev/null)

if [[ "$RESPONSE" != *"Yes"* ]]; then
    # User declined - increase threshold for next time (backoff)
    CURRENT=$(cat "$THRESHOLD_FILE" 2>/dev/null || echo "5")
    NEW_THRESHOLD=$((CURRENT * BACKOFF_MULTIPLIER))
    if [ "$NEW_THRESHOLD" -gt "$MAX_TOOL_THRESHOLD" ]; then
        NEW_THRESHOLD="$MAX_TOOL_THRESHOLD"
    fi
    echo "$NEW_THRESHOLD" > "$THRESHOLD_FILE"
    # Reset tool count so we count from here
    echo "0" > "$TOOL_COUNT_FILE"
    date +%s > "$FIRST_TOOL_FILE"

    rmdir "$LOCK_DIR" 2>/dev/null
    echo "$(date): User declined - backoff threshold now $NEW_THRESHOLD" >> "$LOG"
    rm -f "$0"  # Clean up launcher script
    exit 0
fi

# User said yes - create signal file and launch game
touch "$SIGNAL_FILE"

# Game command
GAME_CMD="cd '$FLAPPY_CLAUDE_DIR' && uv run python -m flappy_claude; rm -f '$SIGNAL_FILE' '$FIRST_TOOL_FILE' '$TOOL_COUNT_FILE'; rmdir '$LOCK_DIR' 2>/dev/null"

# Launch in detected terminal
case "$TERM_PROG" in
    ghostty)
        ghostty -e bash -c "$GAME_CMD"
        ;;
    iTerm.app)
        osascript -e "tell application \"iTerm\" to create window with default profile command \"bash -c '$GAME_CMD'\""
        ;;
    kitty)
        kitty bash -c "$GAME_CMD"
        ;;
    alacritty)
        alacritty -e bash -c "$GAME_CMD"
        ;;
    WarpTerminal)
        osascript -e "tell application \"Warp\" to do script \"$GAME_CMD\""
        ;;
    *)
        osascript -e "tell application \"Terminal\" to do script \"$GAME_CMD\""
        ;;
esac

echo "$(date): Launched game in $TERM_PROG" >> "$LOG"
rm -f "$0"  # Clean up launcher script
LAUNCHER_EOF

chmod +x "$LAUNCHER"

# Run launcher completely detached using nohup + disown
nohup "$LAUNCHER" "$SIGNAL_FILE" "$LOCK_DIR" "$FIRST_TOOL_FILE" "$TOOL_COUNT_FILE" "$FLAPPY_CLAUDE_DIR" "$TERM_PROG" "$THRESHOLD_FILE" "$BACKOFF_MULTIPLIER" "$MAX_TOOL_THRESHOLD" > /dev/null 2>&1 &
disown

# Exit immediately - don't block Claude!
exit 0
