# Plan: Reddit + RSS Support

## Goal
Add two new feed sources:
1. **Reddit** — track subreddit posts (new posts filtered to today)
2. **RSS** — generic RSS/Atom feed scraping (any feed URL)

---

## 1. Reddit Scraper

### Feasibility: ✅ Yes, straightforward

Reddit has a public JSON API that works without authentication:
```
https://www.reddit.com/r/{subreddit}/new.json
https://www.reddit.com/r/{subreddit}/hot.json
https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=day
```

- No auth required for basic reading
- Rate limited (~30-60 requests/min without auth, ~1000+/min with OAuth)
- Returns structured JSON with post metadata
- Can use `httpx` (already available via hikerapi) — no new dependency needed
- Alternative: `praw` library (full OAuth, more features, but heavier)

**Decision**: Use Reddit's public JSON API via `httpx` (no new dependency). Mention `praw` as an optional upgrade path.

### Implementation

**New file**: `src/socials_daily/scrapers/reddit.py`

```python
class RedditScraper(Scraper):
    name = "reddit"

    def fetch_posts(self, subreddit: str, limit: int = 10) -> list[Post]:
        # Fetch https://www.reddit.com/r/{subreddit}/new.json
        # Parse response: data.children[].data -> {title, url, created_utc, selftext}
        # Filter to today (UTC)
        # Return list[Post]
```

- `created_utc` → convert to `datetime` → filter by today's date
- `selftext` → caption (may be empty for link posts)
- `url` → link
- `title` → caption if selftext is empty
- Handle markdown → plain text conversion for selftext

### accounts.json change

Reddit uses subreddits, not handles. New platform entry:

```json
{
  "reddit": {
    "accounts": [
      {"handle": "programming"},
      {"handle": "python", "limit": 20}
    ]
  }
}
```

Same `handle` field semantics — just represents a subreddit name.

### CLI change

Add `reddit` to `SUPPORTED_PLATFORMS` in `__main__.py`.

---

## 2. RSS Scraper

### Feasibility: ✅ Yes, straightforward

RSS/Atom is a well-standardized XML format. Python has excellent libraries:
- **`feedparser`** — the de facto standard, handles all RSS/Atom versions, malformed feeds gracefully
- Alternative: `xml.etree` (stdlib) — but RSS/Atom has many variants, `feedparser` handles edge cases

**Decision**: Add `feedparser` as a dependency. It's lightweight (~50KB), battle-tested, and handles all RSS/Atom quirks.

### Implementation

**New file**: `src/socials_daily/scrapers/rss.py`

```python
class RSSScraper(Scraper):
    name = "rss"

    def fetch_posts(self, feed_url: str, limit: int = 10) -> list[Post]:
        # Use feedparser.parse(feed_url)
        # Iterate feed.entries
        # Filter to today (UTC) via published_parsed / updated_parsed
        # Map: entry.title → caption, entry.link → link, entry.published_parsed → date
        # Handle missing fields gracefully
```

- RSS feeds don't have "handles" — they have URLs. The `handle` field in accounts.json will hold the feed URL.
- RSS feeds typically don't have captions in the social-media sense — use `title` or `summary`/`content`
- Date handling: RSS feeds vary (pubDate, updated, dc:date, etc.) — `feedparser` normalizes these

### accounts.json change

New `rss` platform. Since RSS feeds are URLs, the structure needs a slight tweak:

```json
{
  "rss": {
    "accounts": [
      {"handle": "https://www.reddit.com/r/programming/.rss"},
      {"handle": "https://hnrss.org/newest?q=python", "limit": 20}
    ]
  }
}
```

**Consideration**: Should RSS feeds be grouped differently? Options:
- **Option A**: Same structure, `handle` = feed URL (simple, consistent)
- **Option B**: RSS gets a `url` field instead of `handle`
- **Option C**: RSS feeds as top-level keys, not inside `accounts`

**Decision**: Option A — keep it simple. `handle` = feed URL. Users understand this. The scraper knows it's dealing with a URL, not a handle.

### CLI change

Add `rss` to `SUPPORTED_PLATFORMS` in `__main__.py`.

---

## 2. Cross-cutting Changes

### 2.1 `pyproject.toml`
- Add `feedparser>=6.0.0` to dependencies
- (Reddit uses `httpx` which is already a transitive dependency — no new dep needed)

### 2.2 `scrapers/__init__.py`
- Import and register `RedditScraper` and `RSSScraper`
- Add to `PLATFORM_MAP`: `"reddit": "reddit"`, `"rss": "rss"`
- Add to `backends` dict
- Update `__all__`

### 2.3 `__main__.py`
- Add `"reddit"` and `"rss"` to `SUPPORTED_PLATFORMS`
- (No other changes needed — the generic loop already handles any platform)

### 2.4 `.gitignore`
- No changes needed

### 2.5 `ARCHITECTURE.md`
- Add Reddit and RSS rows to the backend table
- Update project structure diagram

### 2.6 `README.md`
- Add Reddit and RSS to supported platforms list
- Add example accounts.json entries

---

## 3. Implementation Order

1. **Reddit scraper** — no new dependency, quick win
2. **RSS scraper** — needs `feedparser` dependency
3. **Wire up both** in `__main__.py` and `scrapers/__init__.py`
4. **Update docs** (ARCHITECTURE.md, README.md)
5. **Test** both scrapers

---

## 4. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Reddit rate limiting without auth | Low | 3s sleep between accounts already helps; can add retry logic |
| Reddit JSON API changes | Low | Reddit's JSON API is stable; if broken, `praw` is a fallback |
| RSS feed URLs are broken/malformed | Low | `feedparser` is very tolerant of malformed XML |
| RSS feeds don't include dates | Low | Skip entries without dates, log warning |
| RSS feeds have posts from before today only | Low | Same behavior as existing scrapers — just no output |

---

## 5. Summary

Both features are **low-risk, high-value additions** that follow the existing architecture pattern exactly:
- One new file per scraper (`scrapers/reddit.py`, `scrapers/rss.py`)
- Register in `scrapers/__init__.py`
- Add to `SUPPORTED_PLATFORMS` in `__main__.py`
- No changes to the core loop or data model

The only new external dependency is `feedparser` (~50KB).
