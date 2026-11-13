"""Check the wording of the optional MCP routes and keep their documentation in step.

A `## MCP servers` section tells an agent to use a connected MCP server first. These checks
keep that preference a soft and safe one in every skill: the section says that the server
is optional, says what to do without it or when a call fails, ends by forbidding to
install or configure one and contains no setup step; a database is only read, and the
user's QGIS session is only changed on request. They also keep the skill READMEs and
docs/mcp-servers.md listing the same skills. They read files only: whether an agent uses a
connected server as written is measured by agent runs.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADING = "## MCP servers"
RULE = "Never install, configure or start an MCP server"
SERVERS = ("Geocontext", "PostGIS", "QGIS")
# The fallback sentence: no server, or a server whose call fails.
FALLBACK = re.compile(r"Without .{1,80}?, or when (?:a|the|its) (?:call|query) fails")
# The section ends with the rule; a QGIS skill also names the plugin.
ENDS_WITH_RULE = re.compile(re.escape(RULE) + r"(?: or a QGIS plugin)? yourself\.$")
# Installing is only named by the rule that forbids it.
SETUP = re.compile(r"(?i)\binstall(?!ed\b)|\bnpx\b|\bmcp add\b")
# The WFS tools of Geocontext are named `gpf_wfs_*` in 0.9 and `gpf_*` from 0.10.
GPF_TOOL = re.compile(r"`gpf_\w+`")
# What a section naming them must add, so that an agent on another version copes.
OTHER_VERSIONS = re.compile(r"(?:version|Geocontext) \d+\.\d+|tool list")
READ_ONLY = ("Run read-only queries: `SELECT` without `INTO`, and no function that changes "
             "data, schema or SRID.")
SESSION_GUARD = re.compile(r"unless (?:asked|the user asks)|[Oo]nly (?:when|if) (?:asked|the user asks)"
                           r"|only on (?:explicit )?request")
# qgis-layer-styling guards two steps: showing the style, and any other change.
SESSION_GUARDS = {"qgis-layer-styling": 2}


def section(path):
    """Return the text of the MCP section of a Markdown file, or None."""
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(HEADING)}\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return " ".join(match.group(1).split()) if match else None


def skills_with_section(filename):
    return {path.parent.name: path for path in sorted(ROOT.glob(f"skills/*/*/{filename}"))
            if section(path) is not None}


class McpSectionTests(unittest.TestCase):
    def setUp(self):
        self.skills = skills_with_section("SKILL.md")

    def test_some_skills_have_an_mcp_section(self):
        self.assertTrue(self.skills, f"no SKILL.md has a '{HEADING}' section")

    def test_the_server_stays_optional(self):
        for name, path in self.skills.items():
            text = section(path)
            with self.subTest(skill=name):
                self.assertTrue(text.startswith("Optional."), "start the section with 'Optional.'")
                self.assertRegex(text, FALLBACK, "say what to do without the server or when a "
                                 "call fails: 'Without …, or when a call fails, …'")
                self.assertRegex(text, ENDS_WITH_RULE, f"end the section with '{RULE} yourself.'")
                self.assertNotRegex(text.replace(RULE, ""), SETUP,
                                    "leave installing a server to the user: no setup step")
                self.assertTrue(any(server in text for server in SERVERS),
                                f"name the server: one of {SERVERS}")

    def test_mcp_guidance_lives_in_the_section(self):
        """A misspelled heading, or guidance left elsewhere, would escape every other check."""
        for path in sorted(ROOT.glob("skills/*/*/SKILL.md")):
            if not re.search(r"\bMCP\b|Geocontext", path.read_text(encoding="utf-8")):
                continue
            with self.subTest(skill=path.parent.name):
                self.assertIn(path.parent.name, self.skills,
                              f"an MCP server is mentioned without a '{HEADING}' section")

    def test_the_section_comes_before_the_prerequisites(self):
        for name, path in self.skills.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(skill=name):
                self.assertLess(text.index(f"\n{HEADING}\n"), text.index("\n## Prerequisites\n"),
                                "an agent must read the MCP route before the local tools")

    def test_geocontext_tool_names_are_not_taken_for_granted(self):
        """Tool names differ between Geocontext versions: name the version or the tool list."""
        for name, path in self.skills.items():
            text = section(path)
            if not GPF_TOOL.search(text):
                continue
            with self.subTest(skill=name):
                self.assertRegex(text, OTHER_VERSIONS,
                                 "name the Geocontext version or tell the agent to read the tool list")

    def test_a_database_is_only_read(self):
        for name, path in self.skills.items():
            text = section(path)
            if "PostGIS" not in text:
                continue
            with self.subTest(skill=name):
                self.assertIn(READ_ONLY, text)
                self.assertIn("never ask for database credentials", text)

    def test_the_qgis_session_changes_only_on_request(self):
        for name, path in self.skills.items():
            text = section(path)
            if "QGIS MCP server" not in text:
                continue
            with self.subTest(skill=name):
                self.assertGreaterEqual(len(SESSION_GUARD.findall(text)), SESSION_GUARDS.get(name, 1),
                                        "say that the user's project changes only when asked")

    def test_readmes_and_guide_list_the_same_skills(self):
        readmes = skills_with_section("README.md")
        guide = (ROOT / "docs" / "mcp-servers.md").read_text(encoding="utf-8")
        table = guide.split("## Skills and servers", 1)[1].split("\n## ", 1)[0]
        listed = set(re.findall(r"^\| \[([a-z0-9-]+)\]\(\.\./skills/", table, flags=re.M))
        self.assertEqual(set(readmes), set(self.skills), "skill READMEs with an MCP section")
        self.assertEqual(listed, set(self.skills), "rows of docs/mcp-servers.md")
        for name, path in readmes.items():
            with self.subTest(readme=name):
                self.assertTrue(section(path).startswith("Optional."),
                                "start the README section with 'Optional.'")
        others = table.split("The other skills", 1)[1].split("\n\n", 1)[0]
        every = {path.parent.name for path in ROOT.glob("skills/*/*/SKILL.md")}
        self.assertEqual(set(re.findall(r"`([a-z0-9-]+)`", others)), every - set(self.skills),
                         "the skills without an MCP route listed in docs/mcp-servers.md")


if __name__ == "__main__":
    unittest.main()
