# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] — 2026-10-07

### Added
- Test suite with pytest — 53 tests covering config, accounts, deduplication, scrapers, providers, and summary generation

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
- Bartlomiej Cieszkowski

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
- Bartlomiej Cieszkowski

---

## [0.3.0] — Planned

- [ ] Improve error handling and logging
- [ ] Add more social platforms (TikTok, X/Twitter, etc.)
- [ ] Add `--output-dir` and `--format` CLI flags
- [ ] Add `console_scripts` entry point (`socials-daily` command)

[Unreleased]: https://github.com/bartlomiejcieszkowski/socials-daily/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/bartlomiejcieszkowski/socials-daily/releases/tag/v0.2.0
[0.1.0]: https://github.com/bartlomiejcieszkowski/socials-daily/releases/tag/v0.1.0
