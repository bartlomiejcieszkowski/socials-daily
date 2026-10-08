"""Base scraper interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone


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
    def fetch_posts(
        self,
        username: str,
        limit: int = 10,
        since: datetime | None = None,
        till: datetime | None = None,
    ) -> list[Post]:
        """Fetch recent posts from a public account.

        Args:
            username: Account handle or username.
            limit: Maximum number of posts to fetch.
            since: Start date (inclusive). Defaults to today.
            till: End date (inclusive). Defaults to today.
        """
