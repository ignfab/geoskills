"""Check the experimental prompt catalog and run log in tests/prompts/."""
from datetime import date
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tests" / "prompts"
spec = importlib.util.spec_from_file_location("validate_skills", ROOT / ".github" / "validate-skills.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

SKILLS = {path.parent.name for path in (ROOT / "skills").glob("*/*/SKILL.md")}
HEADER = "| Date | Prompt | Harness | Model | Commit | Skills loaded | Outcome | Notes |"
OUTCOMES = {"pass", "partial", "fail"}
SKILL_LIST = re.compile(r"none|`[a-z0-9-]+`(?:(?:,| or|,? then) `[a-z0-9-]+`)*")


def catalog_entries():
    """Return (identifier, fields, prompt) for each catalog entry, in file order."""
    text = (PROMPTS / "catalog.md").read_text(encoding="utf-8")
    parts = re.split(r"^## (XP-\d+) — .+$", text, flags=re.M)
    entries = []
    for identifier, body in zip(parts[1::2], parts[2::2]):
        prompt = " ".join(line[1:].strip() for line in body.splitlines() if line.startswith(">"))
        fields = {name: " ".join(value.split()) for name, value in re.findall(
            r"^- \*\*([A-Za-z ]+):\*\* (.+(?:\n  .+)*)", body, flags=re.M)}
        entries.append((identifier, fields, prompt))
    return entries


def run_rows():
    lines = (PROMPTS / "runs.md").read_text(encoding="utf-8").splitlines()
    start = lines.index(HEADER)
    rows = []
    for line in lines[start + 2:]:
        if not line.strip():
            break
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        rows.append((line, cells))
    return rows


def scenario_ids():
    ids = set()
    for path in (ROOT / "tests").glob("*.md"):
        ids.update(re.findall(r"^## ([A-Z]+-N?\d+)\s", path.read_text(encoding="utf-8"), re.M))
    return ids


class PromptLogTests(unittest.TestCase):
    def test_catalog_entries_are_complete(self):
        entries = catalog_entries()
        self.assertTrue(entries)
        identifiers = [identifier for identifier, _, _ in entries]
        self.assertEqual(len(identifiers), len(set(identifiers)), "XP identifiers must be unique")
        scenarios = scenario_ids()
        for identifier, fields, prompt in entries:
            with self.subTest(prompt=identifier):
                self.assertRegex(identifier, r"^XP-\d{2,}$")
                self.assertTrue(prompt, "missing French prompt")
                self.assertEqual(set(fields), {"Family", "Expected skills", "Watch", "Status"})
                family = fields["Family"].strip("`")
                self.assertIn(family, validator.FAMILIES)
                expected = fields["Expected skills"]
                self.assertRegex(expected, rf"^(?:{SKILL_LIST.pattern})$")
                self.assertLessEqual(set(re.findall(r"`([a-z0-9-]+)`", expected)), SKILLS)
                self.assertTrue(fields["Watch"])
                status = fields["Status"]
                self.assertRegex(status, r"^(open|promoted to [A-Z]+-N?\d+|dropped\b.*)$")
                if status.startswith("promoted to "):
                    self.assertIn(status.removeprefix("promoted to "), scenarios)

    def test_run_rows_are_well_formed(self):
        catalog = {identifier for identifier, _, _ in catalog_entries()}
        for line, cells in run_rows():
            with self.subTest(row=line[:60]):
                self.assertEqual(len(cells), 8, "a row has eight columns")
                when, prompt, harness, model, commit, skills, outcome, notes = cells
                date.fromisoformat(when)
                self.assertIn(prompt, catalog)
                self.assertTrue(harness and model and notes)
                self.assertRegex(commit, r"^[0-9a-f]{7,40}(\+dirty)?$")
                self.assertRegex(skills, rf"^(?:{SKILL_LIST.pattern})$")
                self.assertIn(outcome, OUTCOMES)

    def test_template_cannot_shadow_a_catalog_prompt(self):
        # The A/B runner reads tests/prompts/*.md: the template must not match an identifier.
        readme = (PROMPTS / "README.md").read_text(encoding="utf-8")
        self.assertNotRegex(readme, r"(?m)^## XP-\d")


if __name__ == "__main__":
    unittest.main()
