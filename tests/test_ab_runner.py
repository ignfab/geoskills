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
                     FAKE_TRANSCRIPT="\n".join(json.dumps(event) for event in (
                         transcript if isinstance(transcript, list) else [transcript]))),
            text=True, capture_output=True, timeout=60,
        )

    def test_dry_campaign_covers_every_scenario_with_isolated_inputs(self):
        result = self.run_shell("ab_campaign 1", dry=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        skills = {p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md")}
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

    def test_experimental_prompt_runs_like_a_scenario(self):
        result = self.run_shell("ab_run XP-05 with x1", dry=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        run = self.campaign / "runs/XP-05/with-x1"
        prompt = (run / "prompt.txt").read_text(encoding="utf-8")
        self.assertTrue(prompt.startswith("Quelle part de la commune de Saint-Mandé"), prompt)
        self.assertTrue((run / ".claude/skills/geopf-routing/SKILL.md").is_file())
        self.assertTrue((run / "data/saint_mande.geojson").is_file())
        self.assertFalse((self.campaign / "agent-invocations.txt").exists())

    def test_reusing_a_run_preserves_its_results(self):
        first = self.run_shell("ab_run MS-01 with 1")
        self.assertEqual(first.returncode, 0, first.stderr)
        output = self.campaign / "runs/MS-01/with-1/output/keep.txt"
        output.write_text("previous result")
        second = self.run_shell("ab_run MS-01 with 1")
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(output.read_text(), "previous result")
        self.assertEqual((self.campaign / "agent-invocations.txt").read_text(), "called\n")

    def test_prerequisite_outputs_are_copied_without_sharing_files(self):
        result = self.run_shell('''
ab_run WFS-01 with 1 || exit 1
printf 'source result' > "$AB/runs/WFS-01/with-1/output/communes.gpkg"
ab_run WFS-03 with 1 WFS-01
''', dry=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        before = self.campaign / "runs/WFS-01/with-1/output/communes.gpkg"
        after = self.campaign / "runs/WFS-03/with-1/output/communes.gpkg"
        self.assertEqual(after.read_bytes(), before.read_bytes())
        after.write_text("changed by dependent scenario")
        self.assertEqual(before.read_text(), "source result")
        self.assertFalse((self.campaign / "agent-invocations.txt").exists())

    def test_invalid_comparisons_are_preserved_in_summary_and_report(self):
        cases = [
            ("skill", "without", "Skill", {"skill": "mapshaper-simplify"}, True, 0),
            ("read", "without", "Read", {"file_path": "/repo/skills/mapshaper-simplify/SKILL.md"}, True, 0),
            ("install", "with", "Bash", {"command": "python3 -m pip install geopandas"}, False, 1),
        ]
        for name, mode, tool, arguments, contaminated, installs in cases:
            with self.subTest(case=name):
                self.campaign = self.directory / name
                transcript = [
                    {"type": "assistant", "message": {"content": [
                        {"type": "tool_use", "name": tool, "input": arguments}]}},
                    {"type": "result", "is_error": False, "result": "done"},
                ]
                result = self.run_shell(f"ab_run MS-01 {mode} 1", transcript=transcript)
                self.assertNotEqual(result.returncode, 0)
                run = self.campaign / f"runs/MS-01/{mode}-1"
                summary = json.loads((run / "summary.json").read_text())
                self.assertTrue(summary["ok"])  # Process success is not evaluation validity.
                self.assertEqual(summary["contaminated"], contaminated)
                self.assertEqual(summary["install_attempts"], installs)
                self.assertFalse(summary["comparable"])
                report = self.run_shell("ab_report")
                self.assertEqual(report.returncode, 0, report.stderr)
                self.assertIn("INVALID", (self.campaign / "report.md").read_text())

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

    def test_dry_sweep_prepares_one_isolated_campaign_per_model(self):
        result = self.run_shell('AB_MODELS="model-a model-b"; ab_sweep 1 MS-01 MS-N1 WFS-01 WFS-03',
                                dry=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        skills = {p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md")}
        for model in ("model-a", "model-b"):
            runs = self.campaign / "models" / model / "runs"
            with self.subTest(model=model):
                self.assertEqual({(p.parent.name, p.name) for p in runs.glob("*/*")},
                                 {(i, "with-1") for i in ("MS-01", "MS-N1", "WFS-01", "WFS-03")})
                self.assertEqual({p.name for p in (runs / "MS-N1/with-1/.claude/skills").glob("*")},
                                 skills)
        self.assertFalse((self.campaign / "runs").exists())
        self.assertFalse(list(self.campaign.rglob("agent-invocations.txt")))

    def test_panel_holds_the_first_positive_and_negative_of_each_skill(self):
        result = self.run_shell("ab_panel")
        self.assertEqual(result.returncode, 0, result.stderr)
        panel = result.stdout.split()
        skills = {p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md")}
        self.assertEqual(len(panel), 2 * len(skills))
        self.assertTrue(all(re.fullmatch(r"[A-Z]+-(01|N1)", i) for i in panel), panel)

    def test_sweep_calls_each_model_and_scores_selection_per_model(self):
        # model-a loads mapshaper-simplify for every prompt, model-b loads no skill.
        result = self.run_shell('''
export CALLS="$AB/calls.txt" AB_MODELS="model-a model-b"
claude() {
  local model=
  while [ $# -gt 0 ]; do [ "$1" = --model ] && model=$2; shift; done
  printf '%s\\n' "$model" >> "$CALLS"
  printf '{"type":"system","subtype":"init","model":"%s-id"}\\n' "$model"
  [ "$model" = model-a ] && printf '%s\\n' '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"mapshaper-simplify"}}]}}'
  printf '%s\\n' '{"type":"result","is_error":false,"result":"done","num_turns":3,"total_cost_usd":0.5}'
}
ab_sweep 1 MS-01 GPD-N1 || exit 1
for model in $AB_MODELS; do AB="$AB/models/$model" ab_report >/dev/null || exit 1; done
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        # All models of a scenario run back to back.
        self.assertEqual((self.campaign / "calls.txt").read_text().split(),
                         ["model-a", "model-b", "model-a", "model-b"])
        for model, verdict in (("model-a", "pass"), ("model-b", "fail")):  # hand scores
            report = self.campaign / "models" / model / "report.md"
            lines = report.read_text().splitlines()
            for n, line in enumerate(lines):
                if line.startswith("| MS-01 | with | 1 |"):
                    cells = line.strip("|").split("|")
                    cells[8] = f" {verdict} "
                    lines[n] = "|" + "|".join(cells) + "|"
            report.write_text("\n".join(lines) + "\n")
        invalid = self.campaign / "models/model-c/runs/MS-01/with-1"
        invalid.mkdir(parents=True)
        (invalid / "summary.json").write_text(json.dumps(dict(
            scenario="MS-01", mode="with", rep="1", model="model-c-id", skills=["mapshaper-simplify"],
            turns=2, cost_usd=0.25, ok=True, comparable=False)))
        result = self.run_shell('AB_MODELS="model-a model-b"; ab_sensitivity')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = (self.campaign / "sensitivity.md").read_text()
        self.assertIn("Models: model-a (model-a-id); model-b (model-b-id); model-c (model-c-id)", report)
        selection, rest = report.split("## Skill selection (automatic)")[1].split("## Task result")
        results, rest = rest.split("## Cost and invalid runs")
        # MS-01 expects mapshaper-simplify; GPD-N1 must not load geopandas-basics.
        self.assertIn("| mapshaper-simplify | 1/1 | 0/1 | — | 100 % | SENSITIVE |", selection)
        self.assertIn("| geopandas-basics | 1/1 | 1/1 | — | 0 % |  |", selection)
        self.assertIn("| mapshaper-simplify | 1/1 | 0/1 | — | 100 % | SENSITIVE |", results)
        self.assertNotIn("geopandas-basics", results)  # GPD-N1 was not hand-scored
        self.assertIn("| model-a | 2 | 0 | 1.00 | 3.0 |", rest)
        self.assertIn("| model-c | 1 | 1 | 0.25 | 2.0 |", rest)
        self.assertIn("| MS-01 | 1 | ok: mapshaper-simplify; pass | FAIL: -; fail | invalid |", rest)
        self.assertIn("| GPD-N1 | 1 | ok: mapshaper-simplify | ok: - | — |", rest)
        # A spread equal to the threshold is flagged; a higher threshold clears it.
        for spread, flag in (("1", "SENSITIVE"), ("101/100", "")):
            result = self.run_shell(f'AB_MODELS="model-a model-b" AB_SPREAD={spread}; ab_sensitivity')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"| mapshaper-simplify | 1/1 | 0/1 | — | 100 % | {flag} |",
                          (self.campaign / "sensitivity.md").read_text())

    def test_successful_process_is_recorded(self):
        result = self.run_shell("ab_run MS-01 with 1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads((self.campaign / "runs/MS-01/with-1/summary.json").read_text())
        self.assertEqual(summary["exit_code"], 0)
        self.assertTrue(summary["ok"])
        self.assertTrue(summary["comparable"])
        self.assertFalse(summary["contaminated"])


if __name__ == "__main__":
    unittest.main()
