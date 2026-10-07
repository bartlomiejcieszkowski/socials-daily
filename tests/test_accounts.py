"""Tests for account loading and saving."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from socials_daily.__main__ import add_account, load_accounts, save_accounts


class TestLoadAccounts:
    """Tests for load_accounts()."""

    def test_returns_empty_dict_when_file_missing(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        assert not accounts_file.exists()
        assert load_accounts(accounts_file) == {}

    def test_returns_empty_dict_on_invalid_json(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        accounts_file.write_text("{invalid}", encoding="utf-8")
        assert load_accounts(accounts_file) == {}

    def test_handles_legacy_flat_list_format(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        accounts_file.write_text(
            json.dumps(["bsky.app", "natgeo"]),
            encoding="utf-8",
        )
        result = load_accounts(accounts_file)
        assert "bluesky" in result
        assert len(result["bluesky"]["accounts"]) == 2
        assert result["bluesky"]["accounts"][0]["handle"] == "bsky.app"
        assert result["bluesky"]["accounts"][1]["handle"] == "natgeo"

    def test_handles_legacy_format_with_objects(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        accounts_file.write_text(
            json.dumps([
                {"handle": "bsky.app"},
                {"handle": "natgeo", "platform": "instagram", "limit": 20},
            ]),
            encoding="utf-8",
        )
        result = load_accounts(accounts_file)
        assert "bluesky" in result
        assert "instagram" in result
        assert result["instagram"]["accounts"][0]["handle"] == "natgeo"
        assert result["instagram"]["accounts"][0]["limit"] == 20

    def test_handles_platform_object_format(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        data = {
            "bluesky": {
                "accounts": [{"handle": "bsky.app"}, {"handle": "atmos.bsky.social", "limit": 20}],
            },
            "instagram": {
                "accounts": [{"handle": "natgeo"}],
            },
        }
        accounts_file.write_text(json.dumps(data), encoding="utf-8")
        result = load_accounts(accounts_file)
        assert result == data

    def test_handles_backend_config(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        data = {
            "instagram": {
                "backend": "hikerapi",
                "accounts": [{"handle": "natgeo"}],
            },
        }
        accounts_file.write_text(json.dumps(data), encoding="utf-8")
        result = load_accounts(accounts_file)
        assert result["instagram"]["backend"] == "hikerapi"
        assert len(result["instagram"]["accounts"]) == 1


class TestSaveAccounts:
    """Tests for save_accounts()."""

    def test_writes_valid_json(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        accounts = {
            "bluesky": {"accounts": [{"handle": "bsky.app"}]},
        }
        save_accounts(accounts, accounts_file)
        result = json.loads(accounts_file.read_text(encoding="utf-8"))
        assert result == accounts

    def test_trailing_newline(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        save_accounts({"bluesky": {"accounts": []}}, accounts_file)
        content = accounts_file.read_text(encoding="utf-8")
        assert content.endswith("\n")


class TestAddAccount:
    """Tests for add_account()."""

    def test_adds_new_account(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        add_account("bsky.app", "bluesky", accounts_file)
        result = load_accounts(accounts_file)
        assert "bluesky" in result
        assert result["bluesky"]["accounts"][0]["handle"] == "bsky.app"

    def test_strips_at_symbol(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        add_account("@bsky.app", "bluesky", accounts_file)
        result = load_accounts(accounts_file)
        assert result["bluesky"]["accounts"][0]["handle"] == "bsky.app"

    def test_skips_duplicate(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        add_account("bsky.app", "bluesky", accounts_file)
        add_account("bsky.app", "bluesky", accounts_file)
        result = load_accounts(accounts_file)
        assert len(result["bluesky"]["accounts"]) == 1

    def test_adds_with_limit(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        add_account("bsky.app", "bluesky", accounts_file, limit=20)
        result = load_accounts(accounts_file)
        assert result["bluesky"]["accounts"][0]["limit"] == 20

    def test_adds_with_backend(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        add_account("natgeo", "instagram", accounts_file, backend="hikerapi")
        result = load_accounts(accounts_file)
        assert result["instagram"]["backend"] == "hikerapi"

    def test_creates_new_platform(self, tmp_path: Path) -> None:
        accounts_file = tmp_path / "accounts.json"
        add_account("natgeo", "instagram", accounts_file)
        add_account("bsky.app", "bluesky", accounts_file)
        result = load_accounts(accounts_file)
        assert "instagram" in result
        assert "bluesky" in result
