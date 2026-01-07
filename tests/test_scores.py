"""Tests for high score loading and saving."""

import pytest
from pathlib import Path

from flappy_claude.scores import load_high_score, save_high_score


class TestLoadHighScore:
    """Tests for load_high_score function."""

    def test_returns_zero_when_file_missing(self, tmp_path: Path) -> None:
        """load_high_score returns 0 when file doesn't exist."""
        score_file = tmp_path / "nonexistent" / "highscore"

        result = load_high_score(score_file)

        assert result == 0

    def test_returns_score_when_file_exists(self, tmp_path: Path) -> None:
        """load_high_score returns the score from file."""
        score_file = tmp_path / "highscore"
        score_file.write_text("42")

        result = load_high_score(score_file)

        assert result == 42

    def test_returns_zero_for_invalid_content(self, tmp_path: Path) -> None:
        """load_high_score returns 0 when file contains invalid data."""
        score_file = tmp_path / "highscore"
        score_file.write_text("not a number")

        result = load_high_score(score_file)

        assert result == 0

    def test_returns_zero_for_empty_file(self, tmp_path: Path) -> None:
        """load_high_score returns 0 when file is empty."""
        score_file = tmp_path / "highscore"
        score_file.write_text("")

        result = load_high_score(score_file)

        assert result == 0

    def test_handles_whitespace_around_score(self, tmp_path: Path) -> None:
        """load_high_score handles whitespace around the score."""
        score_file = tmp_path / "highscore"
        score_file.write_text("  123  \n")

        result = load_high_score(score_file)

        assert result == 123


class TestSaveHighScore:
    """Tests for save_high_score function."""

    def test_creates_directory_and_writes_score(self, tmp_path: Path) -> None:
        """save_high_score creates parent directory and writes score."""
        score_file = tmp_path / "subdir" / "highscore"

        save_high_score(score_file, 99)

        assert score_file.exists()
        assert score_file.read_text() == "99"

    def test_overwrites_existing_score(self, tmp_path: Path) -> None:
        """save_high_score overwrites existing score file."""
        score_file = tmp_path / "highscore"
        score_file.write_text("50")

        save_high_score(score_file, 100)

        assert score_file.read_text() == "100"

    def test_writes_zero_score(self, tmp_path: Path) -> None:
        """save_high_score can write a zero score."""
        score_file = tmp_path / "highscore"

        save_high_score(score_file, 0)

        assert score_file.read_text() == "0"
