# Plan: YouTube Scraper

## Goal
Add YouTube channel video tracking as an optional scraper backend.

## Feasibility: ✅ Yes, straightforward

yt-dlp is a Python library with 1,500+ site extractors. For metadata extraction only (no download), it's lightweight and requires no auth.

### Key details
- **Dependency**: `yt-dlp` — optional, installed via `uv sync -E youtube`
- **No auth required** — works on public pages
- **ffmpeg** — optional, only needed for downloading (not for metadata extraction)
- **Size**: ~2.5 MB pure Python
- **Reliability**: YouTube changes page structure frequently, but yt-dlp updates quickly

### How it works
```python
import yt_dlp

ydl_opts = {'skip_download': True, 'quiet': True}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info("https://www.youtube.com/@mkbhd/videos", download=False)
    # info['entries'] -> list of video metadata dicts
```

## Implementation

### New file: `src/socials_daily/scrapers/youtube.py`

```python
class YouTubeScraper(Scraper):
    name = "youtube"

    def __init__(self) -> None:
        # Lazy import — fail gracefully if yt-dlp not installed
        try:
            import yt_dlp
            del yt_dlp
        except ImportError as exc:
            self._import_error = exc

    def fetch_posts(self, username: str, limit: int = 10) -> list[Post]:
        # URL: https://www.youtube.com/@{handle}/videos
        # Extract info with skip_download=True
        # Filter entries by today's date
        # Map: description (or title) → caption, webpage_url → link, upload_date → date
```

### accounts.json change

```json
{
  "youtube": {
    "accounts": [
      {"handle": "mkbhd"},
      {"handle": "veritasium", "limit": 5}
    ]
  }
}
```

`handle` = YouTube channel handle (with or without `@`) or channel name.

### Cross-cutting changes

| File | Change |
|------|--------|
| `pyproject.toml` | Add `yt-dlp` to `[project.optional-dependencies]` |
| `scrapers/youtube.py` | New file |
| `scrapers/__init__.py` | Import + register YouTubeScraper in backends dict + PLATFORM_MAP |
| `__main__.py` | Add `"youtube"` to SUPPORTED_PLATFORMS |
| `ARCHITECTURE.md` | Add YouTube to table + structure diagram |
| `README.md` | Add YouTube section + usage examples |

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| YouTube page structure changes | Medium | yt-dlp updates frequently; graceful error handling |
| Heavy dependency (2.5 MB) | Low | Optional dep — only installed by users who need it |
| No community posts support | Medium | yt-dlp extracts uploads/videos, not community tab posts |
| Rate limiting | Low | yt-dlp respects YouTube's rate limits; 3s sleep between accounts |

## Comparison: yt-dlp vs YouTube Data API

| | yt-dlp | YouTube Data API v3 |
|---|---|---|
| Auth | None | API key required |
| Rate limit | ~unlimited (page scraping) | 10,000 units/day |
| Metadata | Rich (all fields) | Rich (some fields differ) |
| Cost | Free | Free (up to quota) |
| Reliability | Fragile (page scraping) | Stable (official API) |
| Complexity | Simple import | API key management |
| Extra features | Thumbnails, subtitles | Channel stats, comments |

yt-dlp wins on simplicity (no auth, no key management). YouTube API is more stable but requires setup.

## Secondary Use Case (Future): Video Link Enrichment

When a post from any platform (Bluesky, Reddit, Instagram) contains a video URL (YouTube, Twitch, etc.), enrich the summary with metadata:

```
## @mkbhd
- New Studio Setup! — https://youtube.com/watch?v=abc123 (10:32, 1.2M views)
```

Implementation approach:
- Post-processing step that scans all post links
- Detects video URLs (YouTube, Twitch, etc.)
- Fetches metadata via yt-dlp (duration, view count)
- Enriches the markdown output with metadata

This would be a separate `--enrich` flag or automatic post-processing step.
