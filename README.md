# Socials Daily

Fetch recent posts from public social media accounts and generate a daily summary.

## Setup

```bash
uv sync
```

Optional backends (installed by default):

```bash
uv sync
```

For Xpoz backend (optional):

```bash
uv sync -E xpoz
```

## Usage

1. Edit `accounts.json` — grouped by platform:

```json
{
  "bluesky": {
    "accounts": ["bsky.app"]
  },
  "instagram": {
    "accounts": ["natgeo", "nasa"]
  }
}
```

Each account can have a custom `limit`:

```json
{
  "bluesky": {
    "accounts": [
      {"handle": "bsky.app"},
      {"handle": "atmos.bsky.social", "limit": 20}
    ]
  },
  "instagram": {
    "accounts": [
      {"handle": "natgeo"}
    ]
  }
}
```

Each platform can override the scraper backend (optional):

```json
{
  "instagram": {
    "backend": "hikerapi",
    "accounts": [
      {"handle": "natgeo"}
    ]
  }
}
```

**Backend resolution** (highest to lowest priority):
1. CLI `--backend` flag (overrides everything)
2. Platform `backend` in `accounts.json`
3. Default mapping (`instagram` → `instaloader`, `bluesky` → `bluesky`, etc.)

2. Run the scraper:

```bash
# Default: Bluesky (free, no auth needed)
uv run python -m socials_daily scrape

# Instagram (free, rate-limited)
uv run python -m socials_daily scrape --backend instaloader

# HikerAPI (pay-per-request, ~$0.0006/request)
uv run python -m socials_daily scrape --backend hikerapi --api-key YOUR_KEY

# Xpoz (pre-indexed data, free tier available)
uv run python -m socials_daily scrape --backend xpoz --api-key YOUR_KEY
```

3. Check the output:

```
output/daily-summary-YYYY-MM-DD.md   # Markdown summary
output/daily-summary-YYYY-MM-DD.json # JSON for programmatic use
```

## Add Accounts

```bash
# Bluesky (default)
uv run python -m socials_daily add bsky.app

# Instagram
uv run python -m socials_daily add natgeo --platform instagram

# With custom limit
uv run python -m socials_daily add atmos.bsky.social --platform bluesky --limit 20

# Set platform backend
uv run python -m socials_daily add natgeo --platform instagram --backend hikerapi
```

## Scrapers

| Backend | Cost | Setup | Best For |
|---|---|---|---|
| `bluesky` | Free | None | Public Bluesky accounts |
| `instaloader` | Free | None | 1-5 Instagram accounts, low volume |
| `reddit` | Free | None | Subreddit posts |
| `rss` | Free | None | Any RSS/Atom feed |
| `hikerapi` | ~$0.0006/request | API key | Reliable, high volume |
| `xpoz` | Free tier available | API key | Pre-indexed data, multi-platform |

### Bluesky (default)

Uses Bluesky's public AT Protocol API. No authentication required.

```bash
uv run python -m socials_daily scrape --backend bluesky
```

### Instaloader

Free, open-source Instagram scraper. Rate-limited by Instagram.

### HikerAPI

REST API with 100+ endpoints. No blocks, no rate limits.

```bash
export HIKERAPI_TOKEN=your-key
uv run python -m socials_daily scrape --backend hikerapi
```

### Xpoz

Pre-indexed social data API. Supports Instagram, Twitter, TikTok, Reddit.

```bash
export XPOZ_API_KEY=your-key
uv run python -m socials_daily scrape --backend xpoz
```

### Reddit

Fetches recent posts from public subreddits via Reddit's JSON API. No authentication required.

```bash
# Add a subreddit
uv run python -m socials_daily add programming --platform reddit

# Scrape
uv run python -m socials_daily scrape
```

### RSS

Scrapes any RSS/Atom feed. The `handle` field holds the feed URL.

```bash
# Add an RSS feed
uv run python -m socials_daily add https://www.reddit.com/r/programming/.rss --platform rss

# Scrape
uv run python -m socials_daily scrape
```

## Project Structure

```
accounts.json         # Accounts grouped by platform (with optional backend config)
src/socials_daily/    # Source code
├── __main__.py       # Entry point
└── scrapers/         # Scraper backends
    ├── base.py       # Abstract interface
    ├── bluesky.py
    ├── instaloader.py
    ├── reddit.py     # Reddit JSON API
    ├── rss.py        # RSS/Atom feeds
    ├── hikerapi.py
    └── xpoz.py
output/               # Generated daily summaries
pyproject.toml        # Project config (uv)
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed breakdown of the scraper layer, config resolution, deduplication system, and data flow.
