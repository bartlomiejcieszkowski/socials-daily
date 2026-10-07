"""Scraper backends."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Post, Scraper
from .bluesky import BlueskyScraper
from .instaloader import InstaloaderScraper
from .reddit import RedditScraper
from .rss import RSSScraper
from .youtube import YouTubeScraper

if TYPE_CHECKING:
    pass  # hikerapi and xpoz imported lazily

# Map platform names (user-facing) to scraper names (internal)
PLATFORM_MAP = {
    "instagram": "instaloader",
    "bluesky": "bluesky",
    "reddit": "reddit",
    "rss": "rss",
    "youtube": "youtube",
    "hikerapi": "hikerapi",
    "xpoz": "xpoz",
}

# Known optional backends that may not be installed
_OPTIONAL_BACKENDS = {"hikerapi", "xpoz"}


def create_scraper(platform: str, api_key: str | None = None, backend: str | None = None) -> Scraper:
    """Create a scraper instance for the given platform.

    Backend resolution (highest to lowest priority):
    1. Explicit ``backend`` argument (CLI override)
    2. ``backend`` from platform config in accounts.json
    3. Default mapping: platform name → scraper name (e.g. ``instagram`` → ``instaloader``)

    API key is resolved in order: explicit argument > config file > env var.
    """
    from ..config import get_api_key

    # Resolve platform name to scraper name
    if backend:
        scraper_name = backend
    else:
        scraper_name = PLATFORM_MAP.get(platform, platform)

    backends: dict[str, type[Scraper]] = {
        "bluesky": BlueskyScraper,
        "instaloader": InstaloaderScraper,
        "reddit": RedditScraper,
        "rss": RSSScraper,
        "youtube": YouTubeScraper,
    }

    # Lazy-load optional backends so the package imports without them
    if scraper_name in _OPTIONAL_BACKENDS:
        if scraper_name == "hikerapi":
            from .hikerapi import HikerAPIScraper  # noqa: PLC0415

            backends["hikerapi"] = HikerAPIScraper
        elif scraper_name == "xpoz":
            from .xpoz import XpozScraper  # noqa: PLC0415

            backends["xpoz"] = XpozScraper

    cls = backends.get(scraper_name)
    if not cls:
        raise ValueError(f"Unknown backend: {scraper_name}. Available: {list(backends.keys())}")

    # Resolve API key: explicit > config > env var
    key = api_key or get_api_key(scraper_name)
    return cls(api_key=key) if key else cls()


__all__ = ["Post", "Scraper", "BlueskyScraper", "InstaloaderScraper", "RedditScraper", "RSSScraper", "YouTubeScraper", "create_scraper"]
