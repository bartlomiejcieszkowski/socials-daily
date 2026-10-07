"""Tests for scraper factory and platform mapping."""

from __future__ import annotations

import pytest

from socials_daily.scrapers import (
    PLATFORM_MAP,
    BlueskyScraper,
    InstaloaderScraper,
    RedditScraper,
    RSSScraper,
    YouTubeScraper,
    create_scraper,
)


class TestPlatformMap:
    """Tests for PLATFORM_MAP."""

    def test_instagram_maps_to_instaloader(self) -> None:
        assert PLATFORM_MAP["instagram"] == "instaloader"

    def test_bluesky_maps_to_bluesky(self) -> None:
        assert PLATFORM_MAP["bluesky"] == "bluesky"

    def test_reddit_maps_to_reddit(self) -> None:
        assert PLATFORM_MAP["reddit"] == "reddit"

    def test_rss_maps_to_rss(self) -> None:
        assert PLATFORM_MAP["rss"] == "rss"

    def test_youtube_maps_to_youtube(self) -> None:
        assert PLATFORM_MAP["youtube"] == "youtube"


class TestCreateScraper:
    """Tests for create_scraper()."""

    def test_creates_bluesky_scraper(self) -> None:
        scraper = create_scraper("bluesky")
        assert isinstance(scraper, BlueskyScraper)

    def test_creates_instaloader_scraper(self) -> None:
        scraper = create_scraper("instagram")
        assert isinstance(scraper, InstaloaderScraper)

    def test_creates_reddit_scraper(self) -> None:
        scraper = create_scraper("reddit")
        assert isinstance(scraper, RedditScraper)

    def test_creates_rss_scraper(self) -> None:
        scraper = create_scraper("rss")
        assert isinstance(scraper, RSSScraper)

    def test_creates_youtube_scraper(self) -> None:
        scraper = create_scraper("youtube")
        assert isinstance(scraper, YouTubeScraper)

    def test_backend_override(self) -> None:
        scraper = create_scraper("instagram", backend="bluesky")
        assert isinstance(scraper, BlueskyScraper)

    def test_unknown_backend_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown backend"):
            create_scraper("unknown_platform")

    def test_explicit_backend_takes_precedence(self) -> None:
        # Even if platform is instagram, explicit backend should be used
        scraper = create_scraper("instagram", backend="reddit")
        assert isinstance(scraper, RedditScraper)
