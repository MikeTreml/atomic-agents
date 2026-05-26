#!/usr/bin/env python3
"""Gather a machine-readable index of community resources.

Companion to docs/guides/community-catalog.md. Hits the GitHub REST API to
enumerate repositories that look like:

  - Claude Code skills (topic:claude-code-skill, topic:claude-skill, ...)
  - Atomic Agents tools (topic:atomic-agents, atomic-agents in:readme ...)
  - Claude Code plugin marketplaces (topic:claude-code-plugin, ...)

Writes docs/guides/community-catalog.json next to the markdown. The markdown
file stays hand-curated; this JSON is the raw discovery feed you can grep,
diff over time, or use to surface new candidates for the curated list.

Usage:
    GITHUB_TOKEN=ghp_xxx python scripts/gather_community_catalog.py
    python scripts/gather_community_catalog.py --no-token   # slower, anonymous

Network requirement: api.github.com must be reachable from the runner. Many
sandboxed cloud environments block it — run locally or in CI.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "guides" / "community-catalog.json"

GITHUB_API = "https://api.github.com"

CLAUDE_SKILL_QUERIES = [
    "topic:claude-code-skill",
    "topic:claude-skill",
    "topic:claude-code-skills",
    "topic:awesome-claude-code",
]
CLAUDE_PLUGIN_QUERIES = [
    "topic:claude-code-plugin",
    "topic:claude-plugin",
    "topic:claude-plugins",
    "topic:claude-code-marketplace",
]
ATOMIC_TOOL_QUERIES = [
    "topic:atomic-agents",
    "atomic-agents in:readme language:Python",
    "from-atomic_agents in:file language:Python",
]


@dataclass
class RepoEntry:
    name: str
    url: str
    description: str | None
    stars: int
    forks: int
    pushed_at: str | None
    language: str | None
    license: str | None
    topics: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "RepoEntry":
        return cls(
            name=raw["full_name"],
            url=raw["html_url"],
            description=raw.get("description"),
            stars=raw.get("stargazers_count", 0),
            forks=raw.get("forks_count", 0),
            pushed_at=raw.get("pushed_at"),
            language=raw.get("language"),
            license=(raw.get("license") or {}).get("spdx_id"),
            topics=raw.get("topics") or [],
        )


def _request(path: str, token: str | None) -> Any:
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "atomic-agents-catalog-gatherer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                # Polite rate-limit handling: sleep before exhausting the bucket.
                remaining = resp.headers.get("X-RateLimit-Remaining")
                if remaining is not None and int(remaining) < 3:
                    reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
                    wait = max(reset - int(time.time()), 0) + 1
                    print(
                        f"[rate-limit] {remaining} requests left, sleeping {wait}s",
                        file=sys.stderr,
                    )
                    time.sleep(min(wait, 70))
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace") if e.fp else ""
            if e.code == 403 and "rate limit" in body.lower():
                if not token:
                    print(
                        "[error] anonymous rate limit hit; set GITHUB_TOKEN",
                        file=sys.stderr,
                    )
                    raise
                time.sleep(2 ** attempt)
                continue
            if e.code in (502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError(f"Failed after retries: {url}")


def search_repos(query: str, token: str | None, max_results: int = 200) -> list[RepoEntry]:
    """Page through GitHub's repo search. Caps out at the API's 1000-result limit."""
    entries: list[RepoEntry] = []
    page = 1
    while len(entries) < max_results:
        params = urlencode(
            {"q": query, "sort": "stars", "order": "desc", "per_page": 100, "page": page}
        )
        data = _request(f"/search/repositories?{params}", token)
        items = data.get("items") or []
        for item in items:
            entries.append(RepoEntry.from_api(item))
            if len(entries) >= max_results:
                break
        if len(items) < 100:
            break
        page += 1
        if page > 10:
            break
    return entries


def gather(token: str | None) -> dict[str, Any]:
    queries_by_cat = {
        "claude_skills": CLAUDE_SKILL_QUERIES,
        "atomic_tools": ATOMIC_TOOL_QUERIES,
        "claude_plugins": CLAUDE_PLUGIN_QUERIES,
    }
    by_category: dict[str, list[RepoEntry]] = {cat: [] for cat in queries_by_cat}

    for cat, queries in queries_by_cat.items():
        seen: set[str] = set()
        for q in queries:
            print(f"[{cat}] query: {q}", file=sys.stderr)
            for entry in search_repos(q, token):
                if entry.name in seen:
                    continue
                seen.add(entry.name)
                by_category[cat].append(entry)
        by_category[cat].sort(key=lambda e: e.stars, reverse=True)

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "queries": queries_by_cat,
        "categories": {
            cat: [asdict(e) for e in entries] for cat, entries in by_category.items()
        },
        "total": sum(len(v) for v in by_category.values()),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--no-token",
        action="store_true",
        help="Skip token lookup and run anonymously (10 req/min for search).",
    )
    args = parser.parse_args(argv)

    token = (
        None
        if args.no_token
        else os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    )
    if not token:
        print(
            "[warn] No GITHUB_TOKEN/GH_TOKEN — search rate limit is 10 requests/minute.",
            file=sys.stderr,
        )

    payload = gather(token)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {payload['total']} entries across {len(payload['categories'])} categories → {args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
