"""YouTube scraper — uses yt-dlp library for metadata extraction."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .base import Post, Scraper

if TYPE_CHECKING:
    pass  # yt_dlp imported lazily to avoid hard dependency

log = logging.getLogger(__name__)


class YouTubeScraper(Scraper):
    """Scraper using yt-dlp to extract video metadata from YouTube channels."""

    name = "youtube"

    def __init__(self) -> None:
        self._import_error: Exception | None = None
        try:
            import yt_dlp  # noqa: PLC0415

            del yt_dlp  # only checking availability
        except ImportError as exc:
            self._import_error = exc

    def _ensure_import(self) -> None:
        if self._import_error:
            raise RuntimeError(
                "yt-dlp is not installed. Install it with: uv sync -E youtube"
            ) from self._import_error

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent videos from a YouTube channel.

        Args:
            username: YouTube channel handle (e.g. @mkbhd) or channel name.
            limit: Maximum number of videos to fetch.
        """
        self._ensure_import()

        import yt_dlp  # noqa: PLC0415

        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []

        url = f"https://www.youtube.com/@{username.lstrip('@')}/videos"

        ydl_opts: dict = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'playlistend': limit,
            'dateafter': today.isoformat(),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                info = ydl.extract_info(url, download=False)

                if not info:
                    log.warning("No channel info found for %s", username)
                    return []

                entries = info.get('entries') or []
                if not entries:
                    log.warning("No videos found for channel %s", username)
                    return []

                for entry in entries:
                    if len(posts) >= limit:
                        break

                    if not entry:
                        continue

                    upload_date_raw = entry.get('upload_date') or entry.get('timestamp')
                    if not upload_date_raw:
                        continue

                    upload_date = str(upload_date_raw)
                    try:
                        if len(upload_date) == 8:
                            post_date = datetime.strptime(
                                upload_date, "%Y%m%d"
                            ).replace(tzinfo=timezone.utc)
                        else:
                            post_date = datetime.fromtimestamp(
                                int(upload_date_raw), tz=timezone.utc
                            )
                    except (ValueError, TypeError, OSError):
                        continue

                    if post_date.date() != today:
                        continue

                    title = (entry.get('title') or '').strip()
                    description = (entry.get('description') or '').strip()
                    caption = description if description else title
                    caption = re.sub(r'\s+', ' ', caption)

                    link = (entry.get('webpage_url') or entry.get('url') or '').strip()

                    posts.append(
                        Post(
                            caption=caption,
                            link=link,
                            date=post_date,
                        )
                    )

        except Exception as exc:
            log.warning("Failed to extract from YouTube channel %s: %s", username, exc)

        return posts
