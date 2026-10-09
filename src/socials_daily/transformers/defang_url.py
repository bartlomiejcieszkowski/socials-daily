"""Defang URL transformer — obfuscates URLs for safe display."""

from __future__ import annotations

from .base import Post, Transformer, transformer


@transformer("defang_url")
class DefangUrlTransformer(Transformer):
    """Defang URLs in captions for safe display.

    Converts URLs to non-clickable form:
    - `http://` → `hxxp://`
    - `https://` → `hxxps://`
    - `.` → `[.]`
    - `@` → `[@]`
    - `://` → `[://]`
    """

    name = "defang_url"

    def transform(self, posts: list[Post]) -> list[Post]:
        """Defang URLs in post captions."""
        for post in posts:
            if post.caption:
                post.caption = (
                    post.caption
                    .replace("https://", "hxxps://")
                    .replace("http://", "hxxp://")
                    .replace(".", "[.]")
                    .replace("@", "[@]")
                    .replace("://", "[://]")
                )
        return posts
