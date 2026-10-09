"""Defang URL transformer — obfuscates URLs, emails, and IPs for safe display."""

from __future__ import annotations

import re

from .base import Post, Transformer, transformer

# Match any URL with a scheme (http, https, ftp, ssh, etc.)
_URL_RE = re.compile(r'[a-zA-Z][a-zA-Z0-9+.-]*://\S+')
_EMAIL_RE = re.compile(r'\S+@\S+\.\S+')
_IP_RE = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')


def _defang_url(url: str) -> str:
    """Defang a single URL in one pass, skipping already-defanged content."""
    result = []
    i = 0
    while i < len(url):
        # Skip already-defanged segments like [://] or [.] or [/]
        if url[i] == '[':
            bracket_end = url.find(']', i)
            if bracket_end != -1:
                result.append(url[i:bracket_end + 1])
                i = bracket_end + 1
                continue
        # Check for :// at current position
        if url[i:i+3] == '://':
            result.append('[://]')
            i += 3
        elif url[i] == '/':
            result.append('[/]')
            i += 1
        elif url[i] == '.':
            result.append('[.]')
            i += 1
        else:
            result.append(url[i])
            i += 1
    return ''.join(result)


def _defang_email(email: str) -> str:
    """Defang a single email address."""
    return email.replace('@', '[@]').replace('.', '[.]')


def _defang_ip(ip: str) -> str:
    """Defang a single IP address."""
    return ip.replace('.', '[.]')


@transformer("defang_url")
class DefangUrlTransformer(Transformer):
    """Defang URLs, emails, and IP addresses for safe display.

    Only targets actual URLs, email addresses, and IP addresses —
    not arbitrary dots or colons in regular text.
    """

    name = "defang_url"

    def transform(self, posts: list[Post]) -> list[Post]:
        """Defang URLs, emails, and IPs in post captions."""
        for post in posts:
            if post.caption:
                # Email first (URLs contain email patterns)
                post.caption = _EMAIL_RE.sub(lambda m: _defang_email(m.group()), post.caption)
                post.caption = _URL_RE.sub(lambda m: _defang_url(m.group()), post.caption)
                post.caption = _IP_RE.sub(lambda m: _defang_ip(m.group()), post.caption)
        return posts
