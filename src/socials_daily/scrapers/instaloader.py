"""Instaloader scraper — free, rate-limited."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone

import instaloader
from instaloader import Instaloader, Profile

from ..errors import ScraperError
from .base import Post, Scraper

log = logging.getLogger(__name__)


class LenientRateController(instaloader.RateController):
    """A less aggressive rate controller."""

    def sleep_time_seconds(self, rtype: instaloader.RequestType) -> float:  # type: ignore[override]  # type: ignore[override]  # type: ignore[override]
        return 1.0

    def sleep(self, rtype: instaloader.RequestType) -> None:  # type: ignore[override]  # type: ignore[override]  # type: ignore[override]
        time.sleep(self.sleep_time_seconds(rtype))

    def check_request(self, rtype: instaloader.RequestType) -> None:
        pass


class InstaloaderScraper(Scraper):
    """Scraper using the free instaloader library."""

    name = "instaloader"

    def __init__(self) -> None:
        self._loader = Instaloader(
            sleep=False,
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            rate_controller=lambda ctx: LenientRateController(ctx),
        )

    def fetch_posts(
        self,
        username: str,
        limit: int = 10,
        since: datetime | None = None,
        till: datetime | None = None,
    ) -> list[Post]:
        """Fetch recent posts from a public account."""
        try:
            profile = Profile.from_username(self._loader.context, username)
        except Exception as exc:
            raise ScraperError(f"Failed to load profile: {exc}", "instaloader") from exc

        since = since or datetime.now(timezone.utc)
        till = till or datetime.now(timezone.utc)
        posts: list[Post] = []

        for post in profile.get_posts():
            if len(posts) >= limit:
                break
            if not (since.date() <= post.date_utc.date() <= till.date()):
                continue
            caption = (post.caption or "").strip()
            caption = re.sub(r"\s+", " ", caption)
            posts.append(
                Post(
                    caption=caption,
                    link=post.permalink,  # type: ignore[union-attr]  # type: ignore[union-attr]  # type: ignore[union-attr]
                    date=post.date_utc,
                )
            )
        return posts
