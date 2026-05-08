#!/usr/bin/env python3
"""Cross-repo promo block sync from Productions Stars list (Spec B auto-gen).

Fetches Productions Stars list (14 public repos), generates a markdown
`<details>`-collapsed table, and either prints diffs (--dry-run) or
opens PRs in each repo (live mode).

Block is delimited by:
    <!-- BEGIN: AUTO-GENERATED-CROSS-PROMO -->
    ...
    <!-- END: AUTO-GENERATED-CROSS-PROMO -->

Usage:
    python promo_sync.py --dry-run                  # show 14 diffs, no PRs
    python promo_sync.py                            # open PRs (default)
    python promo_sync.py --repos=skret,wet-mcp      # subset
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import GhClient, GhError  # type: ignore[import-not-found]


PROMO_BEGIN = "<!-- BEGIN: AUTO-GENERATED-CROSS-PROMO -->"
PROMO_END = "<!-- END: AUTO-GENERATED-CROSS-PROMO -->"


_PRODUCTIONS_QUERY = """
query {
  user(login: "n24q02m") {
    lists(first: 10) {
      nodes {
        name
        items(first: 100) {
          nodes {
            ... on Repository {
              nameWithOwner
              description
              isPrivate
              isArchived
              repositoryTopics(first: 20) {
                nodes { topic { name } }
              }
            }
          }
        }
      }
    }
  }
}
"""


def fetch_productions_public(gh: GhClient) -> list[dict]:
    data = gh.graphql(_PRODUCTIONS_QUERY)
    lists = data["data"]["user"]["lists"]["nodes"]
    productions = next((lst for lst in lists if lst["name"] == "Productions"), None)
    if not productions:
        raise RuntimeError("Productions Stars list not found")
    repos: list[dict] = []
    for item in productions["items"]["nodes"]:
        if not item or item.get("isPrivate") or item.get("isArchived"):
            continue
        topics = [t["topic"]["name"] for t in (item.get("repositoryTopics") or {}).get("nodes", [])]
        repos.append({
            "name_with_owner": item["nameWithOwner"],
            "description": (item.get("description") or "").strip(),
            "topics": topics,
        })
    return repos


def categorize_tag(name_with_owner: str, topics: list[str]) -> str:
    name = name_with_owner.split("/", 1)[1].lower()
    topics_lower = [t.lower() for t in topics]

    if "marketplace" in topics_lower or name == "claude-plugins":
        return "Marketplace"
    if "mcp" in topics_lower or "mcp-server" in topics_lower or name.endswith("-mcp"):
        return "MCP"
    if "cli" in topics_lower:
        return "CLI"
    if "library" in topics_lower or name.endswith(("-core", "-embed", "-lib")):
        return "Library"
    return "Tooling"


def render_promo_block(repos: list[dict]) -> str:
    rows = []
    for r in sorted(repos, key=lambda x: x["name_with_owner"].split("/")[1].lower()):
        owner_name = r["name_with_owner"]
        name = owner_name.split("/", 1)[1]
        url = f"https://github.com/{owner_name}"
        tagline = (r["description"] or "—").replace("|", "\\|")
        if len(tagline) > 80:
            tagline = tagline[:77] + "..."
        tag = categorize_tag(owner_name, r["topics"])
        rows.append(f"| [{name}]({url}) | {tagline} | {tag} |")

    lines = [
        PROMO_BEGIN,
        "<details>",
        "  <summary><strong>Sister projects from n24q02m</strong> (click to expand)</summary>",
        "",
        "| Project | Tagline | Tag |",
        "|---|---|---|",
        *rows,
        "",
        "</details>",
        PROMO_END,
    ]
    return "\n".join(lines)


def splice_block(readme_text: str, new_block: str) -> str:
    """Replace existing block (between delimiters) or insert after badge row.

    Returns updated text. Idempotent: if existing block content matches new_block,
    the function returns the input unchanged (modulo trailing newline normalization).
    """
    if PROMO_BEGIN in readme_text and PROMO_END in readme_text:
        pattern = re.compile(
            re.escape(PROMO_BEGIN) + r".*?" + re.escape(PROMO_END),
            re.DOTALL,
        )
        return pattern.sub(new_block, readme_text)

    # Insert new block: find the last consecutive line containing a shield badge,
    # then insert after that line block.
    lines = readme_text.splitlines()
    last_badge_idx = -1
    for i, ln in enumerate(lines):
        if "https://img.shields.io/" in ln or "https://github.com/n24q02m/" in ln and "/actions/workflows" in ln:
            last_badge_idx = i

    if last_badge_idx >= 0:
        # Find the closing of the badge block (next blank line or non-badge)
        insert_at = last_badge_idx + 1
        while insert_at < len(lines) and (
            "https://img.shields.io/" in lines[insert_at]
            or lines[insert_at].strip().startswith(("</p>", "<p"))
        ):
            insert_at += 1
        new_lines = lines[:insert_at] + ["", new_block, ""] + lines[insert_at:]
    else:
        # Fallback: insert after first heading line, or at top
        insert_at = 0
        for i, ln in enumerate(lines):
            if ln.startswith("# ") or "<h1" in ln.lower():
                insert_at = i + 1
                break
        new_lines = lines[:insert_at] + ["", new_block, ""] + lines[insert_at:]

    return "\n".join(new_lines)


def get_readme(gh: GhClient, repo: str) -> tuple[str, str]:
    """Return (content_decoded, sha) for repo's README.md on default branch."""
    data = gh.api(f"repos/{repo}/contents/README.md")
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response for {repo}/README.md")
    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    sha = data["sha"]
    return content, sha


def open_pr_with_readme_update(
    gh: GhClient, repo: str, new_readme: str, current_sha: str
) -> str:
    """Create a branch, commit updated README, open PR. Returns PR URL."""
    branch = "auto/promo-sync"
    # Get default branch SHA
    info = gh.repo_view(repo, ["defaultBranchRef"])
    default_branch = (info.get("defaultBranchRef") or {}).get("name", "main")
    ref_data = gh.api(f"repos/{repo}/git/ref/heads/{default_branch}")
    base_sha = ref_data["object"]["sha"]

    # Create branch (or update if exists)
    try:
        gh.api(
            f"repos/{repo}/git/refs",
            method="POST",
            fields={"ref": f"refs/heads/{branch}", "sha": base_sha},
        )
    except GhError as e:
        if "Reference already exists" not in str(e):
            raise

    # Update README on branch
    encoded = base64.b64encode(new_readme.encode("utf-8")).decode("ascii")
    gh.api(
        f"repos/{repo}/contents/README.md",
        method="PUT",
        fields={
            "message": "feat: sync cross-promo section",
            "content": encoded,
            "sha": current_sha,
            "branch": branch,
        },
    )

    # Open PR
    pr = gh.api(
        f"repos/{repo}/pulls",
        method="POST",
        fields={
            "title": "feat: sync cross-promo section (auto-generated)",
            "head": branch,
            "base": default_branch,
            "body": (
                "Automated sync of `<!-- BEGIN/END: AUTO-GENERATED-CROSS-PROMO -->` block "
                "from Productions Stars list. Generated by `scripts/repo-bootstrap/promo_sync.py` "
                "in n24q02m/n24q02m profile repo.\n\n"
                "Reviewer: do not edit content inside delimiters — next sync reverts."
            ),
        },
    )
    return pr["html_url"] if isinstance(pr, dict) else "(unknown)"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cross-repo promo block sync")
    p.add_argument("--dry-run", action="store_true", help="Print diffs only, no PRs")
    p.add_argument(
        "--repos",
        help="Comma-separated subset of repo names (default: all 14 Productions public)",
    )
    return p.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    gh = GhClient()

    print(f"Fetching Productions Stars list...", file=sys.stderr)
    try:
        repos = fetch_productions_public(gh)
    except (GhError, RuntimeError) as e:
        print(f"ERROR fetching repos: {e}", file=sys.stderr)
        return 2

    if args.repos:
        wanted = {n.strip() for n in args.repos.split(",")}
        repos = [r for r in repos if r["name_with_owner"].split("/", 1)[1] in wanted]
        if not repos:
            print(f"No repos matched filter {wanted}", file=sys.stderr)
            return 2

    print(f"Targeting {len(repos)} repos", file=sys.stderr)
    block = render_promo_block(repos)
    print(f"\nGenerated block ({len(block)} chars):", file=sys.stderr)
    print(block, file=sys.stderr)
    print("\n" + "=" * 80 + "\n", file=sys.stderr)

    failures = 0
    for r in repos:
        repo_name = r["name_with_owner"]
        try:
            current, sha = get_readme(gh, repo_name)
        except (GhError, RuntimeError) as e:
            print(f"  [{repo_name}] FAIL — could not fetch README: {e}", file=sys.stderr)
            failures += 1
            continue
        new = splice_block(current, block)
        if normalize_eol(current) == normalize_eol(new):
            print(f"  [{repo_name}] no diff (already in sync)", file=sys.stderr)
            continue
        if args.dry_run:
            print(f"  [{repo_name}] WOULD UPDATE ({len(new) - len(current):+d} chars)", file=sys.stderr)
            continue
        try:
            pr_url = open_pr_with_readme_update(gh, repo_name, new, sha)
            print(f"  [{repo_name}] PR opened: {pr_url}", file=sys.stderr)
        except GhError as e:
            print(f"  [{repo_name}] FAIL — PR creation: {e}", file=sys.stderr)
            failures += 1

    print(f"\nDone. Failures: {failures}", file=sys.stderr)
    return 1 if failures > 0 else 0


def normalize_eol(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip() + "\n"


if __name__ == "__main__":
    sys.exit(main())
