# yt-dlp Support — Feasibility Evaluation

## What yt-dlp is

yt-dlp is a video/audio downloader with a Python library API. It supports **1,500–1,700+ sites** (YouTube, Twitch, Vimeo, Dailymotion, TikTok, and many more).

## Feasibility: ✅ Yes, straightforward

### How it works (metadata only, no download)

```python
import yt_dlp

ydl_opts = {
    'skip_download': True,
    'quiet': True,
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info("https://youtube.com/watch?v=...", download=False)
    # info is a dict with title, description, upload_date, view_count, duration, etc.
```

- `skip_download=True` — never downloads the video, only fetches metadata
- ffmpeg is **optional** — only needed for downloading/merging formats, not for metadata extraction
- Python library API is clean and importable

### Dependency size

| Package | Size | Notes |
|---------|------|-------|
| `yt-dlp` | ~2.5 MB | 1,500+ extractors, many unused for YouTube-only |
| ffmpeg | ~100 MB | Optional, only needed if downloading |

yt-dlp itself is pure Python — no compilation, no native deps. ffmpeg is a separate install.

## Possible Use Cases

### 1. YouTube Channel Scraper (primary use case)

Track recent videos from YouTube channels, treating each video as a "post":

```json
{
  "youtube": {
    "accounts": [
      {"handle": "UC_x5XG1OV2P6uZZ5FSM9Ttw"},  // Google's channel ID
      {"handle": "mkbhd", "limit": 10}            // handle or channel ID
    ]
  }
}
```

Each video becomes a `Post`:
- `caption` → video description (or title if no description)
- `link` → `https://youtube.com/watch?v=...`
- `date` → upload date
- Extra metadata available: title, view count, duration, like count, thumbnail URL

This is the natural fit — YouTube is a major platform we don't currently support.

### 2. Video Link Enrichment (secondary)

When an existing post (Bluesky, Reddit, Instagram) contains a video URL (YouTube, Twitch, etc.), use yt-dlp to extract metadata and enrich the summary:

```
## @mkbhd
- New Studio Setup! — https://youtube.com/watch?v=abc123 (10:32, 1.2M views)
```

This would add a post-processing step that scans all post links and enriches video URLs with metadata.

### 3. Generic Video Platform Support (theoretical)

Since yt-dlp supports 1,500+ sites, we could add more video platforms. But for a "daily posts" tracker, YouTube is the overwhelming use case. Other platforms (Twitch VODs, etc.) are niche.

## Pros

- **One dependency covers YouTube** (and 1,500+ other video sites)
- **No API key needed** — yt-dlp works with public pages
- **Rich metadata** — title, description, view count, duration, like count, thumbnails, subtitles, etc.
- **Well-maintained** — frequent updates, large community
- **Metadata extraction is fast** — no video download, just HTTP requests

## Cons

- **Heavy dependency** — 2.5 MB for pure metadata extraction is disproportionate
- **YouTube-specific**: Most of the 1,500+ extractors are unused if we only need YouTube
- **Fragile**: YouTube changes their page structure frequently, yt-dlp needs updates to keep up (but they update quickly)
- **Not a "daily posts" native fit**: YouTube's "recent" content lives in multiple places (uploads playlist, shorts, community posts) — yt-dlp handles uploads/playlists well but not community posts
- **ffmpeg optional but commonly expected**: Users may need it for full functionality

## Comparison: yt-dlp vs YouTube Data API

| | yt-dlp | YouTube Data API v3 |
|---|---|---|
| Auth | None | API key required |
| Rate limit | ~unlimited (page scraping) | 10,000 units/day |
| Metadata | Rich (all fields) | Rich (some fields differ) |
| Cost | Free | Free (up to quota) |
| Reliability | Fragile (page scraping) | Stable (official API) |
| Complexity | Simple import | API key management |
| Extra features | Thumbnails, subtitles, etc. | Channel stats, comments, etc. |

yt-dlp wins on simplicity (no auth, no key management). The YouTube API is more stable but requires setup.

## Recommendation

**Feasible and worth doing — but as an optional dependency.**

```toml
[project.optional-dependencies]
youtube = ["yt-dlp>=2024.0.0"]
```

This way:
- Core project stays lightweight
- Users who want YouTube can `uv sync -E youtube`
- Video link enrichment could be a separate optional feature

**Implementation scope**: A single `YouTubeScraper` that extracts video metadata from channel uploads playlists, following the existing scraper pattern.
