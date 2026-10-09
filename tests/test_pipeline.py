"""Tests for pipeline runner."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from socials_daily.__main__ import DEFAULT_PIPELINES, load_pipelines, run_pipeline
from socials_daily.transformers.base import Post


class TestLoadPipelines:
    """Tests for pipeline config loading."""

    def test_missing_file_returns_default(self, tmp_path: Path) -> None:
        """Missing pipelines.json should return default config."""
        config = load_pipelines(tmp_path / "pipelines.json")
        assert config == DEFAULT_PIPELINES

    def test_invalid_json_returns_default(self, tmp_path: Path) -> None:
        """Invalid JSON should return default config."""
        (tmp_path / "pipelines.json").write_text("not json{{{", encoding="utf-8")
        config = load_pipelines(tmp_path / "pipelines.json")
        assert config == DEFAULT_PIPELINES

    def test_missing_pipelines_key_returns_default(self, tmp_path: Path) -> None:
        """Missing 'pipelines' key should return default config."""
        (tmp_path / "pipelines.json").write_text("{}", encoding="utf-8")
        config = load_pipelines(tmp_path / "pipelines.json")
        assert config == DEFAULT_PIPELINES

    def test_custom_pipeline_config(self, tmp_path: Path) -> None:
        """Custom pipeline config should be loaded correctly."""
        config_data = {
            "pipelines": {
                "default": {"transformers": ["filter_no_caption"], "output": ["markdown"]},
                "enriched": {"transformers": ["filter_no_caption", "add_tags"], "output": ["markdown", "json", "html"]},
            }
        }
        (tmp_path / "pipelines.json").write_text(json.dumps(config_data), encoding="utf-8")
        config = load_pipelines(tmp_path / "pipelines.json")
        assert config["pipelines"]["default"]["transformers"] == ["filter_no_caption"]
        assert config["pipelines"]["enriched"]["transformers"] == ["filter_no_caption", "add_tags"]


class TestRunPipeline:
    """Tests for pipeline execution."""

    def test_empty_pipeline_passes_through(self) -> None:
        """Empty transformer list should return posts unchanged."""
        posts = [Post(caption="test", link="http://example.com", date=datetime.now(timezone.utc))]
        result = run_pipeline(posts, "default")
        assert len(result) == 1
        assert result[0].caption == "test"

    def test_filter_no_caption_removes_empty(self, tmp_path: Path) -> None:
        """filter_no_caption should remove posts with empty captions."""
        posts = [
            Post(caption="has caption", link="http://example.com/1", date=datetime.now(timezone.utc)),
            Post(caption="", link="http://example.com/2", date=datetime.now(timezone.utc)),
            Post(caption="   ", link="http://example.com/3", date=datetime.now(timezone.utc)),
        ]
        config = {"pipelines": {"default": {"transformers": ["filter_no_caption"], "output": ["markdown"]}}}
        (tmp_path / "pipelines.json").write_text(json.dumps(config), encoding="utf-8")
        result = run_pipeline(posts, "default", config_path=tmp_path / "pipelines.json")
        assert len(result) == 1
        assert result[0].caption == "has caption"

    def test_filter_no_caption_keeps_all_valid(self, tmp_path: Path) -> None:
        """filter_no_caption should keep all posts with captions."""
        posts = [
            Post(caption="first", link="http://example.com/1", date=datetime.now(timezone.utc)),
            Post(caption="second", link="http://example.com/2", date=datetime.now(timezone.utc)),
        ]
        config = {"pipelines": {"default": {"transformers": ["filter_no_caption"], "output": ["markdown"]}}}
        (tmp_path / "pipelines.json").write_text(json.dumps(config), encoding="utf-8")
        result = run_pipeline(posts, "default", config_path=tmp_path / "pipelines.json")
        assert len(result) == 2
