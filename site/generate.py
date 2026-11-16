#!/usr/bin/env python3
"""Generate the Hugo content of the geoskills site from the repository Markdown.

The site mirrors the repository: one section per family, one per skill (its README), with
the skill's SKILL.md and references as child pages, plus the documentation of docs/. The
Markdown is kept as written. Links between published pages become Hugo ``relref``
shortcodes, which Hugo checks at build time; links to any other repository file (scripts,
tests, CLAUDE.md) become GitHub URLs.

The generator also writes two machine-readable entry points:

- ``llms.txt``, the llms.txt index of the skills and guides;
- ``.well-known/agent-skills/index.json`` (Agent Skills Discovery v0.2.0) with one zip
  archive per skill, so that ``npx skills add <site URL>`` installs from the site.

Usage: python3 site/generate.py [--out site/generated] [--base-url URL]
"""

import argparse
from dataclasses import dataclass, field
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import sys
import zipfile
from urllib.parse import quote, unquote, urlsplit

import yaml

REPO = Path(__file__).resolve().parents[1]
GITHUB = "https://github.com/ignfab/geoskills"
RAW = "https://raw.githubusercontent.com/ignfab/geoskills/main"
DEFAULT_BASE_URL = "https://ignfab.github.io/geoskills/"
DISCOVERY_SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
WELL_KNOWN = ".well-known/agent-skills"
FR_SECTION = "Résumé (FR)"
# Root README sections left out of the English home page.
HOME_EXCLUDED = (FR_SECTION, "Contributing", "License")
SUMMARY_LENGTH = 240
# README paragraphs that link to the site itself (as an autolink) are left out of the site.
SELF_LINK = f"<{DEFAULT_BASE_URL}"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)
ARCHIVE_EXCLUDED_DIRS = {"__pycache__"}

FENCE = re.compile(r"^(`{3,}|~{3,}).*?^\1[^\n]*$", re.M | re.S)
INLINE_CODE = re.compile(r"(`+)(?:(?!\1)[^\n]|\n(?!\n))+?\1")
LINK = re.compile(r"(\[[^\]]*\]\()([^\s)]+)(\))")
RELREF = re.compile(r'\{\{< relref "([^"#]*)(#[^"]*)?" >\}\}')
SHORTCODE = re.compile(r"\{\{[<%]")
H1 = re.compile(r"\A\s*# (.+?)\s*\n")
H2 = re.compile(r"^## (.+?)\s*$", re.M)


class GenerationError(Exception):
    """The repository Markdown cannot be published as is."""


def load_validator(repo=REPO):
    """Reuse the frontmatter parser and FAMILIES list of .github/validate-skills.py."""
    path = repo / ".github" / "validate-skills.py"
    spec = importlib.util.spec_from_file_location("validate_skills", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class Page:
    source: str  # repository path, e.g. skills/2-access/README.md
    target: str  # content path, e.g. shared/skills/2-access/_index.md
    title: str
    body: str
    weight: int = 0
    description: str = ""
    summary: str = ""


@dataclass
class Skill:
    family: str
    name: str
    description: str
    weight: int

    @property
    def path(self):
        return f"skills/{self.family}/{self.name}"


@dataclass
class Family:
    folder: str
    title: str
    weight: int
    skills: list = field(default_factory=list)


# --- Markdown helpers -------------------------------------------------------------------


def split_title(text, source):
    """Return the first-level heading and the text that follows it."""
    match = H1.match(text)
    if not match:
        raise GenerationError(f"{source}: no first-level heading to use as the title")
    return match.group(1).strip(), text[match.end():].lstrip("\n")


def sections(text):
    """Split Markdown at second-level headings: [(heading or None, block), ...]."""
    code = [(m.start(), m.end()) for m in FENCE.finditer(text)]
    starts = [m for m in H2.finditer(text) if not any(a <= m.start() < b for a, b in code)]
    result = [(None, text[: starts[0].start()] if starts else text)]
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        result.append((match.group(1), text[match.start():end]))
    return result


def outside_code(text, transform):
    """Apply transform to the text outside fenced code blocks and inline code spans."""

    def inline(segment):
        spans = []

        def mask(match):
            spans.append(match.group(0))
            return f"\x00{len(spans) - 1}\x00"

        masked = transform(INLINE_CODE.sub(mask, segment))
        return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], masked)

    parts, pos = [], 0
    for match in FENCE.finditer(text):
        parts.append(inline(text[pos:match.start()]))
        parts.append(match.group(0))
        pos = match.end()
    parts.append(inline(text[pos:]))
    return "".join(parts)


def first_paragraph(body):
    """First prose paragraph: skips headings, tables, lists, badges and the family line."""
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        skipped = block.startswith(("#", "|", "- ", "* ", "[![", "```", "~~~", ">", "**Family:**"))
        if block and not skipped:
            return block
    return ""


def without_self_links(text):
    """Drop the paragraphs that only send README readers to this website."""
    return "\n\n".join(p for p in text.split("\n\n") if SELF_LINK not in p)


def plain(markdown, keep_code=True, limit=None):
    """Markdown fragment to one line of text: links become their label."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", markdown)
    text = text.replace("**", "").replace("__", "")
    if not keep_code:
        text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return text


def github_url(path, is_dir=False, fragment=""):
    kind = "tree" if is_dir else "blob"
    url = f"{GITHUB}/{kind}/main/{quote(path)}" if path else f"{GITHUB}"
    return url + (f"#{fragment}" if fragment else "")


# --- Site model -------------------------------------------------------------------------


class Site:
    def __init__(self, repo=REPO, base_url=DEFAULT_BASE_URL):
        self.repo = Path(repo)
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.validator = load_validator(self.repo)
        self.families = self._families()
        self.skills = [skill for family in self.families for skill in family.skills]
        self.docs = sorted(p.name for p in (self.repo / "docs").glob("*.md"))
        self.routes = self._routes()

    def read(self, path):
        return (self.repo / path).read_text(encoding="utf-8")

    def _families(self):
        families = []
        for index, folder in enumerate(self.validator.FAMILIES, start=1):
            readme = f"skills/{folder}/README.md"
            title, body = split_title(self.read(readme), readme)
            names = sorted(p.parent.name for p in (self.repo / "skills" / folder).glob("*/SKILL.md"))
            # Keep the order of the family page, which lists its skills in a table.
            listed = re.findall(r"\]\(([a-z0-9-]+)/README\.md\)", body)
            order = [n for n in dict.fromkeys(listed) if n in names] + [n for n in names if n not in listed]
            family = Family(folder, title, index * 10)
            for position, name in enumerate(order, start=1):
                meta = self.validator.frontmatter_fields(self.read(f"skills/{folder}/{name}/SKILL.md"))
                family.skills.append(Skill(folder, name, str(meta["description"]).strip(), position * 10))
            families.append(family)
        return families

    def _routes(self):
        """Repository Markdown path -> Hugo content path (as used in relref)."""
        routes = {"README.md": "/", "docs/README.md": "/docs/_index.md"}
        for name in self.docs:
            if name != "README.md":
                routes[f"docs/{name}"] = f"/docs/{name}"
        for family in self.families:
            routes[f"skills/{family.folder}/README.md"] = f"/skills/{family.folder}/_index.md"
        for skill in self.skills:
            routes[f"{skill.path}/README.md"] = f"/{skill.path}/_index.md"
            routes[f"{skill.path}/SKILL.md"] = f"/{skill.path}/instructions.md"
            for ref in sorted((self.repo / skill.path / "references").glob("*.md")):
                routes[f"{skill.path}/references/{ref.name}"] = f"/{skill.path}/references/{ref.name}"
        return routes

    def page_url(self, route):
        """Public URL of a routed page (Hugo's default permalinks)."""
        path = route.removesuffix("_index.md").removesuffix(".md")
        path = path if path.endswith("/") else path + "/"
        return self.base_url + path.lstrip("/")

    # --- links ---------------------------------------------------------------------------

    def rewrite_links(self, text, source):
        """Rewrite the relative links of a Markdown text read from repository path source."""
        directory = posixpath.dirname(source)

        def replace(match):
            target = match.group(2)
            bare = target.strip("<>")
            parsed = urlsplit(bare)
            if parsed.scheme or parsed.netloc or not parsed.path:
                return match.group(0)
            resolved = posixpath.normpath(posixpath.join(directory, unquote(parsed.path)))
            if resolved.startswith("../") or resolved == "..":
                raise GenerationError(f"{source}: link {target} leaves the repository")
            fragment = parsed.fragment
            if resolved == "README.md" and fragment == "skills":
                new = '{{< relref "/skills/_index.md" >}}'
            elif resolved in self.routes:
                anchor = f"#{fragment}" if fragment else ""
                new = f'{{{{< relref "{self.routes[resolved]}{anchor}" >}}}}'
            elif (self.repo / resolved).is_dir():
                new = github_url("" if resolved == "." else resolved, is_dir=True, fragment=fragment)
            elif (self.repo / resolved).exists():
                new = github_url(resolved, fragment=fragment)
            else:
                raise GenerationError(f"{source}: broken link {target}")
            return f"{match.group(1)}{new}{match.group(3)}"

        return outside_code(text, lambda segment: LINK.sub(replace, segment))

    # --- pages ---------------------------------------------------------------------------

    def pages(self):
        pages = []
        readme = self.read("README.md")
        title, body = split_title(readme, "README.md")
        parts = sections(body)

        intro = first_paragraph(parts[0][1])
        home = []
        for heading, block in parts:
            if heading in HOME_EXCLUDED:
                continue
            if heading is None:
                # The badge and the first paragraph are in the cartouche of the home page.
                block = re.sub(r"^\[!\[.*\n", "", block.replace(intro, "", 1), flags=re.M).lstrip("\n")
            if heading == "Skills":
                block = self._with_family_diagram(block)
            home.append(block)
        pages.append(Page("README.md", "en/_index.md", title, without_self_links("".join(home)), 0,
                          plain(intro, keep_code=False), plain(intro, limit=SUMMARY_LENGTH)))

        french = dict(parts).get(FR_SECTION)
        if not french:
            raise GenerationError(f"README.md: no '## {FR_SECTION}' section for the French home page")
        french = french.split("\n", 1)[1].lstrip("\n")
        french = without_self_links(self._link_french_families(french))
        fr_intro = first_paragraph(french)
        pages.append(Page("README.md", "fr/_index.md", title, french, 0,
                          plain(fr_intro, keep_code=False), plain(fr_intro, limit=SUMMARY_LENGTH)))

        skills_block = dict(parts).get("Skills")
        if not skills_block:
            raise GenerationError("README.md: no '## Skills' section")
        skills_body = skills_block.split("\n", 1)[1].lstrip("\n")
        skills_intro = first_paragraph(skills_body)
        pages.append(Page("README.md", "shared/skills/_index.md", "Skills", skills_body, 10,
                          plain(skills_intro, keep_code=False), plain(skills_intro, limit=SUMMARY_LENGTH)))

        for family in self.families:
            source = f"skills/{family.folder}/README.md"
            pages.append(self._markdown_page(source, f"shared/skills/{family.folder}/_index.md", family.weight))
            for skill in family.skills:
                pages.extend(self._skill_pages(skill))

        for index, name in enumerate(self.docs, start=1):
            target = "shared/docs/_index.md" if name == "README.md" else f"shared/docs/{name}"
            pages.append(self._markdown_page(f"docs/{name}", target, 20 if name == "README.md" else index * 10))
        return pages

    def _markdown_page(self, source, target, weight, description=""):
        title, body = split_title(self.read(source), source)
        intro = first_paragraph(body)
        return Page(source, target, title, body, weight,
                    description or plain(intro, keep_code=False), plain(intro, limit=SUMMARY_LENGTH))

    def _skill_pages(self, skill):
        pages = [self._markdown_page(f"{skill.path}/README.md", f"shared/{skill.path}/_index.md",
                                     skill.weight, skill.description)]
        source = f"{skill.path}/SKILL.md"
        text = self.read(source)
        frontmatter = re.match(r"\A---[ \t]*\r?\n.*?\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
        heading, body = split_title(text[frontmatter.end():], source)
        lead = "{{< lead >}}\n" + skill.description + "\n{{< /lead >}}\n\n"
        pages.append(Page(source, f"shared/{skill.path}/instructions.md", f"SKILL.md: {heading}",
                          lead + body, 1, skill.description,
                          plain(f"The agent instructions of {skill.name}. {skill.description}",
                                limit=SUMMARY_LENGTH)))
        for index, ref in enumerate(sorted((self.repo / skill.path / "references").glob("*.md")), start=1):
            rel = f"{skill.path}/references/{ref.name}"
            pages.append(self._markdown_page(rel, f"shared/{rel}", 10 + index))
        return pages

    def _with_family_diagram(self, block):
        """Insert a Mermaid map of the families before the first table of the block."""
        nodes = []
        for family in self.families:
            label = re.sub(r"^\d+\.\s*", "", family.title)
            nodes.append(f'  F{family.weight // 10}["{label}"]')
        pipeline = " --> ".join(f"F{f.weight // 10}" for f in self.families[:-1])
        last = self.families[-1].weight // 10
        chained = " & ".join(f"F{f.weight // 10}" for f in self.families[:-1])
        diagram = "\n".join(["{{< mermaid >}}", "flowchart LR", *nodes, f"  {pipeline}",
                             f"  F{last} -.-> {chained}", "{{< /mermaid >}}", "", ""])
        index = block.find("\n|")
        return block if index < 0 else block[: index + 1] + diagram + block[index + 1:]

    def _link_french_families(self, text):
        """Link the bold family names of the French summary, in family order, to their pages."""
        families = iter(self.families)

        def link(match):
            family = next(families, None)
            if family is None:
                return match.group(0)
            return f'**[{match.group(1)}]({{{{< relref "/skills/{family.folder}/_index.md" >}}}})**{match.group(2)}'

        return re.sub(r"^\*\*([^*]+)\*\*( :)", link, text, flags=re.M)

    # --- output --------------------------------------------------------------------------

    def render(self, page):
        if SHORTCODE.search(self.read(page.source)):
            raise GenerationError(f"{page.source}: contains '{{{{<' or '{{{{%', which Hugo would execute")
        body = self.rewrite_links(page.body, page.source).rstrip() + "\n"
        front = {"title": page.title, "weight": page.weight}
        if page.description:
            front["description"] = page.description
        if page.summary:
            front["summary"] = page.summary
        front["editURL"] = github_url(page.source)
        return "---\n" + yaml.safe_dump(front, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n" + body

    def check(self, rendered):
        """Fail on what Hugo would not catch or would publish wrongly."""
        problems = []
        # Pages under shared/ exist in both languages; en/ and fr/ hold the home pages.
        available = {"/" + t.split("/", 1)[1] for t in rendered if t.startswith("shared/")} | {"/"}
        for target, text in rendered.items():
            if PurePosixPath(target).name == "SKILL.md":
                problems.append(f"{target}: a generated file must not be named SKILL.md")
            for path, _ in RELREF.findall(text):
                if path not in available:
                    problems.append(f"{target}: relref to unknown page {path}")

            def leftover(segment, target=target):
                for match in LINK.finditer(segment):
                    parsed = urlsplit(match.group(2).strip("<>"))
                    if not (parsed.scheme or parsed.netloc or not parsed.path or match.group(2).startswith("{{<")):
                        problems.append(f"{target}: relative link {match.group(2)} was not rewritten")
                return segment

            outside_code(text, leftover)
        if problems:
            raise GenerationError("\n".join(problems))

    def llms_txt(self):
        description = plain(first_paragraph(split_title(self.read("README.md"), "README.md")[1]), keep_code=False)
        lines = [
            "# geoskills",
            "",
            f"> {description}",
            "",
            "Each skill is a folder with a SKILL.md (the agent instructions, linked below), "
            "references and helper scripts. Install them with `npx skills add ignfab/geoskills` "
            f"or `npx skills add {self.base_url.rstrip('/')}`.",
        ]
        for family in self.families:
            lines += ["", f"## {family.title}", ""]
            for skill in family.skills:
                lines.append(f"- [{skill.name}]({RAW}/{skill.path}/SKILL.md): {skill.description} "
                             f"Page: {self.page_url(self.routes[f'{skill.path}/README.md'])}")
        lines += ["", "## Optional", ""]
        for name in self.docs:
            route = self.routes.get(f"docs/{name}")
            title, _ = split_title(self.read(f"docs/{name}"), f"docs/{name}")
            lines.append(f"- [{title}]({RAW}/docs/{name}): {self.page_url(route)}")
        return "\n".join(lines) + "\n"

    def skill_archive(self, skill):
        """Deterministic zip of a skill folder, SKILL.md at its root."""
        root = self.repo / skill.path
        files = []
        for directory, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in ARCHIVE_EXCLUDED_DIRS and not d.startswith("."))
            for name in filenames:
                if not name.startswith(".") and not name.endswith(".pyc"):
                    files.append(Path(directory, name))
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for path in sorted(files, key=lambda p: p.relative_to(root).as_posix()):
                info = zipfile.ZipInfo(path.relative_to(root).as_posix(), ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                mode = 0o755 if os.access(path, os.X_OK) else 0o644
                info.external_attr = (0o100000 | mode) << 16
                archive.writestr(info, path.read_bytes(), compresslevel=9)
        return buffer.getvalue()

    def discovery(self):
        """Agent Skills Discovery index (v0.2.0) and its archives: {relative path: bytes}."""
        files, entries = {}, []
        for skill in self.skills:
            data = self.skill_archive(skill)
            files[f"{WELL_KNOWN}/{skill.name}.zip"] = data
            entries.append({
                "name": skill.name,
                "type": "archive",
                "description": skill.description,
                "url": f"{skill.name}.zip",
                "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
            })
        index = {"$schema": DISCOVERY_SCHEMA, "skills": entries}
        files[f"{WELL_KNOWN}/index.json"] = (json.dumps(index, indent=2, ensure_ascii=False) + "\n").encode()
        return files

    def generate(self, out):
        out = Path(out)
        rendered = {page.target: self.render(page) for page in self.pages()}
        self.check(rendered)
        if out.exists():
            shutil.rmtree(out)
        for target, text in rendered.items():
            path = out / "content" / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        static = {"llms.txt": self.llms_txt().encode(), **self.discovery()}
        for target, data in static.items():
            path = out / "static" / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return rendered, static


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", default=str(REPO / "site" / "generated"), help="output directory (replaced)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="public URL of the site")
    args = parser.parse_args(argv)
    try:
        site = Site(REPO, args.base_url)
        rendered, static = site.generate(args.out)
    except GenerationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"{len(rendered)} pages, {len(site.families)} families, {len(site.skills)} skills, "
          f"{len(static)} static files -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
