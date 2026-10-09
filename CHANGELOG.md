# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] — 2026-10-07

### Added
- Test suite with pytest — 69 tests covering config, accounts, deduplication, scrapers, providers, and summary generation
- Custom exception types: `SocialsDailyError`, `ScraperError`, `ProviderError`, `ConfigError`, `AccountError`
- Structured logging in all scrapers and providers (replaced `print()` calls)
- API key validation warnings in hikerapi and xpoz providers
- HTTP error handling with descriptive messages in hikerapi (401, 404, 429)
- Error chaining with `from exc` for better debugging

### Changed
- Nothing

### Fixed
- Nothing

### Deprecated
- Nothing

### Removed
- Nothing

### Security
- Nothing

### Contributors
- [@bartlomiejcieszkowski](https://github.com/bartlomiejcieszkowski)

---

## [0.1.0] — 2026-10-07

### Added
- Multi-platform scraper support: Bluesky, Instagram, Reddit, RSS, YouTube
- Platform-grouped `accounts.json` with per-account metadata (handle, limit)
- Per-platform backend configuration with precedence resolution (CLI > config > default)
- Provider architecture: third-party services (HikerAPI, Xpoz) separated from direct scrapers
- Truly optional dependencies — HikerAPI, Xpoz, and YouTube load lazily
- Secure API key storage in `.socials_daily.config.json` (gitignored)
- Config resolution: CLI flag > config file > environment variables
- Post deduplication via permalink tracking in `.seen.json`
- Daily markdown and JSON summaries in `output/daily-summary-YYYY-MM-DD.*`
- MIT license
- GitHub Actions workflows: Build & Test, PyPI publish
- PyPI publishing support (hatchling, dynamic version, workflows)

### Changed
- Project renamed from `instagram-daily` to `socials-daily`
- Account storage migrated from flat `accounts.txt` to platform-grouped `accounts.json`
- Scraper base class uses `ABC` with `@abstractmethod` for idiomatic Python inheritance
- HikerAPI and Xpoz moved from `scrapers/` to `providers/` directory

### Fixed
- HikerAPI and Xpoz hard import crashes — now lazy-loaded
- Malformed config file JSON parsing — added error handling
- Type checking for `_PROVIDER_BACKENDS` import — added type ignore

### Deprecated
- Nothing

### Removed
- Nothing

### Security
- Nothing

### Contributors
- [@bartlomiejcieszkowski](https://github.com/bartlomiejcieszkowski)

---

## [0.3.0] — 2026-10-09

### Added
- **Transformer plugin architecture** — New `transformers/` module with auto-discovery of local `.py` files and pip entry point support via `importlib.metadata.entry_points()`
- **`pipelines.json`** — Pipeline configuration file with default transformer list and output format selection
- **`filter_no_caption` transformer** — Removes posts with empty or whitespace-only captions
- **`html_escape` transformer** — Escapes HTML entities in post captions for safe rendering
- **`@transformer("name")` decorator** — Simple way to register custom transformers
- **Auto-resume from last scrape** — `.last.socials-daily` file tracks last run date, scraper resumes from there on next run
- **`--since`, `--till`, `--day` CLI arguments** — Date range scraping for historical or multi-day summaries
- **Per-day output files** — One `daily-summary-YYYY-MM-DD.md` and `.json` file per day instead of one file for the whole range
- **Enhanced `Post` dataclass** — Added `platform`, `account`, and `tags` fields for richer post metadata
- **Pipeline logging** — Transforms log post counts before/after each transformer

### Changed
- Output generation now runs through the transformer pipeline before writing files
- `Post` objects now carry `platform` and `account` metadata throughout the pipeline
- Default output: one markdown file and one JSON file per day in `output/`

### Fixed
- Nothing

### Deprecated
- Nothing

### Removed
- Nothing

### Security
- Nothing

### Contributors
- [@bartlomiejcieszkowski](https://github.com/bartlomiejcieszkowski)

[Unreleased]: https://github.com/bartlomiejcieszkowski/socials-daily/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/bartlomiejcieszkowski/socials-daily/releases/tag/v0.2.0
[0.1.0]: https://github.com/bartlomiejcieszkowski/socials-daily/releases/tag/v0.1.0
