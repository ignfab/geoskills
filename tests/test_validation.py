"""Regression tests for metadata validation, using isolated miniature repositories."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / ".github" / "validate-skills.py"
spec = importlib.util.spec_from_file_location("validate_skills", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills" / "example-skill"
        self.skill.mkdir(parents=True)
        (self.skill / "README.md").write_text("# Example\n")

    def check(self, frontmatter, body="", *, required_sections=True):
        if required_sections:
            body += "\n## Prerequisites\nUse existing tools.\n## Validate the output\nCheck the result.\n"
        (self.skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}")
        return validator.validate(self.root)[0]

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
        fields = "name: example-skill\ndescription: Useful"
        for heading in ("Prerequisites", "Validate the output"):
            with self.subTest(missing=heading):
                other = "Prerequisites" if heading == "Validate the output" else "Validate the output"
                body = f"## {other}\nInstructions.\n```markdown\n## {heading}\n```\n"
                errors = self.check(fields, body, required_sections=False)
                self.assertTrue(any(f"missing required section '## {heading}'" in error
                                    for error in errors), errors)

    def test_reference_links(self):
        refs = self.skill / "references"
        refs.mkdir()
        (refs / "details.md").write_text("# Details\n")
        fields = "name: example-skill\ndescription: Useful"
        self.assertTrue(self.check(fields))  # Undiscoverable reference.
        self.assertEqual(self.check(fields, "[Details](references/details.md)"), [])
        self.assertTrue(self.check(fields, "[Missing](references/missing.md)"))

    def test_reference_chain(self):
        refs = self.skill / "references"
        refs.mkdir()
        (refs / "one.md").write_text("[Two](two.md)\n")
        (refs / "two.md").write_text("# Two\n")
        self.assertEqual(self.check("name: example-skill\ndescription: Useful",
                                    "[One](references/one.md)"), [])

    def test_examples_are_not_links(self):
        body = "```markdown\n[Example](does-not-exist.md)\n```\n[Site](https://example.org/)"
        self.assertEqual(self.check("name: example-skill\ndescription: Useful", body), [])

    def test_missing_skill_file(self):
        self.assertTrue(validator.validate(self.root)[0])


if __name__ == "__main__":
    unittest.main()
