"""Scraper backends."""

from __future__ import annotations

from typing import Optional

from .base import Post, Scraper
from .bluesky import BlueskyScraper
from .hikerapi import HikerAPIScraper
from .instaloader import InstaloaderScraper
from .xpoz import XpozScraper


def create_scraper(backend: str, api_key: Optional[str] = None) -> Scraper:
    """Create a scraper instance for the given backend.

    API key is resolved in order: explicit argument > config file > env var.
    """
    from ..config import get_api_key

    backends = {
        "bluesky": BlueskyScraper,
        "instaloader": InstaloaderScraper,
        "hikerapi": HikerAPIScraper,
        "xpoz": XpozScraper,
    }
    cls = backends.get(backend)
    if not cls:
        raise ValueError(f"Unknown backend: {backend}. Available: {list(backends.keys())}")

    # Resolve API key: explicit > config > env var
    key = api_key or get_api_key(backend)
    return cls(api_key=key) if key else cls()


__all__ = ["Post", "Scraper", "BlueskyScraper", "InstaloaderScraper", "HikerAPIScraper", "XpozScraper", "create_scraper"]
