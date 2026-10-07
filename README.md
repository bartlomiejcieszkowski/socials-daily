# Socials Daily

Fetch recent posts from public social media accounts and generate a daily summary.

## Quick Start

```bash
pip install socials-daily
```

Create `accounts.json`:

```json
{
  "bluesky": {
    "accounts": [{"handle": "bsky.app"}]
  },
  "instagram": {
    "accounts": [{"handle": "natgeo"}]
  }
}
```

Run the scraper:

```bash
python -m socials_daily scrape
```

Output:

```
output/daily-summary-YYYY-MM-DD.md   # Markdown summary
output/daily-summary-YYYY-MM-DD.json # JSON for programmatic use
```

## Usage

### Scrape

```bash
# Default: Bluesky (free, no auth needed)
python -m socials_daily scrape

# Instagram (free, rate-limited)
python -m socials_daily scrape --backend instaloader

# HikerAPI (pay-per-request, ~$0.0006/request)
python -m socials_daily scrape --backend hikerapi --api-key YOUR_KEY

# Xpoz (pre-indexed data, free tier available)
python -m socials_daily scrape --backend xpoz --api-key YOUR_KEY
```

### Add Accounts

```bash
# Bluesky (default)
python -m socials_daily add bsky.app

# Instagram
python -m socials_daily add natgeo --platform instagram

# With custom limit
python -m socials_daily add atmos.bsky.social --platform bluesky --limit 20

# Set platform backend
python -m socials_daily add natgeo --platform instagram --backend hikerapi
```

## Configuration

### accounts.json

Accounts are grouped by platform. Each account can have a custom `limit`:

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

Each platform can override the scraper backend:

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

### API Keys

API keys are stored in `.socials_daily.config.json` (gitignored). Keys are resolved in order:
1. CLI `--api-key` flag
2. `.socials_daily.config.json`
3. Environment variables (`HIKERAPI_TOKEN`, `XPOZ_API_KEY`)

## Backends

| Backend | Cost | Setup | Best For |
|---|---|---|---|
| `bluesky` | Free | None | Public Bluesky accounts |
| `instaloader` | Free | None | 1-5 Instagram accounts, low volume |
| `reddit` | Free | None | Subreddit posts |
| `rss` | Free | None | Any RSS/Atom feed |
| `youtube` | Free | `pip install "socials-daily[youtube]"` | YouTube channel videos |
| `hikerapi` | ~$0.0006/request | API key | Reliable, high volume |
| `xpoz` | Free tier available | API key | Pre-indexed data, multi-platform |

### Bluesky

Uses Bluesky's public AT Protocol API. No authentication required.

```bash
python -m socials_daily scrape --backend bluesky
```

### Instaloader

Free, open-source Instagram scraper. Rate-limited by Instagram.

### HikerAPI

REST API with 100+ endpoints. No blocks, no rate limits.

```bash
export HIKERAPI_TOKEN=your-key
python -m socials_daily scrape --backend hikerapi
```

### Xpoz

Pre-indexed social data API. Supports Instagram, Twitter, TikTok, Reddit.

```bash
export XPOZ_API_KEY=your-key
python -m socials_daily scrape --backend xpoz
```

### YouTube

Fetches recent videos from YouTube channels. Requires optional `yt-dlp` dependency.

```bash
# Install YouTube support
pip install "socials-daily[youtube]"

# Add a channel (handle or name)
python -m socials_daily add mkbhd --platform youtube

# Scrape
python -m socials_daily scrape
```

### Reddit

Fetches recent posts from public subreddits via Reddit's JSON API. No authentication required.

```bash
# Add a subreddit
python -m socials_daily add programming --platform reddit

# Scrape
python -m socials_daily scrape
```

### RSS

Scrapes any RSS/Atom feed. The `handle` field holds the feed URL.

```bash
# Add an RSS feed
python -m socials_daily add https://www.reddit.com/r/programming/.rss --platform rss

# Scrape
python -m socials_daily scrape
```

## Development

### Setup

```bash
uv sync
```

Optional backends:

```bash
uv sync -E hikerapi -E xpoz -E youtube
```

### Project Structure

```
accounts.json         # Accounts grouped by platform (with optional backend config)
src/socials_daily/    # Source code
├── __main__.py       # Entry point
├── providers/        # Third-party service providers (require API keys)
│   ├── hikerapi.py
│   └── xpoz.py
└── scrapers/         # Direct scraping (no third-party services)
    ├── base.py       # Abstract interface
    ├── bluesky.py
    ├── instaloader.py
    ├── reddit.py
    ├── rss.py
    └── youtube.py
output/               # Generated daily summaries
pyproject.toml        # Project config (uv)
```

### Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed breakdown of the scraper layer, config resolution, deduplication system, and data flow.

## License

MIT — Copyright 2026 Bartlomiej Cieszkowski
