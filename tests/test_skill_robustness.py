"""Check the wording that keeps skill selection from depending on the model's own inference.

A strong model can guess that "a raster skill" means `gdal-raster-basics`, or that a
request about a local file needs no Géoplateforme service; a smaller model often cannot.
These checks require each skill to spell out what a model needs to choose correctly: when
to use it, which skill to use instead at each boundary that a negative scenario tests, and
exact skill names rather than descriptions of them. They read files only; measuring how
each model actually behaves is the model sweep of tests/ab-testing.md.
"""
import re
import unittest

from test_scenarios import ROOT, SKILLS, is_negative, paragraph, scenarios

SKILL_FILES = {p.parent.name: p for p in (ROOT / "skills").glob("*/*/SKILL.md")}
# "a raster skill", "the WFS skill", "the corresponding specialized skill"; not "this skill".
GENERIC_REFERENCE = re.compile(
    r"\b(?:a|an|the|corresponding|specialized)\s+(?:[\w/-]+\s+){0,2}skills?\b", re.I)
WHEN_TO_USE = re.compile(r"\bUse (?:when|for|to|it)\b")


def frontmatter(skill):
    text = SKILL_FILES[skill].read_text(encoding="utf-8")
    header, body = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.S).groups()
    description = re.search(r"^description:\s*(.+)$", header, flags=re.M).group(1).strip()
    return description, body


class DescriptionTests(unittest.TestCase):
    def test_descriptions_say_when_to_use_the_skill(self):
        for skill in SKILLS:
            description, _ = frontmatter(skill)
            with self.subTest(skill=skill):
                self.assertRegex(description, WHEN_TO_USE, "add a 'Use when/for/to …' clause")
                # Agent Skills specification limit; some agents truncate or reject longer ones.
                self.assertLessEqual(len(description), 1024)

    def test_descriptions_name_other_skills_exactly(self):
        for skill in SKILLS:
            description, _ = frontmatter(skill)
            with self.subTest(skill=skill):
                self.assertEqual(GENERIC_REFERENCE.findall(description), [],
                                 "name the skill (geopf-wfs-download), not 'the WFS skill'")


class BoundaryTests(unittest.TestCase):
    def test_tested_boundaries_are_written_in_the_excluded_skill(self):
        """A negative scenario '`X`, not `Y`' needs `Y` to point to `X`.

        A model that loads `Y` by mistake then finds the way out in the text it just read,
        instead of having to work out the boundary by itself.
        """
        for skill in SKILLS:
            description, body = frontmatter(skill)
            for identifier, scenario in scenarios(skill):
                if not is_negative(identifier):
                    continue
                expected = paragraph(scenario, "Expected skill")
                alternatives = [name for name in re.findall(r"`([a-z0-9-]+)`",
                                                            expected.split("not `", 1)[0])
                                if name in SKILLS]
                if not alternatives:
                    continue  # No skill of this repository is the right answer.
                with self.subTest(scenario=identifier, excluded=skill):
                    self.assertTrue(any(name in description or name in body
                                        for name in alternatives),
                                    f"{skill}/SKILL.md names none of {alternatives}")


if __name__ == "__main__":
    unittest.main()
