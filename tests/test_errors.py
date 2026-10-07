"""Tests for custom exception types."""

from __future__ import annotations

import pytest

from socials_daily.errors import (
    AccountError,
    ConfigError,
    ProviderError,
    ScraperError,
    SocialsDailyError,
)


class TestSocialsDailyError:
    """Tests for the base exception."""

    def test_base_exception_is_raised(self) -> None:
        with pytest.raises(SocialsDailyError):
            raise SocialsDailyError("test error")

    def test_message_preserved(self) -> None:
        exc = SocialsDailyError("my message")
        assert str(exc) == "my message"


class TestScraperError:
    """Tests for ScraperError."""

    def test_error_without_scraper(self) -> None:
        exc = ScraperError("network failure")
        assert str(exc) == "network failure"

    def test_error_with_scraper(self) -> None:
        exc = ScraperError("network failure", "bluesky")
        assert str(exc) == "bluesky: network failure"

    def test_is_subclass_of_socials_daily_error(self) -> None:
        exc = ScraperError("test")
        assert isinstance(exc, SocialsDailyError)


class TestProviderError:
    """Tests for ProviderError."""

    def test_error_without_provider(self) -> None:
        exc = ProviderError("API timeout")
        assert str(exc) == "API timeout"

    def test_error_with_provider(self) -> None:
        exc = ProviderError("API timeout", "hikerapi")
        assert str(exc) == "hikerapi: API timeout"

    def test_is_subclass_of_socials_daily_error(self) -> None:
        exc = ProviderError("test")
        assert isinstance(exc, SocialsDailyError)


class TestConfigError:
    """Tests for ConfigError."""

    def test_error_message(self) -> None:
        exc = ConfigError("invalid JSON")
        assert str(exc) == "invalid JSON"

    def test_is_subclass_of_socials_daily_error(self) -> None:
        exc = ConfigError("test")
        assert isinstance(exc, SocialsDailyError)


class TestAccountError:
    """Tests for AccountError."""

    def test_error_message(self) -> None:
        exc = AccountError("handle not found")
        assert str(exc) == "handle not found"

    def test_is_subclass_of_socials_daily_error(self) -> None:
        exc = AccountError("test")
        assert isinstance(exc, SocialsDailyError)
