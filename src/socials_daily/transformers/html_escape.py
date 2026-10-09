"""HTML escape transformer — escapes HTML entities in captions."""

from __future__ import annotations

from html import escape

from .base import Post, Transformer, transformer


@transformer("html_escape")
class HTMLEscapeTransformer(Transformer):
    """Escape HTML entities in post captions for safe rendering."""

    name = "html_escape"

    def transform(self, posts: list[Post]) -> list[Post]:
        """Escape HTML in captions."""
        for post in posts:
            post.caption = escape(post.caption, quote=True)
        return posts
