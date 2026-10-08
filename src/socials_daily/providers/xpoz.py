"""Xpoz provider — pre-indexed social data API."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from ..errors import ProviderError
from ..scrapers.base import Post, Scraper

log = logging.getLogger(__name__)


class XpozProvider(Scraper):
    """Provider using Xpoz's pre-indexed social data API."""

    name = "xpoz"

    def __init__(self, api_key: str | None = None) -> None:
        try:
            from xpoz import XpozClient  # noqa: PLC0415
        except ImportError:
            raise ImportError("Xpoz SDK not installed. Run: uv add xpoz")

        self._api_key = api_key or os.getenv("XPOZ_API_KEY")
        if not self._api_key:
            log.warning("No XPOZ_API_KEY set — API calls will likely fail")
        self._client = XpozClient(self._api_key)

    def fetch_posts(
        self,
        username: str,
        limit: int = 10,
        since: datetime | None = None,
        till: datetime | None = None,
    ) -> list[Post]:
        """Fetch recent posts from a public account."""
        since = since or datetime.now(timezone.utc)
        till = till or datetime.now(timezone.utc)
        posts: list[Post] = []

        try:
            results = self._client.instagram.get_posts_by_user(
                username,
                identifier_type="username",
                limit=limit,
                fields=["id", "caption", "timestamp", "permalink"],
            )
        except Exception as exc:
            raise ProviderError(f"Xpoz API error: {exc}", "xpoz") from exc

        for post in results.data:
            if len(posts) >= limit:
                break
            ts = post.timestamp
            if ts:
                try:
                    post_date = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue
                if not (since.date() <= post_date.date() <= till.date()):
                    continue

            caption = (post.caption or "").strip()
            link = post.permalink or f"https://www.instagram.com/p/{post.id.split('_')[0]}/"
            date = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else datetime.now(timezone.utc)

            posts.append(
                Post(
                    caption=caption,
                    link=link,
                    date=date,
                )
            )

        return posts
