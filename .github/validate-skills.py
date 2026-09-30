#!/usr/bin/env python3
"""Validate that every skill under skills/ has a well-formed SKILL.md.

Checks, for each skills/**/SKILL.md:
  - a YAML frontmatter block delimited by '---';
  - a non-empty 'name' field that matches the skill directory name;
  - a non-empty 'description' field.

Exits non-zero (listing every problem) if any check fails.
"""

import glob
import os
import re
import sys


def frontmatter_fields(text):
    """Return the top-level 'key: value' pairs of the leading YAML frontmatter."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        pair = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if pair:
            fields[pair.group(1)] = pair.group(2).strip().strip("\"'")
    return fields


def main():
    skill_files = sorted(glob.glob("skills/**/SKILL.md", recursive=True))
    errors = []

    if not skill_files:
        errors.append("no skills/**/SKILL.md files found.")

    for path in skill_files:
        skill_dir = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as handle:
            fields = frontmatter_fields(handle.read())

        if fields is None:
            errors.append(f"{path}: missing or unterminated YAML frontmatter ('---').")
            continue

        name = fields.get("name", "")
        if not name:
            errors.append(f"{path}: frontmatter is missing a non-empty 'name'.")
        elif name != skill_dir:
            errors.append(f"{path}: name '{name}' does not match directory '{skill_dir}'.")

        if not fields.get("description", ""):
            errors.append(f"{path}: frontmatter is missing a non-empty 'description'.")

    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"OK: {len(skill_files)} skill(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
