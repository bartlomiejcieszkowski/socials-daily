"""Reddit scraper — uses Reddit's public JSON API."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

import httpx

from .base import Post, Scraper

log = logging.getLogger(__name__)


class RedditScraper(Scraper):
    """Scraper using Reddit's public JSON API (no auth required)."""

    name = "reddit"

    def __init__(self) -> None:
        self._client = httpx.Client(
            headers={
                "User-Agent": "socials-daily/0.1.0 (github.com/.../socials-daily)",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a Reddit subreddit."""
        url = f"https://www.reddit.com/r/{username}/new.json?limit=100"

        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                log.warning("Reddit rate limited for r/%s — will retry next run", username)
            elif exc.response.status_code == 404:
                log.warning("r/%s not found or is private", username)
            else:
                log.warning("Reddit API error for r/%s: %s", username, exc)
            return []
        except Exception as exc:
            log.warning("Failed to fetch r/%s: %s", username, exc)
            return []

        try:
            data = response.json()
        except Exception:
            log.warning("Failed to parse Reddit JSON for r/%s", username)
            return []

        children = data.get("data", {}).get("children", [])
        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []

        for child in children:
            if len(posts) >= limit:
                break

            d = child.get("data", {})
            created_utc = d.get("created_utc")
            if created_utc is None:
                continue

            try:
                post_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            except (ValueError, OSError, OverflowError):
                continue

            if post_date.date() != today:
                continue

            # Caption: selftext > title > empty
            caption = (d.get("selftext") or "").strip()
            if not caption:
                caption = (d.get("title") or "").strip()
            caption = re.sub(r"\s+", " ", caption)

            link = d.get("url", "")
            # Skip self-referential links (e.g. reddit.com/r/sub/comments/xxx/)
            if not link or "reddit.com" in link:
                link = ""

            posts.append(
                Post(
                    caption=caption,
                    link=link,
                    date=post_date,
                )
            )

        return posts
