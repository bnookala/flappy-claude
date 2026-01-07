"""High score persistence."""

from pathlib import Path


def load_high_score(path: Path) -> int:
    """Load high score from file.

    Args:
        path: Path to the high score file

    Returns:
        The high score, or 0 if file doesn't exist or is invalid
    """
    try:
        if not path.exists():
            return 0

        content = path.read_text().strip()
        if not content:
            return 0

        return int(content)
    except (OSError, IOError, ValueError):
        return 0


def save_high_score(path: Path, score: int) -> None:
    """Save high score to file.

    Args:
        path: Path to the high score file
        score: The score to save
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(score))
    except (OSError, IOError):
        pass  # Ignore errors - high scores are not critical
