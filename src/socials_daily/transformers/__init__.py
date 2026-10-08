"""Transformer loader — discovers and registers transformers."""

from __future__ import annotations

import importlib
import importlib.metadata
import logging
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

from .base import Transformer, transformer

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

# Registry of all discovered transformers
_transformers: dict[str, type[Transformer]] = {}


def _discover_local_transformers() -> None:
    """Auto-discover transformers from the transformers/ directory."""
    for importer, mod_name, is_pkg in pkgutil.iter_modules([str(Path(__file__).parent)]):
        if mod_name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f".{mod_name}", package="socials_daily.transformers")
            # Find all classes with a 'name' attribute (registered via @transformer)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and hasattr(attr, "name") and hasattr(attr, "transform"):
                    _transformers[attr.name] = attr
        except Exception as exc:
            log.warning("Failed to load transformer module %s: %s", mod_name, exc)


def _discover_entry_point_transformers() -> dict[str, type[Transformer]]:
    """Discover transformers registered via pip entry points."""
    discovered: dict[str, type[Transformer]] = {}
    try:
        eps = importlib.metadata.entry_points(group="socials_daily.transformers")
        for ep in eps:
            try:
                register = ep.load()
                if callable(register):
                    register()  # Type: ignore[call-arg] — calls the registration function
                    log.info("Loaded transformer package: %s", ep.name)
            except Exception as exc:
                log.warning("Failed to load entry point %s: %s", ep.name, exc)
    except Exception:
        pass  # No entry points or metadata unavailable
    return discovered


def get_transformer(name: str) -> type[Transformer] | None:
    """Get a transformer by name."""
    return _transformers.get(name)


def list_transformers() -> list[str]:
    """List all available transformer names."""
    return sorted(_transformers.keys())


def load_all() -> None:
    """Discover and register all available transformers."""
    if not _transformers:
        _discover_local_transformers()
        _discover_entry_point_transformers()


# Auto-discover on import
load_all()

__all__ = ["Transformer", "transformer", "get_transformer", "list_transformers", "load_all"]
