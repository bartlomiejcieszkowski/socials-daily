"""Base scraper interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class Post:
    """A single Instagram post."""

    caption: str
    link: str
    date: datetime


class Scraper(Protocol):
    """Abstract scraper interface."""

    name: str

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a public account."""
        ...
