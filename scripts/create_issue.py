#!/usr/bin/env python3
"""
Create GitHub issues from a structured markdown issues file.

Expected format (see docs/issues/YYYY-MM-DD-*.md):
  # Title — context header
  ## Issue N — Issue title here
  **Severity:** Low | Medium | High | Critical
  **File:** path/to/file
  [body markdown...]

Usage:
  python scripts/create_issues.py docs/issues/2026-05-20-r3-open-issues.md
  python scripts/create_issues.py docs/issues/2026-05-20-r3-open-issues.md --dry-run
  python scripts/create_issues.py docs/issues/2026-05-20-r3-open-issues.md --label bug
"""

import argparse
import re
import subprocess
import sys
import tempfile
import os

SEVERITY_TO_LABEL = {
    "low":      "priority: low",
    "medium":   "priority: medium",
    "high":     "priority: high",
    "critical": "priority: critical",
}


def parse_issues(filepath: str) -> list[dict]:
    with open(filepath) as f:
        content = f.read()

    # H1 supplies optional milestone context shown in issue body header
    h1 = re.search(r"^# (.+)$", content, re.MULTILINE)
    context = h1.group(1).strip() if h1 else ""

    # Split on "## Issue N — " markers
    parts = re.split(r"^## Issue \d+ — ", content, flags=re.MULTILINE)

    issues = []
    for part in parts[1:]:
        lines = part.strip().splitlines()
        title = lines[0].strip()
        raw_body = "\n".join(lines[1:]).strip()

        sev_match = re.search(r"\*\*Severity:\*\*\s*(\w+)", raw_body, re.IGNORECASE)
        severity = sev_match.group(1).lower() if sev_match else "low"

        file_match = re.search(r"\*\*File:\*\*\s*`?([^`\n]+)`?", raw_body)
        file_ref = file_match.group(1).strip() if file_match else ""

        # Prepend context breadcrumb so issues are self-contained on GitHub
        body_header = f"_From [{context}]_\n\n" if context else ""
        body = body_header + raw_body

        issues.append({
            "title": title,
            "body": body,
            "severity": severity,
            "file": file_ref,
        })

    return issues


def existing_labels() -> set[str]:
    result = subprocess.run(
        ["gh", "label", "list", "--json", "name", "-q", ".[].name"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return set()
    return {l.strip() for l in result.stdout.splitlines() if l.strip()}


def ensure_labels(needed: set[str], dry_run: bool) -> None:
    have = existing_labels()
    for label in needed - have:
        color = {
            "priority: low":      "0075ca",
            "priority: medium":   "e4e669",
            "priority: high":     "d93f0b",
            "priority: critical": "b60205",
        }.get(label, "ededed")
        if dry_run:
            print(f"  [dry-run] would create label: {label}")
            continue
        subprocess.run(
            ["gh", "label", "create", label, "--color", color, "--force"],
            capture_output=True,
        )


def create_issue(issue: dict, extra_labels: list[str], dry_run: bool) -> None:
    title = issue["title"]
    body = issue["body"]
    severity = issue["severity"]

    labels = [SEVERITY_TO_LABEL[severity]] + extra_labels

    print(f"\n  → {title}")
    print(f"    severity={severity}  labels={labels}")

    if dry_run:
        print("    [dry-run] skipping gh issue create")
        return

    # Write body to temp file — avoids shell quoting issues with long markdown
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
        tmp.write(body)
        tmp_path = tmp.name

    try:
        cmd = ["gh", "issue", "create", "--title", title, "--body-file", tmp_path]
        for label in labels:
            cmd += ["--label", label]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"    ✓ {result.stdout.strip()}")
        else:
            print(f"    ✗ {result.stderr.strip()}", file=sys.stderr)
    finally:
        os.unlink(tmp_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create GitHub issues from a structured markdown file."
    )
    parser.add_argument("file", help="Path to the markdown issues file")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without creating")
    parser.add_argument("--label", action="append", default=[], metavar="LABEL",
                        help="Extra label(s) to attach to every issue")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        sys.exit(f"File not found: {args.file}")

    issues = parse_issues(args.file)
    if not issues:
        sys.exit("No issues found. Check markdown format (needs '## Issue N — Title' headers).")

    print(f"Parsed {len(issues)} issue(s) from {args.file}")

    # Collect all labels we'll need and ensure they exist
    needed_labels = {SEVERITY_TO_LABEL[i["severity"]] for i in issues}
    needed_labels.update(args.label)
    ensure_labels(needed_labels, dry_run=args.dry_run)

    for issue in issues:
        create_issue(issue, extra_labels=args.label, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
