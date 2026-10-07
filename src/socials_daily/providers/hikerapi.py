"""HikerAPI provider — pay-per-request REST API."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone

import httpx

from ..errors import ProviderError
from ..scrapers.base import Post, Scraper

log = logging.getLogger(__name__)


class HikerAPIProvider(Scraper):
    """Provider using HikerAPI's REST API."""

    name = "hikerapi"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("HIKERAPI_TOKEN")
        if not self._api_key:
            log.warning("No HIKERAPI_TOKEN set — API calls will fail")
        self._client = httpx.Client(
            base_url="https://api.hikerapi.com",
            headers={
                "x-access-key": self._api_key or "",
                "accept": "application/json",
            },
            timeout=30.0,
        )

    def _get_user_id(self, username: str) -> str:
        """Resolve username to user ID."""
        try:
            resp = self._client.get("/v2/user/by/username", params={"username": username})
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise ProviderError(f"User {username} not found", "hikerapi") from exc
            if exc.response.status_code == 401:
                raise ProviderError("Invalid API key", "hikerapi") from exc
            raise ProviderError(f"API error: {exc}", "hikerapi") from exc

        try:
            data = resp.json()
            return data["user"]["pk"]
        except (KeyError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Unexpected response format: {exc}", "hikerapi") from exc

    def _fetch_medias_chunk(
        self, user_id: str, end_cursor: str | None = None
    ) -> tuple[list[dict], str | None]:
        """Fetch a chunk of user medias."""
        params: dict = {"user_id": user_id}
        if end_cursor:
            params["end_cursor"] = end_cursor
        try:
            resp = self._client.get("/v1/user/medias/chunk", params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"API error: {exc}", "hikerapi") from exc

        try:
            result = resp.json()
        except json.JSONDecodeError as exc:
            raise ProviderError(f"Invalid JSON response: {exc}", "hikerapi") from exc

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
                    try:
                        post_date = datetime.fromtimestamp(taken_at, tz=timezone.utc).date()
                    except (OSError, OverflowError, ValueError):
                        continue
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
                            date=(
                                datetime.fromtimestamp(taken_at, tz=timezone.utc)
                                if taken_at
                                else datetime.now(timezone.utc)
                            ),
                        )
                    )

            if not end_cursor:
                break

        return posts
