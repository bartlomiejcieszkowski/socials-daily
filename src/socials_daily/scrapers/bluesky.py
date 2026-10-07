"""Bluesky scraper — uses atproto library with public list_records endpoint."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from atproto import Client
from atproto_client.models.com.atproto.repo.list_records import Params

from .base import Post, Scraper


class BlueskyScraper(Scraper):
    """Scraper using Bluesky's AT Protocol public endpoints."""

    name = "bluesky"

    def __init__(self) -> None:
        self._client = Client()

    def _resolve_handle(self, handle: str) -> str | None:
        """Resolve handle to DID."""
        try:
            result = self._client.resolve_handle(handle)
            return result.did
        except Exception:
            return None

    def _process_facets(self, text: str, facets: list) -> str:
        """Replace facet mentions with handles. Works on a copy of the text."""
        if not facets:
            return text

        # Collect all replacements sorted by byte position (reverse to preserve indices)
        replacements: list[tuple[int, int, str]] = []
        for facet in facets:
            if not hasattr(facet, "features") or not facet.features:
                continue
            for feature in facet.features:
                if hasattr(feature, "did") and feature.did:
                    start = facet.index.byte_start
                    end = facet.index.byte_end
                    replacements.append((start, end, feature.did))

        # Sort by start position in reverse so replacements don't shift indices
        replacements.sort(key=lambda x: x[0], reverse=True)
        for start, end, did in replacements:
            text = text[:start] + f"@{did}" + text[end:]

        return text

    def fetch_posts(self, handle: str, limit: int = 10) -> list[Post]:
        """Fetch recent posts from a Bluesky account."""
        did = self._resolve_handle(handle)
        if not did:
            return []

        today = datetime.now(timezone.utc).date()
        posts: list[Post] = []
        cursor: str | None = None
        max_pages = 20  # Safety limit to avoid infinite pagination
        consecutive_old = 0  # Stop if we see too many old posts in a row

        while len(posts) < limit and max_pages > 0:
            max_pages -= 1
            params = Params(
                repo=did,
                collection="app.bsky.feed.post",
                cursor=cursor,
                limit=25,  # max per page for efficiency
                reverse=True,  # newest first
            )
            try:
                result = self._client.com.atproto.repo.list_records(params=params)
            except Exception:
                break

            if not result.records:
                break

            has_today_post = False
            for record in result.records:
                if len(posts) >= limit:
                    break

                value = record.value
                if not hasattr(value, "created_at") or not hasattr(value, "text"):
                    continue

                created_at = value.created_at
                try:
                    post_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
                except (ValueError, AttributeError):
                    continue

                if post_date != today:
                    consecutive_old += 1
                    # If we've seen enough old posts, stop paginating
                    if consecutive_old > 50:
                        break
                    continue

                has_today_post = True
                consecutive_old = 0  # Reset counter when we find today's post

                text = (value.text or "").strip()
                text = re.sub(r"\s+", " ", text)

                # Process facets (mentions, links, etc.)
                if hasattr(value, "facets") and value.facets:
                    text = self._process_facets(text, value.facets)

                link = f"https://bsky.app/profile/{did}/post/{record.uri.split('/')[-1]}"
                posts.append(
                    Post(
                        caption=text,
                        link=link,
                        date=datetime.fromisoformat(created_at.replace("Z", "+00:00")),
                    )
                )

            if not has_today_post and consecutive_old > 50:
                break

            cursor = result.cursor if hasattr(result, "cursor") and result.cursor else None
            if not cursor:
                break

        return posts
