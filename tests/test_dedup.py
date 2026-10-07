"""Tests for deduplication and seen file handling."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from socials_daily.__main__ import load_seen, save_seen
from socials_daily.scrapers.base import Post


class TestLoadSeen:
    """Tests for load_seen()."""

    def test_returns_empty_set_when_file_missing(self, tmp_path: Path) -> None:
        import socials_daily.__main__ as main_module

        original = main_module.SEEN_FILE
        try:
            main_module.SEEN_FILE = tmp_path / "missing.json"
            assert load_seen() == set()
        finally:
            main_module.SEEN_FILE = original

    def test_returns_empty_set_on_invalid_json(self, tmp_path: Path) -> None:
        import socials_daily.__main__ as main_module

        seen_file = tmp_path / "seen.json"
        seen_file.write_text("{invalid}", encoding="utf-8")
        original = main_module.SEEN_FILE
        try:
            main_module.SEEN_FILE = seen_file
            assert load_seen() == set()
        finally:
            main_module.SEEN_FILE = original

    def test_returns_set_of_links(self, tmp_path: Path) -> None:
        import socials_daily.__main__ as main_module

        seen_file = tmp_path / "seen.json"
        links = ["https://example.com/1", "https://example.com/2"]
        seen_file.write_text(json.dumps(links), encoding="utf-8")
        original = main_module.SEEN_FILE
        try:
            main_module.SEEN_FILE = seen_file
            result = load_seen()
            assert result == set(links)
        finally:
            main_module.SEEN_FILE = original


class TestSaveSeen:
    """Tests for save_seen()."""

    def test_writes_valid_json(self, tmp_path: Path) -> None:
        import socials_daily.__main__ as main_module

        seen_file = tmp_path / "seen.json"
        links = {"https://example.com/1", "https://example.com/2"}
        original = main_module.SEEN_FILE
        try:
            main_module.SEEN_FILE = seen_file
            save_seen(links)
            result = json.loads(seen_file.read_text(encoding="utf-8"))
            assert set(result) == links
        finally:
            main_module.SEEN_FILE = original

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        import socials_daily.__main__ as main_module

        seen_file = tmp_path / "seen.json"
        original = main_module.SEEN_FILE
        try:
            main_module.SEEN_FILE = seen_file
            save_seen({"https://old.com"})
            save_seen({"https://new.com"})
            result = json.loads(seen_file.read_text(encoding="utf-8"))
            assert result == ["https://new.com"]
        finally:
            main_module.SEEN_FILE = original


class TestDeduplication:
    """Tests for deduplication logic."""

    def test_duplicate_link_filtered(self) -> None:
        seen: set[str] = {"https://example.com/1"}
        post1 = Post(
            caption="Test post 1",
            link="https://example.com/1",
            date=datetime.now(timezone.utc),
        )
        post2 = Post(
            caption="Test post 2",
            link="https://example.com/2",
            date=datetime.now(timezone.utc),
        )
        posts = [post1, post2]
        new_posts = []
        for post in posts:
            if post.link not in seen:
                seen.add(post.link)
                new_posts.append(post)
        assert len(new_posts) == 1
        assert new_posts[0].link == "https://example.com/2"

    def test_all_new_posts_included(self) -> None:
        seen: set[str] = set()
        post1 = Post(
            caption="Test post 1",
            link="https://example.com/1",
            date=datetime.now(timezone.utc),
        )
        post2 = Post(
            caption="Test post 2",
            link="https://example.com/2",
            date=datetime.now(timezone.utc),
        )
        posts = [post1, post2]
        new_posts = []
        for post in posts:
            if post.link not in seen:
                seen.add(post.link)
                new_posts.append(post)
        assert len(new_posts) == 2
