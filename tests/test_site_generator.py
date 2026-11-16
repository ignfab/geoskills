"""Tests for site/generate.py, the generator of the Hugo site, without Hugo."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("generate_site", ROOT / "site" / "generate.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

SKILL_FILES = sorted(ROOT.glob("skills/*/*/SKILL.md"))


class LinkRewritingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = generator.Site(ROOT)

    def rewrite(self, text, source="skills/2-access/geopf-wfs-download/README.md"):
        return self.site.rewrite_links(text, source)

    def test_published_pages_become_checked_hugo_refs(self):
        cases = {
            "[x](../geopf-raster-download/README.md)":
                '[x]({{< relref "/skills/2-access/geopf-raster-download/_index.md" >}})',
            "[x](../README.md)": '[x]({{< relref "/skills/2-access/_index.md" >}})',
            "[x](SKILL.md)": '[x]({{< relref "/skills/2-access/geopf-wfs-download/instructions.md" >}})',
            "[x](references/formats.md#missing-gdal-or-parquet-support)":
                '[x]({{< relref "/skills/2-access/geopf-wfs-download/references/formats.md'
                '#missing-gdal-or-parquet-support" >}})',
            "[x](../../../docs/dependencies.md)": '[x]({{< relref "/docs/dependencies.md" >}})',
            "[x](../../../README.md#skills)": '[x]({{< relref "/skills/_index.md" >}})',
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(self.rewrite(source), expected)

    def test_unpublished_files_link_to_github(self):
        base = "https://github.com/ignfab/geoskills"
        cases = {
            "[x](scripts/check_export.py)":
                f"[x]({base}/blob/main/skills/2-access/geopf-wfs-download/scripts/check_export.py)",
            "[x](../../../tests/geopf-wfs-download.md)": f"[x]({base}/blob/main/tests/geopf-wfs-download.md)",
            "[x](../../../tests/README.md#live-tests)": f"[x]({base}/blob/main/tests/README.md#live-tests)",
            "[x](../../../CLAUDE.md)": f"[x]({base}/blob/main/CLAUDE.md)",
            "[x](../../../tests/prompts/)": f"[x]({base}/tree/main/tests/prompts)",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(self.rewrite(source), expected)

    def test_external_links_anchors_and_code_are_unchanged(self):
        for text in (
            "[x](https://data.geopf.fr/wfs/ows)",
            "[x](#prerequisites)",
            "Inline `[x](SKILL.md)` code.",
            "```markdown\n[x](SKILL.md)\n```",
        ):
            with self.subTest(text=text):
                self.assertEqual(self.rewrite(text), text)

    def test_link_label_with_inline_code_is_rewritten(self):
        self.assertEqual(
            self.rewrite("[`geopf-file-download`](../geopf-file-download/README.md)"),
            '[`geopf-file-download`]({{< relref "/skills/2-access/geopf-file-download/_index.md" >}})')

    def test_broken_or_escaping_links_fail(self):
        for text in ("[x](missing.md)", "[x](../../../../outside.md)"):
            with self.subTest(text=text), self.assertRaises(generator.GenerationError):
                self.rewrite(text)


class MarkdownHelperTests(unittest.TestCase):
    def test_title_comes_from_the_first_heading(self):
        title, body = generator.split_title("# geopf-wfs-download\n\nBody\n", "README.md")
        self.assertEqual((title, body), ("geopf-wfs-download", "Body\n"))
        with self.assertRaises(generator.GenerationError):
            generator.split_title("No heading\n", "README.md")

    def test_summary_skips_the_family_line_and_drops_link_targets(self):
        body = "**Family:** [2. Access](../README.md).\n\nDownload [WFS](https://x) layers.\n"
        paragraph = generator.first_paragraph(body)
        self.assertEqual(generator.plain(paragraph), "Download WFS layers.")

    def test_sections_ignore_headings_inside_code(self):
        text = "Intro\n\n## One\n\n```md\n## Not a section\n```\n\n## Two\n"
        self.assertEqual([h for h, _ in generator.sections(text)], [None, "One", "Two"])


class GeneratedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.temp.name) / "generated"
        cls.site = generator.Site(ROOT, "https://example.org/geoskills")
        cls.rendered, cls.static = cls.site.generate(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_every_skill_family_reference_and_doc_has_a_page(self):
        content = self.out / "content"
        self.assertEqual(len(self.site.families), 6)
        self.assertEqual(len(self.site.skills), len(SKILL_FILES))
        for skill_md in SKILL_FILES:
            skill = skill_md.parent.relative_to(ROOT).as_posix()
            with self.subTest(skill=skill):
                self.assertTrue((content / "shared" / skill / "_index.md").is_file())
                self.assertTrue((content / "shared" / skill / "instructions.md").is_file())
                for ref in (skill_md.parent / "references").glob("*.md"):
                    self.assertTrue((content / "shared" / skill / "references" / ref.name).is_file())
        for family in generator.load_validator(ROOT).FAMILIES:
            self.assertTrue((content / "shared" / "skills" / family / "_index.md").is_file())
        for doc in (ROOT / "docs").glob("*.md"):
            name = "_index.md" if doc.name == "README.md" else doc.name
            self.assertTrue((content / "shared" / "docs" / name).is_file())
        self.assertTrue((content / "en" / "_index.md").is_file())
        self.assertTrue((content / "fr" / "_index.md").is_file())

    def test_no_generated_file_is_named_skill_md(self):
        self.assertEqual([p for p in self.out.rglob("*") if p.name == "SKILL.md"], [])

    def test_pages_have_front_matter_and_no_duplicate_title(self):
        page = (self.out / "content/shared/skills/2-access/geopf-wfs-download/_index.md").read_text()
        front, body = re.match(r"\A---\n(.*?)\n---\n\n(.*)\Z", page, re.S).groups()
        fields = generator.yaml.safe_load(front)
        self.assertEqual(fields["title"], "geopf-wfs-download")
        self.assertTrue(fields["description"].startswith("Downloads WFS data"))
        self.assertTrue(fields["editURL"].endswith("/blob/main/skills/2-access/geopf-wfs-download/README.md"))
        self.assertFalse(body.startswith("# "))

    def test_french_home_comes_from_the_french_summary_only(self):
        french = (self.out / "content/fr/_index.md").read_text()
        english = (self.out / "content/en/_index.md").read_text()
        self.assertIn('**[Découvrir et sélectionner]({{< relref "/skills/1-discover/_index.md" >}})**', french)
        self.assertNotIn("## Scope", french)
        self.assertNotIn("Résumé (FR)", english)
        self.assertIn("{{< mermaid >}}", english)
        # The badge and the first paragraph of the README are shown in the home cartouche.
        self.assertNotIn("[![Agent Skills]", english)
        self.assertNotIn("Agent skills for discovering, retrieving", english.split("---", 2)[2])
        # README paragraphs that send readers to the website are not repeated on it.
        for page in (english, french):
            self.assertNotIn(generator.SELF_LINK, page)

    def test_llms_txt_lists_every_skill(self):
        text = self.static["llms.txt"].decode()
        self.assertTrue(text.startswith("# geoskills\n\n> "))
        for skill in self.site.skills:
            self.assertIn(f"- [{skill.name}]({generator.RAW}/{skill.path}/SKILL.md): ", text)
        self.assertIn("https://example.org/geoskills/skills/2-access/geopf-wfs-download/", text)

    def test_discovery_index_matches_its_archives(self):
        index = json.loads(self.static[".well-known/agent-skills/index.json"])
        self.assertEqual(index["$schema"], generator.DISCOVERY_SCHEMA)
        names = {generator.load_validator(ROOT).frontmatter_fields(p.read_text())["name"] for p in SKILL_FILES}
        self.assertEqual({entry["name"] for entry in index["skills"]}, names)
        for entry in index["skills"]:
            with self.subTest(skill=entry["name"]):
                self.assertRegex(entry["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
                self.assertLessEqual(len(entry["description"]), 1024)
                self.assertEqual(entry["type"], "archive")
                data = self.static[f".well-known/agent-skills/{entry['url']}"]
                self.assertEqual(entry["digest"], "sha256:" + hashlib.sha256(data).hexdigest())
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    files = archive.namelist()
                self.assertIn("SKILL.md", files)
                self.assertFalse([f for f in files if "__pycache__" in f or f.startswith(("/", "..")) or "/." in f])

    def test_archives_are_reproducible(self):
        skill = self.site.skills[0]
        self.assertEqual(self.site.skill_archive(skill), self.site.skill_archive(skill))

    def test_check_rejects_unknown_refs_and_leftover_relative_links(self):
        with self.assertRaises(generator.GenerationError):
            self.site.check({"shared/a.md": '[x]({{< relref "/missing.md" >}})'})
        with self.assertRaises(generator.GenerationError):
            self.site.check({"shared/a.md": "[x](other.md)"})


if __name__ == "__main__":
    unittest.main()
