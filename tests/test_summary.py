"""Tests for summary generation (integration)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from socials_daily.__main__ import (
    fetch_posts,
    generate_summary,
    load_seen,
    process_pipeline,
    run_pipeline,
    save_seen,
)


class TestFetchPosts:
    """Tests for fetch_posts() — fetching and deduplication."""

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def test_empty_accounts_returns_empty(self) -> None:
        accounts: dict[str, dict] = {}
        seen: set[str] = set()
        new_posts, updated_seen, posts_per_account = fetch_posts(
            accounts, api_key=None, cli_backend=None,
            since=self._now(), till=self._now(), seen=seen,
        )
        assert new_posts == []
        assert posts_per_account == {}

    def test_deduplication(self, tmp_path: Path) -> None:
        """Posts already in seen set are not returned as new."""
        seen = {"https://example.com/1"}
        new_posts, updated_seen, _ = fetch_posts(
            {}, api_key=None, cli_backend=None,
            since=self._now(), till=self._now(), seen=seen,
        )
        assert new_posts == []
        assert "https://example.com/1" in updated_seen


class TestProcessPipeline:
    """Tests for process_pipeline()."""

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def test_empty_posts(self) -> None:
        result = process_pipeline([], "default")
        assert result == []

    def test_pipeline_runs(self, tmp_path: Path) -> None:
        """Pipeline runs and returns posts (passthrough)."""
        from socials_daily.transformers.base import Post

        posts = [Post(
            link="https://example.com/1",
            caption="Test post",
            date=self._now(),
            platform="bluesky",
            account="test.bsky.social",
            tags=[],
        )]
        result = process_pipeline(posts, "default")
        assert len(result) == 1

    def test_pipeline_with_filter(self, tmp_path: Path) -> None:
        """Pipeline with filter_no_caption removes empty captions."""
        from socials_daily.transformers.base import Post

        posts = [
            Post(
                link="https://example.com/1",
                caption="Has caption",
                date=self._now(),
                platform="bluesky",
                account="test.bsky.social",
                tags=[],
            ),
            Post(
                link="https://example.com/2",
                caption="",
                date=self._now(),
                platform="bluesky",
                account="test.bsky.social",
                tags=[],
            ),
        ]
        # Use a pipeline config that includes filter_no_caption
        config = {
            "pipelines": {
                "default": {"transformers": ["filter_no_caption"]}
            }
        }
        config_path = tmp_path / "pipelines.json"
        config_path.write_text(json.dumps(config))

        from socials_daily.transformers import load_all

        # Temporarily override the default config path
        result = run_pipeline(posts, "default", config_path)
        assert len(result) == 1
        assert result[0].caption == "Has caption"


class TestGenerateSummary:
    """Tests for generate_summary() — full orchestration."""

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def test_empty_accounts(self, tmp_path: Path) -> None:
        """Empty accounts list completes without error."""
        accounts: dict[str, dict] = {}
        generate_summary(
            accounts, api_key=None, cli_backend=None,
            since=self._now(), till=self._now(),
        )
        # No crash = pass

    def test_dedup_persists(self, tmp_path: Path) -> None:
        """Seen file is saved after fetch."""
        from socials_daily.__main__ import SEEN_FILE

        seen_path = tmp_path / SEEN_FILE.name
        # Monkey-patch the seen file path
        import socials_daily.__main__ as main_module

        original = main_module.SEEN_FILE
        main_module.SEEN_FILE = seen_path
        try:
            generate_summary(
                {}, api_key=None, cli_backend=None,
                since=self._now(), till=self._now(),
            )
            assert seen_path.exists()
        finally:
            main_module.SEEN_FILE = original
