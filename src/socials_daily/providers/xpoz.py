"""Xpoz provider — pre-indexed social data API."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from ..scrapers.base import Post, Scraper


class XpozProvider(Scraper):
    """Provider using Xpoz's pre-indexed social data API."""

    name = "xpoz"

    def __init__(self, api_key: Optional[str] = None) -> None:
        try:
            from xpoz import XpozClient  # noqa: PLC0415
        except ImportError:
            raise ImportError(
                "Xpoz SDK not installed. Run: uv add xpoz"
            )
        self._api_key = api_key or os.getenv("XPOZ_API_KEY")
        self._client = XpozClient(self._api_key)

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a public account."""
        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []

        try:
            results = self._client.instagram.get_posts_by_user(
                username,
                identifier_type="username",
                limit=limit,
                fields=["id", "caption", "timestamp", "permalink"],
            )

            for post in results.data:
                if len(posts) >= limit:
                    break
                ts = post.timestamp
                if ts:
                    try:
                        post_date = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
                    except (ValueError, AttributeError):
                        continue
                    if post_date != today:
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
        except Exception as exc:
            print(f"Xpoz error for @{username}: {exc}")

        return posts
