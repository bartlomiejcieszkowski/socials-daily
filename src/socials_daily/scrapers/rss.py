"""RSS/Atom feed scraper — uses feedparser library."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

import feedparser

from .base import Post, Scraper

log = logging.getLogger(__name__)


class RSSScraper(Scraper):
    """Scraper for RSS/Atom feeds via feedparser."""

    name = "rss"

    def __init__(self) -> None:
        pass

    def _parse_date(self, entry: feedparser.FeedParserDict) -> datetime | None:
        """Extract a datetime from an RSS/Atom entry, trying multiple fields."""
        for field in ("published_parsed", "updated_parsed", "updated", "published"):
            parsed = entry.get(field)
            if parsed and isinstance(parsed, tuple) and len(parsed) >= 6:
                try:
                    return datetime(*parsed[:6], tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue
        # Fallback: try raw string
        raw = entry.get("published") or entry.get("updated")
        if raw:
            try:
                raw_str = str(raw).strip()
                dt = datetime.fromisoformat(raw_str.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                pass
        return None

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from an RSS/Atom feed."""
        try:
            feed = feedparser.parse(username)
        except Exception as exc:
            log.warning("Failed to parse RSS feed %s: %s", username, exc)
            return []

        if feed.bozo and not feed.entries:
            log.warning("RSS feed %s returned errors: %s", username, feed.bozo_exception)
            return []

        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []

        for entry in feed.entries:
            if len(posts) >= limit:
                break

            post_date = self._parse_date(entry)
            if post_date is None:
                continue

            if post_date.date() != today:
                continue

            # Caption: summary > content (first item) > title
            caption = (entry.get("summary") or "").strip()
            if not caption:
                content = entry.get("content")
                if content:
                    if hasattr(content, "text"):
                        caption = content.text.strip()
                    else:
                        caption = (str(content) or "").strip()
            if not caption:
                caption = (entry.get("title") or "").strip()

            # Strip HTML tags from caption
            caption = re.sub(r"<[^>]+>", "", caption)
            caption = re.sub(r"\s+", " ", caption).strip()

            link = (entry.get("link") or "").strip()
            if not link:
                # Try alternate links
                alternates = entry.get("alternate_links") or entry.get("links", [])
                if alternates:
                    alt = alternates[0] if isinstance(alternates, list) else alternates
                    link = alt.get("href", "") if isinstance(alt, dict) else str(alt)

            posts.append(
                Post(
                    caption=caption,
                    link=link,
                    date=post_date,
                )
            )

        return posts
