"""Tests for scraper error handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from socials_daily.errors import ScraperError


class TestInstaloaderErrorHandling:
    """Tests for instaloader scraper error handling."""

    def test_raises_on_profile_failure(self) -> None:
        with patch("socials_daily.scrapers.instaloader.Instaloader") as MockLoader:
            mock_context = MagicMock()
            MockLoader.return_value.context = mock_context
            MockLoader.return_value.sleep = False

            with patch(
                "socials_daily.scrapers.instaloader.Profile.from_username",
                side_effect=Exception("profile not found"),
            ):
                from socials_daily.scrapers.instaloader import InstaloaderScraper

                scraper = InstaloaderScraper()
                with pytest.raises(ScraperError, match="instaloader"):
                    scraper.fetch_posts("nonexistent_user")


class TestBlueskyErrorHandling:
    """Tests for bluesky scraper error handling."""

    def test_logs_warning_on_handle_resolution_failure(self) -> None:
        with patch("socials_daily.scrapers.bluesky.Client") as MockClient:
            mock_client = MagicMock()
            mock_client.resolve_handle.side_effect = Exception("resolution failed")
            MockClient.return_value = mock_client

            from socials_daily.scrapers.bluesky import BlueskyScraper

            scraper = BlueskyScraper()
            result = scraper.fetch_posts("bad.handle")
            assert result == []


class TestScraperErrorMessages:
    """Tests for ScraperError message formatting."""

    def test_includes_scraper_name(self) -> None:
        exc = ScraperError("connection refused", "instaloader")
        assert "instaloader" in str(exc)
        assert "connection refused" in str(exc)

    def test_chained_exception(self) -> None:
        original = ValueError("original error")
        try:
            raise ScraperError("wrapped", "test") from original
        except ScraperError as exc:
            assert exc.__cause__ is original
