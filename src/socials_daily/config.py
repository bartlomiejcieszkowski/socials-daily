"""Load API keys from .socials_daily.config.json."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_FILE = Path(".socials_daily.config.json")


def load_config() -> dict:
    """Load config from file, or return empty dict if not found."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def get_api_key(service: str) -> str | None:
    """Get API key for a service. Checks config file first, then env var."""
    config = load_config()
    key = config.get(f"{service}_token") or config.get(f"{service}_api_key")
    if key:  # non-empty string
        return key
    # Fallback to env var
    import os
    for suffix in ("_TOKEN", "_API_KEY"):
        env_key = f"{service.upper()}{suffix}"
        val = os.getenv(env_key)
        if val:
            return val
    return None
