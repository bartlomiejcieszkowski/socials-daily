"""Tests for transformer loader."""

from __future__ import annotations

from socials_daily.transformers import list_transformers, get_transformer


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
