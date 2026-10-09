"""Tests for transformer loader."""

from __future__ import annotations

from datetime import datetime, timezone

from socials_daily.transformers import list_transformers, get_transformer
from socials_daily.transformers.base import Post


class TestTransformerDiscovery:
    """Tests for transformer discovery."""

    def test_discovers_filter_no_caption(self) -> None:
        """Auto-discovered local transformers should be available."""
        names = list_transformers()
        assert "filter_no_caption" in names

    def test_get_transformer_returns_class(self) -> None:
        """get_transformer should return the transformer class."""
        cls = get_transformer("filter_no_caption")
        assert cls is not None
        assert cls.name == "filter_no_caption"

    def test_get_transformer_returns_none_for_unknown(self) -> None:
        """get_transformer should return None for unknown names."""
        assert get_transformer("nonexistent_transformer") is None

    def test_list_transformers_returns_sorted(self) -> None:
        """list_transformers should return sorted names."""
        names = list_transformers()
        assert names == sorted(names)

    def test_discovers_html_escape(self) -> None:
        """Auto-discovered local transformers should include html_escape."""
        names = list_transformers()
        assert "html_escape" in names

    def test_html_escape_transforms(self) -> None:
        """html_escape should escape HTML entities in captions."""
        cls = get_transformer("html_escape")
        assert cls is not None
        transformer = cls()
        posts = [
            Post(caption="Hello <b>world</b>", link="http://example.com/1", date=datetime.now(timezone.utc)),
            Post(caption="Safe caption", link="http://example.com/2", date=datetime.now(timezone.utc)),
            Post(caption="Quotes &amp; stuff", link="http://example.com/3", date=datetime.now(timezone.utc)),
        ]
        result = transformer.transform(posts)
        assert result[0].caption == "Hello &lt;b&gt;world&lt;/b&gt;"
        assert result[1].caption == "Safe caption"
        assert result[2].caption == "Quotes &amp;amp; stuff"
