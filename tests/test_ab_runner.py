"""Exercise the documented A/B runner without making any agent or network calls."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("bash"), "The A/B runner requires Bash")
class ABRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="geoskills-ab-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.campaign = self.directory / "campaign"
        self.runner = self.directory / "ab.sh"
        document = (ROOT / "tests/ab-testing.md").read_text(encoding="utf-8")
        self.runner.write_text(document.split("```bash\n", 1)[1].split("\n```", 1)[0])

    def run_shell(self, command, *, dry=False, exit_code=0, transcript=None, root=ROOT):
        if transcript is None:
            transcript = {"type": "result", "is_error": False, "result": "synthetic result"}
        script = '''
source "$1"
export GEOSKILLS="$2" AB="$3" AB_DRY="$4"
claude() {
  printf 'called\n' >> "$AB/agent-invocations.txt"
  printf '%s\n' "$FAKE_TRANSCRIPT"
  return "$FAKE_EXIT"
}
''' + command
        return subprocess.run(
            ["bash", "-c", script, "bash", str(self.runner), str(root),
             str(self.campaign), "1" if dry else "0"],
            env=dict(os.environ, FAKE_EXIT=str(exit_code),
                     FAKE_TRANSCRIPT=json.dumps(transcript)),
            text=True, capture_output=True, timeout=60,
        )

    def test_dry_campaign_covers_every_scenario_with_isolated_inputs(self):
        result = self.run_shell("ab_campaign 1", dry=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        skills = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
        expected = set()
        for skill in skills:
            scenarios = (ROOT / "tests" / f"{skill}.md").read_text(encoding="utf-8")
            for identifier in re.findall(r"^## ([A-Z]+-(?:N)?\d+)\s", scenarios, re.M):
                expected.add((identifier, "with-1"))
                if "-N" not in identifier:
                    expected.add((identifier, "without-1"))
        runs = list((self.campaign / "runs").glob("*/*"))
        self.assertEqual({(p.parent.name, p.name) for p in runs}, expected)
        for run in runs:
            with self.subTest(run=run.relative_to(self.campaign)):
                self.assertTrue((run / "prompt.txt").read_text().strip())
                self.assertTrue((run / "data/saint_mande.geojson").is_file())
                installed = {p.name for p in (run / ".claude/skills").glob("*")}
                self.assertEqual(installed, skills if run.name == "with-1" else set())
        self.assertFalse((self.campaign / "agent-invocations.txt").exists())

    def test_missing_prerequisite_stops_before_creating_a_run(self):
        result = self.run_shell("ab_run WFS-03 with 1 WFS-01", dry=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.campaign / "runs/WFS-03/with-1").exists())
        self.assertFalse((self.campaign / "agent-invocations.txt").exists())

    def test_missing_fixture_data_never_calls_an_agent(self):
        incomplete = self.directory / "incomplete-repository"
        (incomplete / "tests").mkdir(parents=True)
        shutil.copyfile(ROOT / "tests/mapshaper-simplify.md",
                        incomplete / "tests/mapshaper-simplify.md")
        result = self.run_shell("ab_run MS-01 with 1", root=incomplete)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.campaign / "agent-invocations.txt").exists())

    def test_failed_process_cannot_be_reported_as_success(self):
        result = self.run_shell('POSITIVE="MS-01 MS-02"; ab_campaign 1', exit_code=42)
        self.assertNotEqual(result.returncode, 0)
        summary = json.loads((self.campaign / "runs/MS-01/with-1/summary.json").read_text())
        self.assertEqual(summary["exit_code"], 42)
        self.assertFalse(summary["ok"])
        self.assertEqual((self.campaign / "agent-invocations.txt").read_text(), "called\n")

    def test_missing_or_error_result_stops_the_campaign(self):
        for transcript in ({"type": "system"}, {"type": "result", "is_error": True}):
            with self.subTest(transcript=transcript):
                self.campaign = self.directory / ("error" if transcript.get("is_error") else "missing")
                result = self.run_shell('POSITIVE="MS-01 MS-02"; ab_campaign 1', transcript=transcript)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((self.campaign / "agent-invocations.txt").read_text(), "called\n")

    def test_successful_process_is_recorded(self):
        result = self.run_shell("ab_run MS-01 with 1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads((self.campaign / "runs/MS-01/with-1/summary.json").read_text())
        self.assertEqual(summary["exit_code"], 0)
        self.assertTrue(summary["ok"])


if __name__ == "__main__":
    unittest.main()
