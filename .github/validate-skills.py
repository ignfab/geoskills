#!/usr/bin/env python3
"""Validate skill metadata, required files and local Markdown reference targets."""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently accepting the last value."""


def unique_mapping(loader, node):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise ValueError("frontmatter keys must be strings")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def frontmatter_fields(text):
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("missing or unterminated YAML frontmatter")
    fields = yaml.load(match.group(1), Loader=UniqueKeyLoader)
    if not isinstance(fields, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return fields


def without_fenced_code(text):
    return re.sub(r"^(`{3,}|~{3,}).*?^\1[^\n]*$", "", text, flags=re.M | re.S)


def local_targets(path):
    """Read inline Markdown links outside fenced code; ignore external URLs and anchors."""
    text = without_fenced_code(path.read_text(encoding="utf-8"))
    for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
        target = target.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield (path.parent / unquote(parsed.path)).resolve()


def validate(root):
    root = Path(root).resolve()
    errors = []
    skill_root = root / "skills"
    skill_files = sorted(skill_root.glob("**/SKILL.md"))
    if not skill_files:
        errors.append("no skills/**/SKILL.md files found")
    if skill_root.exists():
        for directory in sorted(skill_root.iterdir()):
            if directory.is_dir() and not (directory / "SKILL.md").is_file():
                errors.append(f"skills/{directory.name}: missing SKILL.md")
    for path in skill_files:
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        try:
            fields = frontmatter_fields(text)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"{relative}: {exc}")
            continue
        for field in ("name", "description"):
            value = fields.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{relative}: '{field}' must be a non-empty string")
        name = fields.get("name")
        if isinstance(name, str):
            if name != path.parent.name:
                errors.append(f"{relative}: name '{name}' does not match directory")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
                errors.append(f"{relative}: invalid skill name '{name}'")
        if not (path.parent / "README.md").is_file():
            errors.append(f"{relative}: missing skill README.md")
        headings = set(re.findall(r"^## ([^\r\n]+)", without_fenced_code(text), flags=re.M))
        for heading in ("Prerequisites", "Validate the output"):
            if heading not in headings:
                errors.append(f"{relative}: missing required section '## {heading}'")
        # Walk links from the entrypoint: long references must be discoverable by an agent.
        reachable = set()
        pending = [path.resolve()]
        while pending:
            current = pending.pop()
            if current in reachable:
                continue
            reachable.add(current)
            for target in local_targets(current):
                if target.is_file() and target.suffix == ".md" and target.is_relative_to(path.parent.resolve()):
                    pending.append(target)
        for reference in (path.parent / "references").rglob("*.md"):
            if reference.resolve() not in reachable:
                errors.append(f"{relative}: unlinked reference {reference.name}")
    documents = [*root.glob("*.md"), *skill_root.rglob("*.md"), *(root / "tests").glob("*.md"),
                 *(root / "docs").glob("*.md")]
    for path in sorted(set(documents)):
        for target in local_targets(path):
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: broken local link to {target}")
    return errors, len(skill_files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, count = validate(args.root)
    if errors:
        print("Skill validation failed:\n" + "\n".join(f"  - {error}" for error in errors))
        return 1
    print(f"OK: {count} skill(s); YAML, required files and local links validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
