"""Third-party service providers — require API keys."""

from __future__ import annotations

# Known provider backends that may not be installed
_PROVIDER_BACKENDS = {"hikerapi", "xpoz"}


def create_provider(name: str, api_key: str | None = None):
    """Create a provider instance by name.

    Only imports the requested provider — the package works without
    provider SDKs installed.
    """
    providers: dict[str, type] = {}

    # Lazy-load optional providers
    if name in _PROVIDER_BACKENDS:
        if name == "hikerapi":
            from .hikerapi import HikerAPIProvider  # noqa: PLC0415

            providers["hikerapi"] = HikerAPIProvider
        elif name == "xpoz":
            from .xpoz import XpozProvider  # noqa: PLC0415

            providers["xpoz"] = XpozProvider

    cls = providers.get(name)
    if not cls:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")

    return cls(api_key=api_key)


__all__ = ["create_provider", "_PROVIDER_BACKENDS"]
