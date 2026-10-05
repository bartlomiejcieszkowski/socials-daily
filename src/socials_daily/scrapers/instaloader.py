"""Instaloader scraper — free, rate-limited."""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Optional

import instaloader
from instaloader import Instaloader, Profile

from .base import Post, Scraper


class LenientRateController(instaloader.RateController):
    """A less aggressive rate controller."""

    def sleep_time_seconds(self, rtype: instaloader.RequestType) -> float:
        return 1.0

    def sleep(self, rtype: instaloader.RequestType) -> None:
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

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a public account."""
        try:
            profile = Profile.from_username(self._loader.context, username)
        except Exception as exc:
            return []

        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []

        for post in profile.get_posts():
            if len(posts) >= limit:
                break
            if post.date_utc.date() != today:
                continue
            caption = (post.caption or "").strip()
            caption = re.sub(r"\s+", " ", caption)
            posts.append(
                Post(
                    caption=caption,
                    link=post.permalink,
                    date=post.date_utc,
                )
            )
        return posts
