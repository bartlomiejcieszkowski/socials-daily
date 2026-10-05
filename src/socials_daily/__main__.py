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

from .scrapers import Post, create_scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")
ACCOUNTS_FILE = Path("accounts.txt")
SEEN_FILE = Path(".seen.json")
POSTS_LIMIT = 10  # recent posts per account


def load_seen() -> set[str]:
    """Load already-seen post permalinks from the seen file."""
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def save_seen(seen: set[str]) -> None:
    """Save seen post permalinks to the seen file."""
    SEEN_FILE.write_text(json.dumps(list(seen), indent=2, ensure_ascii=False), encoding="utf-8")


def load_accounts(path: Path = ACCOUNTS_FILE) -> list[str]:
    """Load account usernames from file, one per line, skipping blanks and comments."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def add_account(username: str, platform: str, path: Path = ACCOUNTS_FILE) -> None:
    """Append a username to the accounts file if not already present."""
    existing = load_accounts(path)
    clean = username.lstrip("@")
    if clean in existing:
        log.info("@%s already in %s", clean, path)
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{clean}\n")
    log.info("Added @%s (%s) to %s", clean, platform, path)


def generate_summary(accounts: list[str], backend: str, api_key: str | None, output_dir: Path = OUTPUT_DIR) -> Path:
    """Fetch posts from all accounts and write a daily summary file."""
    scraper = create_scraper(backend, api_key)
    log.info("Using scraper: %s", scraper.name)

    seen = load_seen()
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_file = output_dir / f"daily-summary-{today}.md"

    all_posts: list[dict] = []
    by_account: dict[str, list[dict]] = defaultdict(list)

    for i, username in enumerate(accounts):
        log.info("[%d/%d] Fetching posts from @%s ...", i + 1, len(accounts), username)
        posts = scraper.fetch_posts(username, limit=POSTS_LIMIT)
        for post in posts:
            if post.link not in seen:
                seen.add(post.link)
                all_posts.append({"account": username, "caption": post.caption, "link": post.link, "date": post.date.isoformat()})
                by_account[username].append({"caption": post.caption, "link": post.link, "date": post.date.isoformat()})
        # Pace between accounts (instaloader needs this, APIs don't but safe to keep)
        time.sleep(3)

    # Write markdown summary
    lines: list[str] = []
    lines.append(f"# Socials Daily Summary — {today}")
    lines.append("")

    if not all_posts:
        lines.append("*No new posts today.*")
    else:
        for account, account_posts in sorted(by_account.items()):
            lines.append(f"## @{account}")
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
    log.info("Summary written to %s (%d new posts from %d accounts, %d total tracked)", output_file, len(all_posts), len(by_account), len(seen))
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Socials Daily Post Summarizer")
    sub = parser.add_subparsers(dest="command")

    # scrape (default)
    scrape_parser = sub.add_parser("scrape", help="Fetch posts from all accounts")
    scrape_parser.add_argument("--backend", choices=["bluesky", "instaloader", "hikerapi", "xpoz"], default="bluesky", help="Scraper backend (default: bluesky)")
    scrape_parser.add_argument("--api-key", default=None, help="API key for paid backends (or set env var)")

    # add
    add_parser = sub.add_parser("add", help="Add an account to the list")
    add_parser.add_argument("username", help="Social handle (with or without @)")
    add_parser.add_argument("--platform", choices=["bluesky", "instagram"], default="bluesky", help="Platform (default: bluesky)")

    args = parser.parse_args()

    if args.command == "add":
        add_account(args.username, platform=args.platform)
    else:
        # default: scrape
        accounts = load_accounts()
        if not accounts:
            log.error("No accounts found in %s", ACCOUNTS_FILE)
            sys.exit(1)

        log.info("Scraping %d accounts...", len(accounts))
        output = generate_summary(accounts, backend=args.backend, api_key=args.api_key)
        print(f"\nDone! Summary: {output}")


if __name__ == "__main__":
    main()
