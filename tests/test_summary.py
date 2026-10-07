"""Tests for summary generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from socials_daily.__main__ import generate_summary


class TestGenerateSummary:
    """Tests for generate_summary()."""

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        accounts: dict[str, dict] = {}
        output_dir = tmp_path / "output"
        assert not output_dir.exists()
        generate_summary(accounts, api_key=None, cli_backend=None, output_dir=output_dir)
        assert output_dir.exists()

    def test_creates_markdown_file(self, tmp_path: Path) -> None:
        accounts: dict[str, dict] = {}
        output_dir = tmp_path / "output"
        output_file = generate_summary(accounts, api_key=None, cli_backend=None, output_dir=output_dir)
        assert output_file.exists()
        assert output_file.name.startswith("daily-summary-")
        assert output_file.suffix == ".md"

    def test_creates_json_file(self, tmp_path: Path) -> None:
        accounts: dict[str, dict] = {}
        output_dir = tmp_path / "output"
        output_file = generate_summary(accounts, api_key=None, cli_backend=None, output_dir=output_dir)
        json_file = output_dir / f"daily-summary-{output_file.stem.replace('daily-summary-', '')}.json"
        assert json_file.exists()

    def test_no_posts_shows_message(self, tmp_path: Path) -> None:
        accounts: dict[str, dict] = {}
        output_dir = tmp_path / "output"
        output_file = generate_summary(accounts, api_key=None, cli_backend=None, output_dir=output_dir)
        content = output_file.read_text(encoding="utf-8")
        assert "No new posts today" in content

    def test_includes_date_in_filename(self, tmp_path: Path) -> None:
        accounts: dict[str, dict] = {}
        output_dir = tmp_path / "output"
        output_file = generate_summary(accounts, api_key=None, cli_backend=None, output_dir=output_dir)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        assert today in output_file.name

    def test_json_contains_empty_list(self, tmp_path: Path) -> None:
        accounts: dict[str, dict] = {}
        output_dir = tmp_path / "output"
        generate_summary(accounts, api_key=None, cli_backend=None, output_dir=output_dir)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        json_file = output_dir / f"daily-summary-{today}.json"
        content = json.loads(json_file.read_text(encoding="utf-8"))
        assert content == []
