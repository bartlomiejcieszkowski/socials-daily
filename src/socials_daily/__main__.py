"""Fetch recent posts from public social media accounts and generate a daily summary."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .providers import _PROVIDER_BACKENDS, create_provider  # type: ignore[import-not-found]
from .scrapers import create_scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")
ACCOUNTS_FILE = Path("accounts.json")
SEEN_FILE = Path(".seen.json")
POSTS_LIMIT = 10  # default posts per account

SUPPORTED_PLATFORMS = ["bluesky", "instagram", "reddit", "rss", "youtube"]


def load_seen() -> set[str]:
    """Load already-seen post permalinks from the seen file."""
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def save_seen(seen: set[str]) -> None:
    """Save seen post permalinks to the seen file."""
    SEEN_FILE.write_text(json.dumps(list(seen), indent=2, ensure_ascii=False), encoding="utf-8")


def load_accounts(path: Path = ACCOUNTS_FILE) -> dict[str, dict]:
    """Load accounts grouped by platform.

    Returns dict like:
    {
        "bluesky": {
            "backend": "bluesky",
            "accounts": [{"handle": "bsky.app"}, {"handle": "atmos.bsky.social", "limit": 20}]
        },
        "instagram": {
            "accounts": [{"handle": "natgeo"}]
        }
    }
    """
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    # Handle legacy flat list format
    if isinstance(data, list):
        result: dict[str, dict] = {}
        for item in data:
            if isinstance(item, dict):
                platform = item.get("platform", "bluesky")
                entry = {"handle": item["handle"]}
                if "limit" in item:
                    entry["limit"] = item["limit"]
            else:
                platform = "bluesky"
                entry = {"handle": str(item)}
            if platform not in result:
                result[platform] = {"accounts": []}
            result[platform]["accounts"].append(entry)
        return result

    # Handle new platform→object format
    result: dict[str, dict] = {}
    for platform, config in data.items():
        if isinstance(config, dict):
            result[platform] = config
        else:
            result[platform] = {"accounts": config}
    return result


def save_accounts(accounts: dict[str, dict], path: Path = ACCOUNTS_FILE) -> None:
    """Save accounts grouped by platform."""
    path.write_text(json.dumps(accounts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_account(
    handle: str,
    platform: str,
    path: Path = ACCOUNTS_FILE,
    limit: int | None = None,
    backend: str | None = None,
) -> None:
    """Add an account to the accounts file under the specified platform."""
    accounts = load_accounts(path)

    if platform not in accounts:
        accounts[platform] = {"accounts": []}

    clean = handle.lstrip("@")

    for entry in accounts[platform]["accounts"]:
        if entry.get("handle") == clean:
            log.info("%s/%s already in %s", platform, clean, path)
            return

    entry: dict = {"handle": clean}
    if limit is not None:
        entry["limit"] = limit

    accounts[platform]["accounts"].append(entry)

    # Update backend if specified
    if backend is not None:
        accounts[platform]["backend"] = backend

    save_accounts(accounts, path)
    log.info(
        "Added %s/%s (limit=%s, backend=%s) to %s",
        platform, clean, limit or POSTS_LIMIT, backend or "default", path,
    )


def generate_summary(
    accounts: dict[str, dict],
    api_key: str | None,
    cli_backend: str | None,
    since: datetime,
    till: datetime,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    """Fetch posts from all accounts (grouped by platform) and write a daily summary."""
    seen = load_seen()
    output_dir.mkdir(parents=True, exist_ok=True)
    today = since.strftime("%Y-%m-%d")
    output_file = output_dir / f"daily-summary-{today}.md"

    all_posts: list[dict] = []
    by_account: dict[str, list[dict]] = defaultdict(list)
    total_accounts = sum(len(v.get("accounts", [])) for v in accounts.values())
    index = 0

    for platform, platform_config in accounts.items():
        platform_accounts = platform_config.get("accounts", [])

        # Resolve scraper backend: CLI flag > platform config > default mapping
        scraper_backend = cli_backend or platform_config.get("backend") or platform

        for account in platform_accounts:
            handle = account["handle"]
            limit = account.get("limit", POSTS_LIMIT)
            index += 1

            log.info("[%d/%d] Fetching posts from %s/%s ...", index, total_accounts, platform, handle)
            scraper = create_scraper(scraper_backend, api_key)
            log.info("  Using %s: %s (resolved from %s)", "provider" if scraper_backend in _PROVIDER_BACKENDS else "scraper", scraper.name, scraper_backend)

            try:
                posts = scraper.fetch_posts(handle, limit=limit, since=since, till=till)
            except Exception as exc:
                log.warning("  Failed to fetch from %s/%s: %s", platform, handle, exc)
                posts = []

            for post in posts:
                if post.link not in seen:
                    seen.add(post.link)
                    all_posts.append({
                        "platform": platform,
                        "account": handle,
                        "caption": post.caption,
                        "link": post.link,
                        "date": post.date.isoformat(),
                    })
                    by_account[f"{platform}/{handle}"].append({
                        "caption": post.caption,
                        "link": post.link,
                        "date": post.date.isoformat(),
                    })
            # Pace between accounts (instaloader needs this, APIs don't but safe to keep)
            time.sleep(3)

    # Write markdown summary
    lines: list[str] = []
    lines.append(f"# Socials Daily Summary — {today}")
    lines.append("")

    if not all_posts:
        lines.append("*No new posts today.*")
    else:
        for account_key, account_posts in sorted(by_account.items()):
            lines.append(f"## {account_key}")
            lines.append("")
            for post in account_posts:
                caption = post["caption"]
                if caption:
                    lines.append(f"- {caption} — [{post['link']}]({post['link']})")
                else:
                    lines.append(f"- _No caption_ — [{post['link']}]({post['link']})")
            lines.append("")

    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Also write a JSON version for programmatic use
    json_file = output_dir / f"daily-summary-{today}.json"
    json_file.write_text(json.dumps(all_posts, indent=2, ensure_ascii=False), encoding="utf-8")

    save_seen(seen)
    log.info(
        "Summary written to %s (%d new posts from %d accounts, %d total tracked)",
        output_file, len(all_posts), len(by_account), len(seen),
    )
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Socials Daily Post Summarizer")
    sub = parser.add_subparsers(dest="command")

    # scrape (default)
    scrape_parser = sub.add_parser("scrape", help="Fetch posts from all accounts")
    scrape_parser.add_argument("--api-key", default=None, help="API key for paid backends (or set env var)")
    scrape_parser.add_argument(
        "--backend",
        default=None,
        help="Override scraper backend for all platforms (takes precedence over platform config)",
    )
    scrape_parser.add_argument(
        "--since",
        default=None,
        help="Start date for scraping (YYYY-MM-DD, inclusive). Default: today.",
    )
    scrape_parser.add_argument(
        "--till",
        default=None,
        help="End date for scraping (YYYY-MM-DD, inclusive). Default: today.",
    )
    scrape_parser.add_argument(
        "--day",
        default=None,
        help="Scrape a specific day (YYYY-MM-DD). Overrides --since and --till.",
    )

    # add
    add_parser = sub.add_parser("add", help="Add an account to the list")
    add_parser.add_argument("handle", help="Social handle (with or without @)")
    add_parser.add_argument("--platform", choices=SUPPORTED_PLATFORMS, default="bluesky", help="Platform (default: bluesky)")
    add_parser.add_argument("--limit", type=int, default=None, help="Post limit for this account (default: 10)")
    add_parser.add_argument("--backend", default=None, help="Scraper backend for this platform (overrides default)")

    args = parser.parse_args()

    if args.command == "add":
        add_account(args.handle, platform=args.platform, limit=args.limit, backend=args.backend)
    else:
        # default: scrape
        accounts = load_accounts()
        if not accounts:
            log.error("No accounts found in %s", ACCOUNTS_FILE)
            sys.exit(1)

        platform_count = len(accounts)
        total = sum(len(v.get("accounts", [])) for v in accounts.values())
        log.info("Found %d accounts across %d platforms", total, platform_count)
        for platform, config in accounts.items():
            backend = config.get("backend", platform)
            log.info("  %s: %d account(s) [backend: %s]", platform, len(config.get("accounts", [])), backend)

        # Parse date arguments
        if args.day:
            day = datetime.strptime(args.day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            since = day
            till = day
        else:
            since = datetime.now(timezone.utc)
            till = datetime.now(timezone.utc)
            if args.since:
                since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if args.till:
                till = datetime.strptime(args.till, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        output = generate_summary(
            accounts,
            api_key=args.api_key,
            cli_backend=args.backend,
            since=since,
            till=till,
        )
        log.info("Done! Summary: %s", output)


if __name__ == "__main__":
    main()
