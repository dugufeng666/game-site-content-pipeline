"""Measured MDX draft gates for copied site content pipelines.

This validator checks article shape, metadata, keyword presence, and obvious
evidence refusal markers. It is not a factuality checker. Human source review
is still required before publishing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
KEYWORDS_PATH = ROOT / "keywords.json"


def _load_allowed_keywords() -> list[str]:
    data = json.loads(KEYWORDS_PATH.read_text())
    return sorted(
        [keyword for group in data["categories"] for keyword in group["keywords"]],
        key=len,
        reverse=True,
    )


def _metadata_and_body(content: str) -> tuple[dict, str] | tuple[None, str]:
    match = re.match(r"^export const metadata\s*=\s*(\{.*?\});?", content, re.S)
    if not match:
        return None, content
    try:
        metadata = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None, content[match.end() :]
    if not isinstance(metadata, dict):
        return None, content[match.end() :]
    return metadata, content[match.end() :]


def validate_draft(content: str):
    if "INSUFFICIENT_EVIDENCE" in content:
        return False, "Insufficient source evidence"

    metadata, body = _metadata_and_body(content)
    if metadata is None:
        return False, "Must begin with JS metadata export containing JSON-compatible metadata"

    issues: list[str] = []
    for key, low, high in (("title", 50, 60), ("description", 150, 155)):
        value = metadata.get(key)
        if not isinstance(value, str) or not low <= len(value) <= high:
            actual = len(value) if isinstance(value, str) else "missing"
            issues.append(f"{key} length {actual}; required {low}-{high} characters")

    words = len(re.findall(r"\b[\w'-]+\b", body))
    headings = len(re.findall(r"^## ", body, re.M))
    tables = len(re.findall(r"^\|\s*:?-{3,}", body, re.M))

    if not 1400 <= words <= 1800:
        issues.append(f"{words} words; required 1400-1800 without padding")
    if not 4 <= headings <= 6:
        issues.append(f"{headings} H2s; required 4-6 including opening and FAQ")
    if not 3 <= tables <= 5:
        issues.append(f"{tables} tables; required 3-5 source-supported tables")
    if re.search(r"^# ", body, re.M):
        issues.append("Unexpected H1")
    if not body.lstrip().startswith("## "):
        issues.append("Body must start with an H2")
    if not all(metadata.get(key) for key in ("category", "date")):
        issues.append("Missing category/date")

    title = str(metadata.get("title", "")).lower()
    description = str(metadata.get("description", "")).lower()
    lower_content = content.lower()
    keyword = next((candidate for candidate in _load_allowed_keywords() if candidate in title), None)
    if not keyword:
        issues.append("Title missing a requested keyword")
    else:
        if keyword not in description:
            issues.append("Description missing the main keyword")
        if lower_content.count(keyword) < 9:
            issues.append("Main keyword must occur at least nine times naturally")
        opening = " ".join(re.findall(r"\b[\w'-]+\b", body.lower())[:120])
        if opening.count(keyword) < 2:
            issues.append("Main keyword must occur twice within the opening 120 words")

    return not issues, "; ".join(issues)
