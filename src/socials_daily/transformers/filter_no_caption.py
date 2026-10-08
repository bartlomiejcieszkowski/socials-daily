"""Filter transformer — removes posts with empty captions."""

from __future__ import annotations

from .base import Post, Transformer, transformer


@transformer("filter_no_caption")
class FilterNoCaptionTransformer(Transformer):
    """Remove posts that have no caption text."""

    name = "filter_no_caption"

    def transform(self, posts: list[Post]) -> list[Post]:
        """Filter out posts with empty or whitespace-only captions."""
        return [p for p in posts if p.caption and p.caption.strip()]
