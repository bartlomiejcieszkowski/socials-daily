"""Write markdown output transformer."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

from .base import Post, Transformer, transformer

log = logging.getLogger(__name__)


@transformer("write_markdown")
class WriteMarkdownTransformer(Transformer):
    """Write posts to daily markdown files."""

    name = "write_markdown"
    passthrough = True

    def transform(self, posts: list[Post]) -> list[Post]:
        """Write markdown files grouped by date."""
        if not posts:
            return posts

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        by_date: dict[str, list[Post]] = {}
        for post in posts:
            date_str = post.date.strftime("%Y-%m-%d")
            by_date.setdefault(date_str, []).append(post)

        for date_str, day_posts in sorted(by_date.items()):
            output_file = output_dir / f"daily-summary-{date_str}.md"
            json_file = output_dir / f"daily-summary-{date_str}.json"

            lines: list[str] = []
            lines.append(f"# Socials Daily Summary — {date_str}")
            lines.append("")

            if not day_posts:
                lines.append("*No new posts today.*")
            else:
                by_account: dict[str, list[Post]] = {}
                for post in day_posts:
                    by_account.setdefault(f"{post.platform}/{post.account}", []).append(post)

                for account_key, account_posts in sorted(by_account.items()):
                    lines.append(f"## {account_key}")
                    lines.append("")
                    for post in sorted(account_posts, key=lambda p: p.date, reverse=True):
                        caption = post.caption
                        if caption:
                            lines.append(f"- {caption} — [{post.link}]({post.link})")
                        else:
                            lines.append(f"- [{post.link}]({post.link})")
                        lines.append("")

            output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            log.info("  Written: %s (%d posts)", output_file.name, len(day_posts))

            # Also write JSON
            json_file.write_text(
                json.dumps(
                    [
                        {
                            "platform": p.platform,
                            "account": p.account,
                            "caption": p.caption,
                            "link": p.link,
                            "date": p.date.isoformat(),
                            "tags": p.tags,
                        }
                        for p in day_posts
                    ],
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            log.info("  Written: %s (%d posts)", json_file.name, len(day_posts))

        return posts  # Pass through unchanged
