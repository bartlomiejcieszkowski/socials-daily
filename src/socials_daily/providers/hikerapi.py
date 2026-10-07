"""HikerAPI provider — pay-per-request REST API."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone

import httpx

from ..scrapers.base import Post, Scraper


class HikerAPIProvider(Scraper):
    """Provider using HikerAPI's REST API."""

    name = "hikerapi"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("HIKERAPI_TOKEN")
        self._client = httpx.Client(
            base_url="https://api.hikerapi.com",
            headers={"x-access-key": self._api_key or "", "accept": "application/json"},
            timeout=30.0,
        )

    def _get_user_id(self, username: str) -> str:
        """Resolve username to user ID."""
        resp = self._client.get("/v2/user/by/username", params={"username": username})
        resp.raise_for_status()
        data = resp.json()
        return data["user"]["pk"]

    def _fetch_medias_chunk(self, user_id: str, end_cursor: str | None = None) -> tuple[list[dict], str | None]:
        """Fetch a chunk of user medias."""
        params: dict = {"user_id": user_id}
        if end_cursor:
            params["end_cursor"] = end_cursor
        resp = self._client.get("/v1/user/medias/chunk", params=params)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and len(result) == 2:
            items, cursor = result
        else:
            items = result
            cursor = None
        return items, cursor

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a public account."""
        user_id = self._get_user_id(username)
        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []
        end_cursor: str | None = None

        while len(posts) < limit:
            items, end_cursor = self._fetch_medias_chunk(user_id, end_cursor)
            if not items:
                break

            for item in items:
                if len(posts) >= limit:
                    break
                taken_at = item.get("taken_at")
                if taken_at:
                    post_date = datetime.fromtimestamp(taken_at, tz=timezone.utc).date()
                    if post_date != today:
                        continue
                caption = (item.get("caption_text") or "").strip()
                caption = re.sub(r"\s+", " ", caption)
                shortcode = item.get("code")
                if shortcode:
                    link = f"https://www.instagram.com/p/{shortcode}/"
                    posts.append(
                        Post(
                            caption=caption,
                            link=link,
                            date=datetime.fromtimestamp(taken_at, tz=timezone.utc)
                            if taken_at
                            else datetime.now(timezone.utc),
                        )
                    )

            if not end_cursor:
                break

        return posts
