"""Tests for config module."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from socials_daily.config import get_api_key, load_config


class TestLoadConfig:
    """Tests for load_config()."""

    def test_returns_empty_dict_when_file_missing(self, tmp_path: Path) -> None:
        config_file = tmp_path / "missing.json"
        assert not config_file.exists()
        # Temporarily patch CONFIG_FILE
        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            assert load_config() == {}
        finally:
            config_module.CONFIG_FILE = original

    def test_returns_empty_dict_on_invalid_json(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json}", encoding="utf-8")

        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            assert load_config() == {}
        finally:
            config_module.CONFIG_FILE = original

    def test_returns_parsed_dict_on_valid_json(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_data = {"bluesky_token": "test-key", "instagram_api_key": "another-key"}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            result = load_config()
            assert result == config_data
        finally:
            config_module.CONFIG_FILE = original


class TestGetApiKey:
    """Tests for get_api_key()."""

    def test_returns_key_from_config_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"bluesky_token": "from-config"}),
            encoding="utf-8",
        )

        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            assert get_api_key("bluesky") == "from-config"
        finally:
            config_module.CONFIG_FILE = original

    def test_returns_key_from_env_var(self) -> None:
        with patch.dict(os.environ, {"HIKERAPI_TOKEN": "from-env"}):
            assert get_api_key("hikerapi") == "from-env"

    def test_returns_none_when_no_key(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text("{}", encoding="utf-8")

        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            with patch.dict(os.environ, {}, clear=True):
                assert get_api_key("unknown_service") is None
        finally:
            config_module.CONFIG_FILE = original

    def test_prefers_config_over_env(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"test_token": "from-config"}),
            encoding="utf-8",
        )

        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            with patch.dict(os.environ, {"TEST_TOKEN": "from-env"}):
                assert get_api_key("test") == "from-config"
        finally:
            config_module.CONFIG_FILE = original

    def test_handles_api_key_suffix(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"xpoz_api_key": "api-key-value"}),
            encoding="utf-8",
        )

        import socials_daily.config as config_module

        original = config_module.CONFIG_FILE
        try:
            config_module.CONFIG_FILE = config_file
            assert get_api_key("xpoz") == "api-key-value"
        finally:
            config_module.CONFIG_FILE = original
