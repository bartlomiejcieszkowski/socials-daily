# Socials Daily — Architecture

## Overview

A Python tool that fetches recent posts from public social media accounts and generates a daily markdown/JSON summary. Supports four scraper backends via a pluggable interface, starting with Bluesky and Instagram.

## Project Structure

```
accounts.txt              # List of social handles (one per line)
pyproject.toml            # uv project config
src/socials_daily/
├── __main__.py           # CLI entry point, orchestration
├── config.py             # API key resolution (explicit > config > env)
└── scrapers/
    ├── __init__.py       # Factory: create_scraper(backend, api_key)
    ├── base.py           # Abstract interface: Scraper protocol + Post dataclass
    ├── bluesky.py        # Bluesky AT Protocol (public, no auth)
    ├── instaloader.py    # Free, rate-limited (instaloader library)
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
accounts.txt ──→ load_accounts()
                        │
                 create_scraper() ──→ backend-specific API call
                        │
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
- **`scrape`** (default) — fetch posts from all accounts
  - `--backend {bluesky,instaloader,hikerapi,xpoz}` — select scraper (default: bluesky)
  - `--api-key` — override API key (highest priority)
- **`add <handle> [--platform bluesky|instagram]`** — append handle to `accounts.txt`

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
| `hikerapi` | ~$0.0006/request | REST API (httpx) | `x-access-key` header |
| `xpoz` | Free tier | SDK (xpoz) | API key |

Factory pattern in `scrapers/__init__.py`:

```python
def create_scraper(backend: str, api_key: str | None = None) -> Scraper:
    key = api_key or get_api_key(backend)  # explicit > config > env
    return cls(api_key=key) if key else cls()
```

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
