# Socials Daily — Architecture

## Overview

A Python tool that fetches recent posts from public social media accounts and generates a daily markdown/JSON summary. Supports four scraper backends via a pluggable interface, starting with Bluesky and Instagram.

## Project Structure

```
accounts.json             # Accounts grouped by platform (with optional backend config)
pyproject.toml            # uv project config
src/socials_daily/
├── __main__.py           # CLI entry point, orchestration
├── config.py             # API key resolution (explicit > config > env)
└── scrapers/
    ├── __init__.py       # Factory: create_scraper(backend, api_key)
    ├── base.py           # Abstract interface: Scraper protocol + Post dataclass
    ├── bluesky.py        # Bluesky AT Protocol (public, no auth)
    ├── instaloader.py    # Free, rate-limited (instaloader library)
    ├── reddit.py         # Reddit JSON API (httpx, no auth)
    ├── rss.py            # RSS/Atom feeds (feedparser)
    ├── hikerapi.py       # REST API, pay-per-request (httpx)
    └── xpoz.py           # Pre-indexed DB (xpoz SDK)
output/                   # Generated daily summaries (gitignored)
  ├── daily-summary-YYYY-MM-DD.md
  └── daily-summary-YYYY-MM-DD.json
.seen.json                # Post permalink dedup tracker (gitignored)
.socials_daily.config.json    # API keys (gitignored)
```

## Data Flow

```
accounts.json ──→ load_accounts()  ──→ {platform: {backend?, accounts: [{handle, limit?}]}}
                        │
            for platform, config in accounts.items():
                backend = CLI_flag > config.backend > default_mapping
                create_scraper(platform, backend=backend) ──→ scraper
                        │
                for account in config.accounts:
                    fetch_posts() ──→ list[Post] (today only)
                        │
                 deduplicate against .seen.json
                        │
                 write output/
                 ├── daily-summary-YYYY-MM-DD.md
                 ├── daily-summary-YYYY-MM-DD.json
                 └── .seen.json (updated)
```

## Components

### 1. CLI Layer (`__main__.py`)

`argparse` subcommands:
- **`scrape`** (default) — fetch posts from all accounts (all platforms)
  - `--api-key` — override API key (highest priority)
  - `--backend` — override scraper backend for all platforms (takes precedence over platform config)
- **`add <handle> [--platform bluesky|instagram|...] [--limit N] [--backend X]`** — append handle to `accounts.json`

Orchestrates the flow: load accounts → create scraper → fetch posts → deduplicate → write output.

### 2. Scraper Layer (`scrapers/`)

Abstract protocol:

```python
@dataclass
class Post:
    caption: str
    link: str
    date: datetime

class Scraper(Protocol):
    name: str
    def fetch_posts(handle: str, limit: int) -> list[Post]: ...
```

Each backend implements `fetch_posts()` → returns `Post` objects filtered to **today's date only**.

| Backend | Cost | Transport | Auth |
|---|---|---|---|
| `bluesky` | Free | AT Protocol (atproto lib) | None (public) |
| `instaloader` | Free | HTTP (instaloader lib) | None |
| `reddit` | Free | JSON API (httpx) | None |
| `rss` | Free | RSS/Atom XML (feedparser) | None |
| `hikerapi` | ~$0.0006/request | REST API (httpx) | `x-access-key` header |
| `xpoz` | Free tier | SDK (xpoz) | API key |

Platform-to-scraper mapping in `scrapers/__init__.py`:

```python
PLATFORM_MAP = {
    "instagram": "instaloader",
    "bluesky": "bluesky",
    "reddit": "reddit",
    "rss": "rss",
    "hikerapi": "hikerapi",
    "xpoz": "xpoz",
}

def create_scraper(platform: str, api_key: str | None = None, backend: str | None = None) -> Scraper:
    # Resolution: explicit backend arg > platform config > default mapping
    scraper_name = backend or PLATFORM_MAP.get(platform, platform)
    key = api_key or get_api_key(scraper_name)  # explicit > config > env
    return cls(api_key=key) if key else cls()
```

Backend resolution (highest to lowest priority):
1. **CLI `--backend` flag** — overrides all
2. **Platform `backend` in `accounts.json`** — per-platform override
3. **Default mapping** — platform name → scraper name

The `__main__.py` groups accounts by platform, resolves the scraper backend per platform, and fetches from each account sequentially.

### 3. Config Layer (`config.py`)

Resolves API keys in priority order:

1. **Explicit `--api-key` flag** (highest)
2. **`.socials_daily.config.json`** file
3. **Environment variable** (`HIKERAPI_TOKEN`, `XPOZ_API_KEY`)

```json
// .socials_daily.config.json (gitignored)
{
  "hikerapi_token": "...",
  "xpoz_api_key": "..."
}
```

### 4. Deduplication (`.seen.json`)

Post permalinks tracked across runs in a JSON array:

```json
["https://bsky.app/profile/did:plc:xxx/post/yyy", "https://www.instagram.com/p/ABC123/"]
```

- **Load** at scraper start
- **Filter** out seen posts before adding to output
- **Save** updated list at end
- Result: each post is only scraped once, ever — even if output files are deleted

## Key Design Decisions

- **Backend-agnostic core**: `__main__.py` knows nothing about specific scrapers, only the `Scraper` protocol. Adding a new backend requires one file in `scrapers/` and a registration in `__init__.py`.
- **Today-only filter**: each scraper returns only today's posts, so daily output files are naturally independent.
- **Dedup at core layer**: deduplication happens in `__main__.py`, not in scrapers — works regardless of backend.
- **Pacing**: 3s sleep between accounts (needed for instaloader, harmless for APIs).
- **Config file**: `.socials_daily.config.json` is gitignored, structured JSON for API keys.
- **Bluesky uses public API**: No authentication needed — uses `com.atproto.repo.listRecords` endpoint directly via the `atproto` library.
