"""Test configuration and shared fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_accounts() -> dict[str, dict]:
    """Sample accounts structure for testing."""
    return {
        "bluesky": {
            "accounts": [
                {"handle": "bsky.app"},
                {"handle": "atmos.bsky.social", "limit": 20},
            ],
        },
        "instagram": {
            "accounts": [
                {"handle": "natgeo"},
            ],
        },
    }


@pytest.fixture
def sample_accounts_with_backend() -> dict[str, dict]:
    """Sample accounts with backend configuration."""
    return {
        "instagram": {
            "backend": "hikerapi",
            "accounts": [
                {"handle": "natgeo"},
            ],
        },
    }
