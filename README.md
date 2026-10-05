# Socials Daily

Fetch recent posts from public social media accounts and generate a daily summary.

## Setup

```bash
uv sync
```

For Xpoz backend (optional):

```bash
uv sync -E xpoz
```

## Usage

1. Edit `accounts.txt` — one handle per line:

```
bsky.app
natgeo
nasa
```

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
```

## Scrapers

| Backend | Cost | Setup | Best For |
|---|---|---|---|
| `bluesky` | Free | None | Public Bluesky accounts |
| `instaloader` | Free | None | 1-5 Instagram accounts, low volume |
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

## Project Structure

```
accounts.txt          # List of social handles
src/socials_daily/    # Source code
├── __main__.py       # Entry point
└── scrapers/         # Scraper backends
    ├── base.py       # Abstract interface
    ├── bluesky.py
    ├── instaloader.py
    ├── hikerapi.py
    └── xpoz.py
output/               # Generated daily summaries
pyproject.toml        # Project config (uv)
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed breakdown of the scraper layer, config resolution, deduplication system, and data flow.
