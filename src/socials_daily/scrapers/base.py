"""Base scraper interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Post:
    """A single social media post."""

    caption: str
    link: str
    date: datetime


class Scraper(ABC):
    """Abstract scraper interface."""

    name: str

    @abstractmethod
    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a public account."""
