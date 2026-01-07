#!/bin/bash
# PreToolUse hook - prompts user to play Flappy Claude during wait
# IMPORTANT: This hook exits immediately so Claude isn't blocked.
# All user interaction happens in a background process.

# Configuration
TURNS_BETWEEN_PROMPTS=10    # Only prompt once every N conversation turns
MIN_TOOL_CALLS=5            # Minimum tool calls in a turn before prompting

# File paths
SIGNAL_FILE="/tmp/flappy-claude-signal"
LOCK_DIR="/tmp/flappy-claude-lock"
TOOL_COUNT_FILE="/tmp/flappy-claude-tool-count"
TURN_COUNT_FILE="/tmp/flappy-claude-turns"      # Tracks conversation turns
LAST_PROMPT_TURN_FILE="/tmp/flappy-claude-last-prompt-turn"  # Turn when last prompted
FLAPPY_CLAUDE_DIR="${FLAPPY_CLAUDE_DIR:-$HOME/code/flappy-claude}"
TERM_PROG="$TERM_PROGRAM"  # Capture before backgrounding

# Consume stdin immediately so we don't block
cat > /dev/null &

# Check if game/prompt is already running
if [ -d "$LOCK_DIR" ]; then
    exit 0
fi

# Check if terminal is in foreground (only prompt if user is actively watching)
FRONTMOST=$(osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' 2>/dev/null)
case "$FRONTMOST" in
    ghostty|Ghostty|iTerm*|Terminal|kitty|Kitty|Alacritty|alacritty|Warp)
        # Terminal is focused, continue
        ;;
    *)
        # Terminal not focused, don't bother user
        exit 0
        ;;
esac

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

# Check if we have enough tool calls this turn
if [ "$COUNT" -lt "$MIN_TOOL_CALLS" ]; then
    exit 0
fi

# Check turn-based limiting
CURRENT_TURN=$(cat "$TURN_COUNT_FILE" 2>/dev/null || echo "0")
LAST_PROMPT_TURN=$(cat "$LAST_PROMPT_TURN_FILE" 2>/dev/null || echo "-999")
TURNS_SINCE_PROMPT=$((CURRENT_TURN - LAST_PROMPT_TURN))

if [ "$TURNS_SINCE_PROMPT" -lt "$TURNS_BETWEEN_PROMPTS" ]; then
    exit 0
fi

# Atomic lock to prevent multiple prompts
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    exit 0
fi

# Record that we're prompting on this turn
echo "$CURRENT_TURN" > "$LAST_PROMPT_TURN_FILE"

# Create a detached launcher script and run it completely independently
LAUNCHER="/tmp/flappy-claude-launcher-$$.sh"
cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/bin/bash
SIGNAL_FILE="$1"
LOCK_DIR="$2"
TOOL_COUNT_FILE="$3"
FLAPPY_CLAUDE_DIR="$4"
TERM_PROG="$5"
LOG="/tmp/flappy-claude-hook.log"

echo "$(date): Showing dialog (detached)" >> "$LOG"

# Ask user with a macOS dialog
RESPONSE=$(osascript -e 'display dialog "Play Flappy Claude while Claude works?" buttons {"No", "Yes"} default button "Yes" giving up after 15' 2>/dev/null)

if [[ "$RESPONSE" != *"Yes"* ]]; then
    rmdir "$LOCK_DIR" 2>/dev/null
    echo "$(date): User declined or timeout" >> "$LOG"
    rm -f "$0"  # Clean up launcher script
    exit 0
fi

# User said yes - create signal file and launch game
touch "$SIGNAL_FILE"

# Game command
GAME_CMD="cd '$FLAPPY_CLAUDE_DIR' && uv run python -m flappy_claude; rm -f '$SIGNAL_FILE'; rmdir '$LOCK_DIR' 2>/dev/null"

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
nohup "$LAUNCHER" "$SIGNAL_FILE" "$LOCK_DIR" "$TOOL_COUNT_FILE" "$FLAPPY_CLAUDE_DIR" "$TERM_PROG" > /dev/null 2>&1 &
disown

# Exit immediately - don't block Claude!
exit 0
