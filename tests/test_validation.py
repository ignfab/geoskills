"""Regression tests for metadata validation, using isolated miniature repositories."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / ".github" / "validate-skills.py"
spec = importlib.util.spec_from_file_location("validate_skills", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

FIELDS = "name: example-skill\ndescription: Useful"
SECTIONS = "\n## Prerequisites\nUse existing tools.\n## Validate the output\nCheck the result.\n"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.family = self.root / "skills" / "1-discover"
        self.skill = self.family / "example-skill"
        self.skill.mkdir(parents=True)
        (self.skill / "README.md").write_text("# Example\n")
        (self.family / "README.md").write_text("[example-skill](example-skill/README.md)\n")
        (self.root / "README.md").write_text(
            "[example-skill](skills/1-discover/example-skill/README.md)\n")

    def check(self, frontmatter, body="", *, required_sections=True):
        if required_sections:
            body += SECTIONS
        (self.skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}")
        return validator.validate(self.root)[0]

    def add_skill(self, directory):
        directory.mkdir(parents=True)
        (directory / "README.md").write_text("# Other\n")
        (directory / "SKILL.md").write_text(
            f"---\nname: {directory.name}\ndescription: Useful\n---\n{SECTIONS}")

    def assertReported(self, message, errors):
        self.assertTrue(any(message in error for error in errors), errors)

    def test_valid_multiline_description(self):
        self.assertEqual(self.check("name: example-skill\ndescription: >\n  Useful first line\n  and another line."), [])

    def test_invalid_metadata(self):
        cases = ["description: |", "description: null", "description: false",
                 "description: []", "description: [broken", "description: good\ndescription: other"]
        for case in cases:
            with self.subTest(case=case):
                self.assertTrue(self.check("name: example-skill\n" + case))
        self.assertTrue(self.check("name: other-name\ndescription: Useful"))

    def test_required_workflow_sections(self):
        for heading in ("Prerequisites", "Validate the output"):
            with self.subTest(missing=heading):
                other = "Prerequisites" if heading == "Validate the output" else "Validate the output"
                body = f"## {other}\nInstructions.\n```markdown\n## {heading}\n```\n"
                errors = self.check(FIELDS, body, required_sections=False)
                self.assertReported(f"missing required section '## {heading}'", errors)

    def test_reference_links(self):
        refs = self.skill / "references"
        refs.mkdir()
        (refs / "details.md").write_text("# Details\n")
        self.assertTrue(self.check(FIELDS))  # Undiscoverable reference.
        self.assertEqual(self.check(FIELDS, "[Details](references/details.md)"), [])
        self.assertTrue(self.check(FIELDS, "[Missing](references/missing.md)"))

    def test_reference_chain(self):
        refs = self.skill / "references"
        refs.mkdir()
        (refs / "one.md").write_text("[Two](two.md)\n")
        (refs / "two.md").write_text("# Two\n")
        self.assertEqual(self.check(FIELDS, "[One](references/one.md)"), [])

    def test_examples_are_not_links(self):
        body = "```markdown\n[Example](does-not-exist.md)\n```\n[Site](https://example.org/)"
        self.assertEqual(self.check(FIELDS, body), [])

    def test_missing_skill_file(self):
        self.assertIn("skills/1-discover/example-skill: missing SKILL.md",
                      validator.validate(self.root)[0])

    def test_skills_live_in_a_known_family(self):
        self.add_skill(self.root / "skills" / "flat-skill")
        self.add_skill(self.root / "skills" / "misc" / "other-skill")
        errors = self.check(FIELDS)
        self.assertReported("skills/flat-skill: unknown family", errors)
        self.assertReported("skills/flat-skill/SKILL.md: expected skills/<family>/<skill-name>/SKILL.md",
                            errors)
        self.assertReported("skills/misc: unknown family", errors)

    def test_family_folder_holds_a_readme_and_skills_only(self):
        (self.family / "SKILL.md").write_text(f"---\nname: 1-discover\ndescription: Wrong\n---\n{SECTIONS}")
        (self.family / "README.md").unlink()
        errors = self.check(FIELDS)
        self.assertIn("skills/1-discover/SKILL.md: a family folder must not hold a SKILL.md", errors)
        self.assertIn("skills/1-discover: missing family README.md", errors)

    def test_skill_names_are_unique_across_families(self):
        self.add_skill(self.root / "skills" / "2-access" / "example-skill")
        self.assertReported("duplicate skill name 'example-skill'", self.check(FIELDS))

    def test_every_skill_is_listed_in_both_indexes(self):
        for index in ("README.md", "skills/1-discover/README.md"):
            with self.subTest(index=index):
                path = self.root / index
                original = path.read_text()
                path.write_text("# Index\n")
                errors = self.check(FIELDS)
                path.write_text(original)
                self.assertIn(f"{index}: no link to skills/1-discover/example-skill/README.md", errors)

    def test_agent_files_do_not_link_outside_the_skill(self):
        # Installed copies are flat, so a link out of SKILL.md or references/ would dangle.
        refs = self.skill / "references"
        refs.mkdir()
        (refs / "details.md").write_text("[Family](../../README.md)\n")
        errors = self.check(FIELDS, "[Details](references/details.md)\n[Family](../README.md)\n")
        self.assertReported("example-skill/SKILL.md: link leaves the skill folder", errors)
        self.assertReported("references/details.md: link leaves the skill folder", errors)

    def test_skill_readme_may_link_across_the_repository(self):
        (self.skill / "README.md").write_text("[Family](../README.md) · [Home](../../../README.md)\n")
        self.assertEqual(self.check(FIELDS), [])


if __name__ == "__main__":
    unittest.main()
