#!/usr/bin/env python3
"""Validate every Agent Skill in this repository.

Checks the agentskills.io requirements that matter for this repo:

  * ``SKILL.md`` lives in a directory named after the skill
  * YAML frontmatter is present, delimited, and contains name/description
  * the name is kebab-case, <= 64 chars, and matches the directory
  * the description is 1-1024 chars
  * the body is non-empty and <= 500 lines
  * the standard sections are present

Usage:
    python3 scripts/validate_skills.py [repo-root]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_SECTIONS = (
    "## Overview",
    "## When to use",
    "## Gotchas",
    "## Checklist",
    "## Related skills",
)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse the small YAML subset used by these skills, without PyYAML."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^(name|description):\s*(.+?)\s*$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return fields


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    skills = sorted(root.glob("*/*/SKILL.md"))
    errors: list[str] = []

    for path in skills:
        text = path.read_text(encoding="utf-8")
        fields = parse_frontmatter(text)
        label = f"{path.parent.parent.name}/{path.parent.name}"

        if fields is None:
            errors.append(f"{label}: missing or unterminated frontmatter")
            continue
        name = fields.get("name", "")
        description = fields.get("description", "")
        body = text.split("\n---\n", 1)[1].lstrip("\n")

        if not name:
            errors.append(f"{label}: missing name")
        elif len(name) > 64:
            errors.append(f"{label}: name exceeds 64 chars")
        elif not NAME_RE.match(name):
            errors.append(f"{label}: name is not kebab-case: {name!r}")
        elif name != path.parent.name:
            errors.append(f"{label}: name {name!r} does not match directory")

        if not description:
            errors.append(f"{label}: missing description")
        elif not 1 <= len(description) <= 1024:
            errors.append(f"{label}: description length {len(description)} not in 1..1024")
        elif "\n" in description:
            errors.append(f"{label}: description must be a single line")

        lines = body.count("\n") + 1
        if not body.strip():
            errors.append(f"{label}: empty body")
        elif lines > 500:
            errors.append(f"{label}: body is {lines} lines (limit 500)")

        for section in REQUIRED_SECTIONS:
            if section not in body:
                errors.append(f"{label}: missing section {section!r}")

        print(f"OK  {label:58} {lines:4d} lines  {len(description):4d} desc")

    print(f"\n{len(skills)} skills, {len(errors)} errors")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
