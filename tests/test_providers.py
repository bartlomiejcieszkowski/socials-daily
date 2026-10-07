"""Tests for provider factory."""

from __future__ import annotations

import pytest

from socials_daily.providers import _PROVIDER_BACKENDS, create_provider


class TestProviderBackends:
    """Tests for _PROVIDER_BACKENDS."""

    def test_contains_hikerapi(self) -> None:
        assert "hikerapi" in _PROVIDER_BACKENDS

    def test_contains_xpoz(self) -> None:
        assert "xpoz" in _PROVIDER_BACKENDS

    def test_excludes_non_providers(self) -> None:
        assert "bluesky" not in _PROVIDER_BACKENDS
        assert "instaloader" not in _PROVIDER_BACKENDS


class TestCreateProvider:
    """Tests for create_provider()."""

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("nonexistent")

    def test_returns_error_message_with_available(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider") as exc_info:
            create_provider("nonexistent")
        # Error message includes available providers list
        assert "Available:" in str(exc_info.value)
