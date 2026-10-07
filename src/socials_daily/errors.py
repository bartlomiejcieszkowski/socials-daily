"""Custom exception types for socials-daily."""

from __future__ import annotations


class SocialsDailyError(Exception):
    """Base exception for all socials-daily errors."""


class ScraperError(SocialsDailyError):
    """Raised when a scraper encounters an unexpected error."""

    def __init__(self, message: str, scraper: str = "") -> None:
        full = f"{scraper}: {message}" if scraper else message
        super().__init__(full)


class ConfigError(SocialsDailyError):
    """Raised when there is a problem with the configuration."""


class AccountError(SocialsDailyError):
    """Raised when there is a problem with an account."""


class ProviderError(SocialsDailyError):
    """Raised when a provider fails."""

    def __init__(self, message: str, provider: str = "") -> None:
        full = f"{provider}: {message}" if provider else message
        super().__init__(full)
