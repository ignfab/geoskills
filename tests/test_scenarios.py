"""Check that every agent scenario can be scored and that ab-testing.md follows them.

Agent scenarios (tests/<skill>.md) are scored by hand. These checks make sure that each
one has what a scorer needs (a French prompt, an expected skill and a checklist), that the
fixtures it names exist, and that the lists, matrix, score table and run count of
tests/ab-testing.md stay in step with the scenario files.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md"))
AB = (TESTS / "ab-testing.md").read_text(encoding="utf-8")
README = (TESTS / "README.md").read_text(encoding="utf-8")
SKILL_TOKEN = re.compile(r"`([a-z][a-z0-9-]*[a-z0-9])`")
# Runs after WFS-01 and extends its output, so ab_campaign calls it explicitly.
CHAINED = {"WFS-03"}


def scenarios(skill):
    """Return [(identifier, body)] for the '## <ID> — <title>' sections of tests/<skill>.md."""
    text = (TESTS / f"{skill}.md").read_text(encoding="utf-8")
    parts = re.split(r"^## ([A-Z]+-N?\d+) — .+$", text, flags=re.M)
    return list(zip(parts[1::2], parts[2::2]))


def paragraph(body, label):
    """Return the paragraph that starts with **<label>:**, or None."""
    match = re.search(rf"^\*\*{label}:\*\*(.+?)(?:\n\n|\Z)", body, flags=re.M | re.S)
    return " ".join(match.group(1).split()) if match else None


def is_negative(identifier):
    return "-N" in identifier


class ScenarioFileTests(unittest.TestCase):
    def test_every_skill_has_a_listed_scenario_file(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                self.assertTrue((TESTS / f"{skill}.md").is_file(), f"missing tests/{skill}.md")
                self.assertIn(f"]({skill}.md)", README, "add the file to tests/README.md")

    def test_identifiers_are_numbered_without_gaps(self):
        seen = {}
        for skill in SKILLS:
            identifiers = [identifier for identifier, _ in scenarios(skill)]
            with self.subTest(skill=skill):
                self.assertTrue(identifiers, "no scenario")
                prefixes = {identifier.split("-")[0] for identifier in identifiers}
                self.assertEqual(len(prefixes), 1, f"one prefix per file: {prefixes}")
                positives = [i for i in identifiers if not is_negative(i)]
                negatives = [i for i in identifiers if is_negative(i)]
                self.assertTrue(positives, "at least one positive scenario")
                self.assertTrue(negatives, "at least one negative scenario")
                self.assertEqual(identifiers, positives + negatives,
                                 "positive scenarios come before negative ones")
                prefix = prefixes.pop()
                self.assertEqual(positives, [f"{prefix}-{n:02d}" for n in range(1, len(positives) + 1)])
                self.assertEqual(negatives, [f"{prefix}-N{n}" for n in range(1, len(negatives) + 1)])
                for identifier in identifiers:
                    self.assertNotIn(identifier, seen, f"also in tests/{seen.get(identifier)}.md")
                    seen[identifier] = skill

    def test_every_scenario_can_be_scored(self):
        for skill in SKILLS:
            for identifier, body in scenarios(skill):
                with self.subTest(scenario=identifier):
                    prompt = " ".join(line[1:].strip() for line in body.splitlines()
                                      if line.startswith(">"))
                    self.assertTrue(prompt, "missing French prompt (a > block)")
                    expected = paragraph(body, "Expected skill")
                    self.assertIsNotNone(expected, "missing **Expected skill:** line")
                    named = set(SKILL_TOKEN.findall(expected))
                    self.assertLessEqual(named, set(SKILLS), "unknown skill name")
                    if is_negative(identifier):
                        self.assertIn(f"not `{skill}`", expected,
                                      "a negative scenario names the skill it must not load")
                    else:
                        self.assertIn(f"`{skill}`", expected)
                    self.assertRegex(body, r"(?m)^- \[ \] \S", "missing checklist item")

    def test_fixtures_named_in_prompts_exist(self):
        for skill in SKILLS:
            for identifier, body in scenarios(skill):
                prompt = "\n".join(line for line in body.splitlines() if line.startswith(">"))
                for path in re.findall(r"\bdata/[\w./-]*", prompt):
                    with self.subTest(scenario=identifier, path=path):
                        self.assertTrue((TESTS / path.rstrip(".")).exists())


class ABProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.positives, cls.negatives = {}, {}
        for skill in SKILLS:
            for identifier, _ in scenarios(skill):
                (cls.negatives if is_negative(identifier) else cls.positives)[identifier] = skill

    def runner_list(self, name):
        return re.search(rf'^{name}="([^"]*)"', AB, flags=re.M).group(1).split()

    def test_runner_lists_hold_every_scenario_once(self):
        positive, negative = self.runner_list("POSITIVE"), self.runner_list("NEGATIVE")
        self.assertEqual(len(positive), len(set(positive)), "duplicate in POSITIVE")
        self.assertEqual(len(negative), len(set(negative)), "duplicate in NEGATIVE")
        self.assertEqual(set(positive), set(self.positives) - CHAINED)
        self.assertEqual(set(negative), set(self.negatives))

    def test_matrix_has_one_row_per_scenario_in_its_skill_section(self):
        matrix = AB.split("## Scenario matrix", 1)[1].split("\n## ", 1)[0]
        sections = dict(re.findall(r"^### \[([a-z0-9-]+)\]\([a-z0-9-]+\.md\)\n(.*?)(?=^### |\Z)",
                                   matrix, flags=re.M | re.S))
        self.assertEqual(set(sections), set(SKILLS))
        for skill, section in sections.items():
            rows = dict(re.findall(r"^\| ([A-Z]+-N?\d+) \| ([^|]+?) \|", section, flags=re.M))
            with self.subTest(skill=skill):
                expected = {i for i, s in {**self.positives, **self.negatives}.items() if s == skill}
                self.assertEqual(set(rows), expected)
                for identifier, modes in rows.items():
                    self.assertEqual(modes.split(",")[0],
                                     "A" if is_negative(identifier) else "A + B", identifier)

    def test_score_table_and_run_count_follow_the_scenarios(self):
        for skill in SKILLS:
            count = 3 * sum(1 for s in self.positives.values() if s == skill)
            with self.subTest(skill=skill):
                self.assertRegex(AB, rf"(?m)^\| {re.escape(skill)} \| /{count} \| /{count} \|")
        self.assertRegex(AB, rf"(?m)^\| Negative scenarios \(A only\) \| /{3 * len(self.negatives)} \|")
        runs = 2 * len(self.positives) + len(self.negatives)
        sentence = " ".join(AB.split())
        self.assertIn(f"One repetition has **{runs} runs**: {len(self.positives)} positive "
                      f"scenarios in both modes and {len(self.negatives)} negatives in A.", sentence)
        budget = int(re.search(r"example budget of \$(\d+) per run", sentence).group(1))
        self.assertIn(f"the caps total ${budget * runs} per repetition and ${3 * budget * runs} "
                      "for three repetitions", sentence)


if __name__ == "__main__":
    unittest.main()
