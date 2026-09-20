"""Audit generated MDX drafts for measurable template violations.

This script never equates template compliance with factual correctness.
Use it to catch weak draft shape before editorial review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent


def _load_keyword_mapping() -> dict[str, str]:
    keywords = json.loads((ROOT / "keywords.json").read_text())
    mapping = {}
    for category in keywords["categories"]:
        for keyword in category["keywords"]:
            mapping[keyword.replace(" ", "-")] = keyword
    return mapping


def _metadata_and_body(text: str) -> tuple[dict, str]:
    match = re.match(r"export const metadata\s*=\s*(\{.*?\});?", text, re.S)
    if not match:
        raise ValueError("Missing metadata")
    metadata = json.loads(match.group(1))
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be an object")
    return metadata, text[match.end() :]


def audit_file(path: Path, keyword: str | None) -> dict:
    text = path.read_text()
    try:
        metadata, body = _metadata_and_body(text)
    except (ValueError, json.JSONDecodeError):
        return {"file": str(path), "issues": ["Invalid JSON-compatible metadata"]}

    issues: list[str] = []
    title = metadata.get("title", "")
    description = metadata.get("description", "")
    words = len(re.findall(r"\b[\w'-]+\b", body))
    headings = len(re.findall(r"^## ", body, re.M))
    tables = len(re.findall(r"^\|\s*:?-{3,}", body, re.M))
    mentions = text.lower().count(keyword) if keyword else 0

    if not 50 <= len(title) <= 60:
        issues.append("Title length")
    if not 150 <= len(description) <= 155:
        issues.append("Description length")
    if keyword:
        if keyword not in title.lower():
            issues.append("Keyword missing from title")
        if keyword not in description.lower():
            issues.append("Keyword missing from description")
        if mentions < 9:
            issues.append("Fewer than 9 keyword mentions")
    else:
        issues.append("No keyword mapping for filename")
    if not 4 <= headings <= 6:
        issues.append("H2 count")
    if not 3 <= tables <= 5:
        issues.append("Table count")
    if re.search(r"^# ", body, re.M):
        issues.append("Unexpected H1")
    if not 1400 <= words <= 1800:
        issues.append("Word count outside approximate target")
    if "INSUFFICIENT_EVIDENCE" in text:
        issues.append("Evidence refusal saved as article")

    return {
        "file": str(path),
        "title_chars": len(title),
        "description_chars": len(description),
        "words": words,
        "keyword_mentions": mentions,
        "h2_count": headings,
        "table_count": tables,
        "issues": issues,
        "editorial_status": "requires source review",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--articles-dir", type=Path, required=True)
    args = parser.parse_args()

    mapping = _load_keyword_mapping()
    results = []
    for path in sorted(args.articles_dir.resolve().rglob("*.mdx")):
        keyword = mapping.get(path.stem)
        results.append(audit_file(path, keyword))

    print(json.dumps({"draft_count": len(results), "articles": results}, indent=2))


if __name__ == "__main__":
    main()
