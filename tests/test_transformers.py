"""Tests for defang_url transformer."""

from __future__ import annotations

from datetime import datetime, timezone

from socials_daily.transformers import get_transformer
from socials_daily.transformers.base import Post


class TestDefangUrl:
    """Tests for defang_url transformer."""

    def test_defang_http(self) -> None:
        """http:// should be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Visit http://example.com",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Visit http[://]example[.]com"

    def test_defang_https(self) -> None:
        """https:// should be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Check https://secure.com",
            link="https://secure.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Check https[://]secure[.]com"

    def test_defang_email(self) -> None:
        """@ should become [@]"""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Contact user@example.com",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Contact user[@]example[.]com"

    def test_defang_ip(self) -> None:
        """IP addresses should have dots defanged"""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Server at 192.168.1.1",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Server at 192[.]168[.]1[.]1"

    def test_no_caption_unchanged(self) -> None:
        """Posts with empty caption should pass through unchanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == ""

    def test_non_url_dots_unchanged(self) -> None:
        """Non-URL dots should NOT be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="I have 3.14159 pi and 1.2.3 version",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "I have 3.14159 pi and 1.2.3 version"

    def test_non_url_colons_unchanged(self) -> None:
        """Non-URL colons should NOT be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Time: 10:30 AM",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Time: 10:30 AM"

    def test_non_email_at_unchanged(self) -> None:
        """Non-email @ should NOT be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Price: $10 @ store",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Price: $10 @ store"

    def test_url_with_path(self) -> None:
        """URLs with paths should have slashes defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Check http://example.com/path/to/file",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Check http[://]example[.]com[/]path[/]to[/]file"

    def test_multiple_targets(self) -> None:
        """Multiple URLs/emails in one caption should all be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Visit http://example.com or email user@example.com",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Visit http[://]example[.]com or email user[@]example[.]com"

    def test_ssh_url(self) -> None:
        """Non-http URLs should also be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Clone ssh://git@github.com/user/repo",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Clone ssh[://]git[@]github[.]com[/]user[/]repo"

    def test_ftp_url(self) -> None:
        """FTP URLs should be defanged."""
        cls = get_transformer("defang_url")
        assert cls is not None
        transformer = cls()
        posts = [Post(
            caption="Download ftp://files.example.com/pub/data.zip",
            link="http://example.com",
            date=datetime.now(timezone.utc),
        )]
        result = transformer.transform(posts)
        assert result[0].caption == "Download ftp[://]files[.]example[.]com[/]pub[/]data[.]zip"
