"""Base transformer interface and decorator."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass
class Post:
    """A single social media post with optional metadata."""

    caption: str
    link: str
    date: datetime
    platform: str = ""
    account: str = ""
    tags: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []


@runtime_checkable
class Transformer(Protocol):
    """A post-processing transformer.

    Receives a list of posts and returns a (possibly modified) list.
    Transformers can filter, enrich, or format posts.
    """

    name: str

    def transform(self, posts: list[Post]) -> list[Post]:
        """Transform the given posts.

        Args:
            posts: Input posts to transform.

        Returns:
            Transformed posts (may be fewer if filtering, or enriched).
        """


def transformer(name: str) -> type[Transformer]:
    """Decorator to register a transformer class.

    Usage:
        @transformer("my_transformer")
        class MyTransformer:
            name = "my_transformer"
            def transform(self, posts): ...
    """

    def decorator(cls: type[Transformer]) -> type[Transformer]:
        cls.name = name  # type: ignore[attr-defined]
        return cls

    return decorator
