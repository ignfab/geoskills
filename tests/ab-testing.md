# A/B testing the skills

This protocol measures what each skill adds. Every positive scenario in `tests/<skill>.md`
is run twice under the same conditions: **A** with the skills of this repository installed,
**B** without them. A higher pass rate in A is evidence of added value on those scenarios;
when both pass, compare effort and cost as well as output quality.

A [model sweep](#model-sensitivity) runs the same scenarios with several models, to find
skills whose effect depends on the model that reads them.

The scenario files remain the reference for prompts, expected results and checklists.
This file adds the procedure, a runner and a scoring grid.

## A campaign in five steps

1. **Prepare the machine:** install the tools of [Prerequisites](#prerequisites) and the
   `claude` CLI; the runner never installs anything.
2. **Save the runner:** copy the [Runner](#runner) block to `ab.sh` outside the repository
   and `source` it.
3. **Dry run, free:** `AB_DRY=1 ab_campaign 1` prepares every run directory without calling
   an agent ([Run the campaign](#run-the-campaign)).
4. **Paid runs, on a separate decision:** a smoke pass of one repetition, then three
   repetitions; `ab_report` builds `report.md` with one row per run.
5. **Score and conclude:** fill in each row with the [scoring grid](#score-a-run), then
   summarize per skill and [interpret](#interpret) the difference between A and B.

| Section | Use it to |
| --- | --- |
| [Principle](#principle) | Understand what keeps A and B comparable |
| [Prerequisites](#prerequisites) | Check tools, grids and budgets before a campaign |
| [Runner](#runner) | Copy the shell functions that prepare, run and report |
| [Run the campaign](#run-the-campaign) | Start a dry run, a smoke pass or full repetitions |
| [Scenario matrix](#scenario-matrix) | See, per skill, which modes each scenario runs in, what it needs and what to watch without the skills |
| [Score a run](#score-a-run) and [Interpret](#interpret) | Turn runs into pass rates and conclusions |
| [Model sensitivity](#model-sensitivity) | Run the same scenarios with several models |
| [Variants](#variants), [Experimental prompts](#experimental-prompts), [Limits](#limits) | Adapt the protocol and know what it cannot show |

## Principle

- **One variable.** A and B differ only by `.claude/skills/` in the run directory: same
  prompt, data, model, budget and allowed tools. Choose the same model version in both modes.
- **Outside the repository.** Runs happen under `$AB`, not under `tests/`. Inside the
  clone, the agent loads the root `CLAUDE.md` and can read `skills/`, which contaminates B.
- **A fresh directory per run.** Each run gets its own copy of `data/` and an empty
  `output/`, and starts a new session. The runner refuses to reuse a directory, but global
  instructions and skills still apply; check the contamination limits below.
- **A then B, back to back.** Live services change; running both modes of a scenario
  together keeps their data comparable.
- **Repetitions.** Agent runs are not deterministic: after a one-repetition smoke pass, run
  each scenario three times per mode and compare pass rates.
- **Negative scenarios (`-N`) run in A only.** They check that the wrong skill is not
  selected, which has no meaning without skills.

## Prerequisites

The runner needs the `claude` CLI and Python 3. The scenarios need the tools listed in the
[scenario matrix](#scenario-matrix). The user must install any missing tools before the
campaign; the runner denies common installation commands:

- GDAL ≥ 3.1 that starts (`gdalinfo --version`); GDAL ≥ 3.12 for the
  `gdal raster zonal-stats` path of RAS-05 and the `gdal vector check-coverage` path of
  VDQ-03;
- PROJ with the IGN grids `fr_ign_ntf_r93.tif` (CRS-02) and `fr_ign_RAF18.tif` (CRS-04),
  for example with `projsync --source-id fr_ign`;
- `python3 -m pip install -r tests/requirements-geospatial.txt` for the GPD and VDQ
  scenarios;
- Mapshaper 0.7.83 and compatible Node.js for the MS scenarios; see
  [Mapshaper requirements](../skills/5-publish/mapshaper-simplify/README.md#requirements);
- QGIS/PyQGIS 3.34–3.x for QLS/QPB; record `Qgis.QGIS_VERSION` and use
  `QT_QPA_PLATFORM=offscreen` for headless runs, with `GDAL_PAM_ENABLED=NO` for raster reads;
- network access to `data.geopf.fr` for the GEO, WFS and WMS scenarios, and to
  `apicarto.ign.fr` for the APC scenarios.

A missing tool fails both modes and hides the effect of the skill. `ab_env` records the
versions at the top of the report so that such runs can be excluded.

## Runner

Save the block below as `ab.sh`, outside the repository, check the variables at the top,
then load it with `source ab.sh`.

```bash
export GEOSKILLS="${GEOSKILLS:-$HOME/projects/geoskills}"  # the repository clone
export AB="${AB:-$HOME/geoskills-ab/$(date +%F)}"          # outside the repository
export AB_MODEL="${AB_MODEL:-opus}"              # same model/version in both modes
export AB_MODELS="${AB_MODELS:-haiku sonnet opus}"  # model panel of ab_sweep
export AB_BUDGET="2"                            # USD cap per run
export AB_TOOLS="Bash Read Write Edit Glob Grep Skill WebFetch WebSearch"
export AB_DENY="Bash(sudo *) Bash(pip install *) Bash(pip3 install *) Bash(python3 -m pip install *) Bash(conda install *) Bash(mamba install *) Bash(apt *) Bash(apt-get *) Bash(brew install *) Bash(npm install *)"
export AB_EXTRA_FLAGS=""                        # extra claude flags, both modes
export AB_WITHOUT_FLAGS=""                      # extra claude flags, B runs only

# Positive scenarios run in A and B; WFS-03 is missing on purpose: ab_campaign runs it
# after WFS-01, whose output it extends. Negative scenarios run in A only.
POSITIVE="GSV-01 GSV-02 GSV-03 GSV-04 GSV-05
GEO-01 GEO-02 GEO-03 GEO-04 GEO-05 GEO-06 CRS-01 CRS-02 CRS-03 CRS-04 CRS-05
RAS-01 RAS-02 RAS-03 RAS-04 RAS-05 RAS-06 WMS-01 WMS-02 WMS-03 WMS-04 WMS-05
WFS-01 WFS-02 WFS-04 WFS-05 WFS-06 WFS-07 CQL-01 CQL-02 CQL-03 CQL-04
GPD-01 GPD-02 GPD-03 GPD-04 VDQ-01 VDQ-02 VDQ-03 MS-01 MS-02 MS-03 MS-04
INT-01 INT-02 DLF-01 DLF-02 ALT-01 ALT-02 RTE-01 RTE-02
GVB-01 GVB-02 GVB-03 GVB-04 APC-01 APC-02 APC-03 GDS-01 GDS-02
QLS-01 QLS-02 SPA-01 SPA-02 BTS-01 BTS-02 QPB-01 QPB-02 MBP-01 MBP-02 MBP-03 TES-01 TES-02 TES-03 MAP-01 MAP-02 MAP-03 MAP-04"
NEGATIVE="GSV-N1 GSV-N2 GEO-N1 CRS-N1 RAS-N1 WMS-N1 WFS-N1 CQL-N1 CQL-N2 GPD-N1 VDQ-N1 VDQ-N2
MS-N1 MS-N2 INT-N1 DLF-N1 ALT-N1 RTE-N1 GVB-N1 GVB-N2 APC-N1 GDS-N1 GDS-N2
QLS-N1 SPA-N1 SPA-N2 BTS-N1 BTS-N2 QPB-N1 MBP-N1 MBP-N2 MBP-N3 ALT-N2 TES-N1 TES-N2 MAP-N1 MAP-N2 MAP-N3"

# Print the French prompt of a scenario or an experimental prompt (XP-NN), read from
# tests/*.md, then tests/prompts/*.md.
ab_prompt() {
  python3 - "$1" "$GEOSKILLS"/tests/*.md "$GEOSKILLS"/tests/prompts/*.md <<'PY'
import os, re, sys
want, paths = sys.argv[1], sys.argv[2:]
for path in paths:
    if not os.path.isfile(path):  # unmatched glob
        continue
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"^## {re.escape(want)}\s", line):
            quote = []
            for nxt in lines[i + 1:]:
                if nxt.startswith(">"):
                    quote.append(nxt[1:].strip())
                elif quote or nxt.startswith("## "):
                    break
            print(" ".join(q for q in quote if q))
            sys.exit(0)
sys.exit(f"scenario {want} not found")
PY
}

# Record tool versions and grids once per campaign.
ab_env() {
  mkdir -p "$AB"
  {
    date -Iseconds
    echo "model: $AB_MODEL"
    echo "model panel: $AB_MODELS"
    claude --version
    node --version
    mapshaper -version
    gdalinfo --version 2>&1 | head -1
    cs2cs 2>&1 | head -1
    ls $(projinfo --searchpaths 2>/dev/null | sed 's|$|/fr_ign_*|') 2>/dev/null \
      || echo "IGN grids: none found"
    python3 -c "import geopandas as g, shapely as s; print('geopandas', g.__version__, 'shapely', s.__version__)" \
      2>/dev/null || echo "geopandas: not installed"
    python3 -c "import rasterstats as r; print('rasterstats', r.__version__)" 2>/dev/null \
      || echo "rasterstats: not installed"
  } | tee "$AB/environment.txt"
}

# Run one scenario in a fresh directory: ab_run <scenario> <with|without> [rep] [after]
ab_run() {
  : "${GEOSKILLS:?}" "${AB:?}"
  local id=$1 mode=$2 rep=${3:-1} after=${4:-} prompt flags=$AB_EXTRA_FLAGS status=0 skill
  local dir="$AB/runs/$id/$mode-$rep"
  case $mode in with|without) ;; *) echo "mode must be with or without" >&2; return 1 ;; esac
  [ -e "$dir" ] && { echo "$dir exists: use another rep or AB" >&2; return 1; }
  prompt=$(ab_prompt "$id") || return 1
  [ -n "$prompt" ] || { echo "$id has no prompt" >&2; return 1; }
  if [ -n "$after" ] && [ ! -d "$AB/runs/$after/$mode-$rep/output" ]; then
    echo "Missing prerequisite output: $after $mode-$rep" >&2
    return 1
  fi
  mkdir -p "$dir/output" || return 1
  cp -r "$GEOSKILLS/tests/data" "$dir/data" || return 1
  if [ "$mode" = with ]; then
    mkdir -p "$dir/.claude/skills" || return 1
    # Flat copies, as the Skills CLI installs them: .claude/skills/<skill-name>/
    for skill in "$GEOSKILLS"/skills/*/*/SKILL.md; do
      cp -r "${skill%/SKILL.md}" "$dir/.claude/skills/" || return 1
    done
  fi
  if [ -n "$after" ]; then
    cp -r "$AB/runs/$after/$mode-$rep/output/." "$dir/output/" || return 1
  fi
  printf '%s\n' "$prompt" > "$dir/prompt.txt" || return 1
  if [ "${AB_DRY:-0}" = 1 ]; then echo "$dir"; return 0; fi
  [ "$mode" = without ] && flags="$flags $AB_WITHOUT_FLAGS"
  echo "== $id $mode-$rep"
  (cd "$dir" && claude -p "$prompt" \
      --model "$AB_MODEL" \
      --max-budget-usd "$AB_BUDGET" \
      --output-format stream-json --verbose \
      --no-session-persistence \
      --allowedTools "$AB_TOOLS" \
      --disallowedTools "$AB_DENY" \
      $flags \
      > transcript.jsonl) || status=$?
  printf '%s\n' "$status" > "$dir/exit-code.txt" || return 1
  ab_summary "$dir" || return 1
  return "$status"
}

# One repetition of every scenario: A and B for positives, A only for negatives.
ab_campaign() {
  local rep=${1:-1} id
  for id in $POSITIVE; do
    ab_run "$id" with "$rep" || return 1
    ab_run "$id" without "$rep" || return 1
  done
  ab_run WFS-03 with "$rep" WFS-01 || return 1
  ab_run WFS-03 without "$rep" WFS-01 || return 1
  for id in $NEGATIVE; do ab_run "$id" with "$rep" || return 1; done
}

# Extract skills loaded, commands, final answer, cost and turns from a transcript.
ab_summary() {
  python3 - "$1" <<'PY'
import json, os, pathlib, re, sys
d = pathlib.Path(sys.argv[1])
ours = {p.parent.name for p in pathlib.Path(os.environ["GEOSKILLS"], "skills").glob("*/*/SKILL.md")}
mode, rep = d.name.rsplit("-", 1)
exit_code = int((d / "exit-code.txt").read_text())
skills, files, cmds, result, model = [], [], [], {}, None
for line in (d / "transcript.jsonl").read_text(encoding="utf-8").splitlines():
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") == "system" and ev.get("subtype") == "init":
        model = ev.get("model")
    if ev.get("type") == "result":
        result = ev
    if ev.get("type") != "assistant":
        continue
    for c in ev.get("message", {}).get("content", []):
        if not isinstance(c, dict) or c.get("type") != "tool_use":
            continue
        inp = c.get("input") or {}
        if c.get("name") == "Skill" and inp.get("skill") not in skills:
            skills.append(inp.get("skill"))
        elif c.get("name") == "Bash":
            cmds.append(inp.get("command", ""))
        elif c.get("name") == "Read":
            files.append(inp.get("file_path", ""))
skill_files = [p for p in files + cmds if "/skills/" in p]
installs = [c for c in cmds
            if re.search(r"\bsudo\b|\b(pip3?|conda|mamba|apt(-get)?|brew|npm)\s+install\b", c)]
contaminated = mode == "without" and bool(skill_files or set(skills) & ours)
summary = {
    "scenario": d.parent.name, "mode": mode, "rep": rep, "model": model,
    "skills": skills, "skill_file_reads": len(skill_files),
    "install_attempts": len(installs),
    "turns": result.get("num_turns"), "cost_usd": result.get("total_cost_usd"),
    "duration_s": round(result.get("duration_ms", 0) / 1000),
    "exit_code": exit_code,
    "ok": exit_code == 0 and bool(result) and not result.get("is_error"),
    "contaminated": contaminated,
}
# Process success alone does not make an A/B run usable or its task result correct.
summary["comparable"] = summary["ok"] and not contaminated and not installs
(d / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(d / "answer.md").write_text(str(result.get("result", "")) + "\n", encoding="utf-8")
(d / "commands.txt").write_text("\n\n".join(cmds) + "\n", encoding="utf-8")
flag = "  <-- INVALID: skill used in a run without skills" if contaminated else ""
print(f"{summary['scenario']} {mode}-{rep}: model={model} skills={','.join(skills) or '-'} "
      f"turns={summary['turns']} cost={summary['cost_usd']} "
      f"time={summary['duration_s']}s installs={len(installs)}{flag}")
sys.exit(0 if summary["comparable"] else 1)
PY
}

# Build $AB/report.md: one row per run, with blank columns to score by hand.
ab_report() {
  python3 - "$AB" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
rows = sorted((json.loads(p.read_text(encoding="utf-8"))
               for p in root.glob("runs/*/*/summary.json")),
              key=lambda s: (s["scenario"], s["mode"] != "with", s["rep"]))
env = root / "environment.txt"
out = ["## Environment", "", "```text", env.read_text(encoding="utf-8").strip() if env.exists() else "not recorded", "```", "",
       "## Runs", "",
       "Models: " + ", ".join(sorted({str(s.get("model")) for s in rows})), "",
       "| Scenario | Mode | Rep | Skills loaded | Turns | Cost $ | Time s | Installs | Result | Checklist | Notes |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
for s in rows:
    # Missing comparability evidence in old summaries requires manual review.
    status = "ERROR" if not s["ok"] else (
        "INVALID" if s.get("comparable") is False else (
            "CHECK" if "comparable" not in s else ""))
    out.append(f"| {s['scenario']} | {s['mode']} | {s['rep']} | {', '.join(s['skills']) or '-'} "
               f"| {s['turns']} | {s['cost_usd']} | {s['duration_s']} | {s['install_attempts']} "
               f"| {status} | | |")
for mode in ("with", "without"):
    cost = sum(s["cost_usd"] or 0 for s in rows if s["mode"] == mode)
    out.append(f"\nTotal cost {mode}: {cost:.2f} $")
(root / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(root / "report.md")
PY
}
# First positive and first negative scenario of each skill: the model-sweep panel.
ab_panel() {
  local id
  for id in $POSITIVE $NEGATIVE; do
    case $id in *-01|*-N1) printf '%s\n' "$id" ;; esac
  done
}

# Model sensitivity: run scenarios in A only, once per model of AB_MODELS, all models of a
# scenario back to back. Each model gets its own campaign, $AB/models/<model>/.
# ab_sweep [rep] [scenario...]; without scenarios, every scenario.
ab_sweep() {
  : "${AB:?}" "${AB_MODELS:?}"
  local rep=${1:-1} root=$AB id model after
  shift $(($# > 0 ? 1 : 0))
  for id in ${*:-$POSITIVE WFS-03 $NEGATIVE}; do
    after=
    [ "$id" = WFS-03 ] && after=WFS-01
    for model in $AB_MODELS; do
      AB="$root/models/$model" AB_MODEL="$model" ab_run "$id" with "$rep" $after || return 1
    done
  done
}

# Build $AB/sensitivity.md from an ab_sweep: skill selection scored automatically for every
# run, task results read from the hand-scored models/<model>/report.md, spread per skill.
ab_sensitivity() {
  python3 - "$AB" "$GEOSKILLS" "${AB_SPREAD:-1/3}" "$AB_MODELS" <<'PY'
import json, pathlib, re, sys
from fractions import Fraction
root, repo, limit = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), Fraction(sys.argv[3])
owner = {}  # scenario -> skill whose tests/<skill>.md defines it
for path in repo.glob("skills/*/*/SKILL.md"):
    scenarios = repo / "tests" / f"{path.parent.name}.md"
    if scenarios.exists():
        for ident in re.findall(r"^## ([A-Z]+-N?\d+)\s", scenarios.read_text(encoding="utf-8"), re.M):
            owner[ident] = path.parent.name
found = sorted(p.name for p in (root / "models").glob("*") if p.is_dir())
models = [m for m in sys.argv[4].split() if m in found] + [m for m in found if m not in sys.argv[4].split()]

def hand_scores(model):
    """(scenario, rep) -> True/False from the Result column of a scored report.md."""
    path, scores = root / "models" / model / "report.md", {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) > 8 and cells[1] == "with" and cells[8].lower() in ("pass", "fail"):
                scores[(cells[0], cells[2])] = cells[8].lower() == "pass"
    return scores

runs, selection, result, ids, totals = {}, {}, {}, {}, {}
for model in models:
    scores = hand_scores(model)
    total = totals.setdefault(model, {"runs": 0, "invalid": 0, "cost": 0.0, "turns": 0})
    for path in sorted((root / "models" / model / "runs").glob("*/with-*/summary.json")):
        s = json.loads(path.read_text(encoding="utf-8"))
        skill = owner.get(s["scenario"])
        if skill is None:
            continue  # experimental prompt: no expected skill
        ids.setdefault(model, set()).add(str(s.get("model")))
        total["runs"] += 1
        total["cost"] += s.get("cost_usd") or 0
        total["turns"] += s.get("turns") or 0
        key = (s["scenario"], s["rep"])
        if not s.get("comparable", s.get("ok")):
            total["invalid"] += 1
            runs.setdefault(key, {})[model] = "invalid"
            continue
        loaded = skill in s["skills"]
        hit = not loaded if "-N" in s["scenario"] else loaded
        counts = selection.setdefault(skill, {}).setdefault(model, [0, 0])
        counts[0] += hit
        counts[1] += 1
        cell = ("ok" if hit else "FAIL") + ": " + (", ".join(map(str, s["skills"])) or "-")
        if key in scores:
            counts = result.setdefault(skill, {}).setdefault(model, [0, 0])
            counts[0] += scores[key]
            counts[1] += 1
            cell += "; " + ("pass" if scores[key] else "fail")
        runs.setdefault(key, {})[model] = cell

def table(title, data, note):
    out = [f"## {title}", "", note, "",
           "| Skill | " + " | ".join(models) + " | Spread | Flag |",
           "|---|" + "---|" * len(models) + "---|---|"]
    for skill in sorted(data):
        rates = [Fraction(*data[skill][m]) for m in models if data[skill].get(m, [0, 0])[1]]
        spread = max(rates) - min(rates) if len(rates) > 1 else None
        flag = "SENSITIVE" if spread is not None and spread >= limit else ""
        cells = ["{}/{}".format(*data[skill][m]) if m in data[skill] else "—" for m in models]
        shown = "—" if spread is None else f"{round(100 * spread)} %"
        out.append(f"| {skill} | " + " | ".join(cells) + f" | {shown} | {flag} |")
    return out + [""]

out = ["# Model sensitivity", "",
       "Models: " + "; ".join(f"{m} ({', '.join(sorted(ids[m]))})" if m in ids else m for m in models), "",
       f"A skill is flagged when the best and the worst model differ by at least {limit} of their runs.", ""]
out += table("Skill selection (automatic)", selection,
             "Correct runs / scored runs: the expected skill loaded for a positive scenario, "
             "the excluded skill not loaded for a negative one. Invalid runs are left out.")
out += table("Task result (hand scores)", result,
             "Runs written `pass` / runs written `pass` or `fail` in the Result column of "
             "`models/<model>/report.md`.")
out += ["## Cost and invalid runs", "", "| Model | Runs | Invalid | Cost $ | Mean turns |", "|---|---|---|---|---|"]
for m in models:
    t = totals[m]
    mean = f"{t['turns'] / t['runs']:.1f}" if t["runs"] else "—"
    out.append(f"| {m} | {t['runs']} | {t['invalid']} | {t['cost']:.2f} | {mean} |")
out += ["", "## Runs", "", "| Scenario | Rep | " + " | ".join(models) + " |", "|---|---|" + "---|" * len(models)]
for (ident, rep), cells in sorted(runs.items()):
    out.append(f"| {ident} | {rep} | " + " | ".join(cells.get(m, "—") for m in models) + " |")
(root / "sensitivity.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(root / "sensitivity.md")
PY
}
```

| Function | Role |
|----------|------|
| `ab_env` | Records the date, model, tool versions and IGN grids in `$AB/environment.txt`. |
| `ab_prompt <id>` | Prints the prompt of a scenario, read from `tests/*.md`, or of an experimental prompt, read from `tests/prompts/*.md`. |
| `ab_run <id> <with\|without> [rep] [after]` | Creates `$AB/runs/<id>/<mode>-<rep>/`, copies `data/` (and the skills in A), copies the output of the `after` run, runs `claude -p` and keeps `transcript.jsonl`. |
| `ab_campaign [rep]` | One repetition of every scenario. |
| `ab_summary <dir>` | Writes `summary.json`, `commands.txt` (Bash commands run) and `answer.md` (final answer). Rejects detected contamination in B and installation attempts. |
| `ab_report` | Writes `$AB/report.md`: the environment and one row per run, with blank columns to score. It rewrites the file: score after the last repetition. |
| `ab_panel` | Prints the first positive and first negative scenario of each skill, the panel of a [model sweep](#model-sensitivity). |
| `ab_sweep [rep] [id…]` | Runs the given scenarios (all by default) in A only, once per model of `AB_MODELS`, each model in `$AB/models/<model>/`. |
| `ab_sensitivity` | Writes `$AB/sensitivity.md`: skill selection scored for every sweep run, hand-scored results, spread between models per skill. |

`claude -p` cannot ask for permission, so the allowed tools are listed in `AB_TOOLS`. The
agent can run shell commands and reach the web. The deny list and install counter cover
common spellings, not every possible installer invocation; they are not a sandbox.
Run the campaign in a disposable environment and cap the cost with `AB_BUDGET`.
`AB_DRY=1` prepares a run directory without starting the agent.
Preparation or agent failures, detected contamination and installation attempts stop the
campaign; inspect the failing run before using a
new repetition or campaign directory. Missing prerequisites must not count as skill failures.
`ok` records process completion; `comparable` excludes detected contamination and conduct
violations. Neither field scores the task result. The report retains `INVALID` for those
runs and `CHECK` for historical summaries without comparability evidence.

## Run the campaign

Prepare all directories without calling an agent first:

```bash
source ab.sh
AB_DRY=1 ab_campaign 1
```

Then set `export AB=/path/to/a/new/campaign` for actual agent calls. One repetition has **206 runs**:
84 positive scenarios in both modes and 38 negatives in A. At the example budget of $2 per
run, the caps total $412 per repetition and $1236 for three repetitions. Starting the paid
campaign is a separate user decision; a dry run does not authorize it.

Smoke pass, one repetition:

```bash
source ab.sh
ab_env
ab_campaign 1
ab_report
```

Read `$AB/report.md` before going further: environment failures, runs in error, total
cost. Then run the other two repetitions:

```bash
ab_campaign 2
ab_campaign 3
ab_report
```

One scenario, or the scenarios of one skill:

```bash
ab_run GEO-02 with 1 && ab_run GEO-02 without 1
for id in GEO-01 GEO-02 GEO-03 GEO-04 GEO-05; do ab_run "$id" with 1; ab_run "$id" without 1; done
```

To watch the agent, prepare the directory, start an interactive session there and paste
the prompt. Interactive runs have no `transcript.jsonl`: score them by hand.

```bash
cd "$(AB_DRY=1 ab_run GEO-04 with live)" && cat prompt.txt && claude --model "$AB_MODEL"
```

## Scenario matrix

Needs: **NET** public IGN services, **GDAL**, **PROJ** with the named grid, **PY**
GeoPandas stack; **QGIS** installed PyQGIS 3.34–3.x with compatible Qt. *Watch in B* is the trap the skill is meant to prevent: if the skill is
useful, B fails there. *Control* scenarios are expected to pass in both modes; a skill
whose scenarios are all controls adds nothing measurable.

### [geopf-service-selection](geopf-service-selection.md)

These scenarios ask for advice only. No data download, upload, calculation or account is
needed. Web access can check official guides; distinguish advice from live availability.

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| GSV-01 | A + B | — | service selection by output, metadata and access requirements |
| GSV-02 | A + B | — | WMS-V images and vector tiles are not complete analysis features |
| GSV-03 | A + B | — | package discovery, authenticated extraction and standards-validation reports |
| GSV-04 | A + B | — | autocomplete, reverse geocoding, elevation, routing and isochrones distinguished |
| GSV-05 | A + B | — | dataset search and CSW metadata kept separate from address geocoding |
| GSV-N1 | A | — | local reprojection goes directly to `crs-reprojection-france` |
| GSV-N2 | A | — | explicit WFS workflow goes directly to `geopf-wfs-download` |

### [geopf-geocoding](geopf-geocoding.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| GEO-01 | A + B | NET | `data.geopf.fr/geocodage` rather than another geocoder or an API key; `apicarto-query` not loaded in A |
| GEO-02 | A + B | NET | one `POST /search/csv`; `postcode=` given a column name; encoding trap on row 1; rows 6–8 flagged |
| GEO-03 | A + B | NET | lon/lat order (point 3 is in Réunion) |
| GEO-04 | A + B | NET | `index=parcel` and `truegeometry` promoted, or `apicarto-query` `cadastre/parcelle`: a `Point` output fails |
| GEO-05 | A + B | — | control |
| GEO-06 | A + B | — | explicit policy, ambiguity, row conservation and reasons |
| GEO-N1 | A | — | `geopf-geocoding` not loaded, no call to `data.geopf.fr` |

### [crs-reprojection-france](crs-reprojection-france.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| CRS-01 | A + B | PROJ | `latitude` read before `longitude`; Réunion point flagged and given in EPSG:2975 |
| CRS-02 | A + B | PROJ, `fr_ign_ntf_r93.tif` | grid use checked; no centimetric claim without the grid |
| CRS-03 | A + B | GDAL | EPSG:2154 assigned, not reprojected from an assumed WGS84 |
| CRS-04 | A + B | PROJ, `fr_ign_RAF18.tif` | an unchanged 100 m is a failure; missing grid reported, not worked around |
| CRS-05 | A + B | GDAL or PY | control: area in EPSG:2154, not EPSG:3857 |
| CRS-N1 | A | — | `crs-reprojection-france` not loaded; coordinates unchanged |

### [gdal-raster-processing](gdal-raster-processing.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| RAS-01 | A + B | GDAL | control: missing CRS reported |
| RAS-02 | A + B | GDAL | EPSG:2154 assigned to the tiles; cutline reprojected on the fly; COG; no sidecar on the sources |
| RAS-03 | A + B | GDAL | `-tap -r average`, not the default `near` |
| RAS-04 | A + B | GDAL | control |
| RAS-05 | A + B | GDAL ≥ 3.12 or PY | zones reprojected to EPSG:2154, not the DEM; `count = 0` caught |
| RAS-06 | A + B | GDAL | class zero remains valid; no interpolation; full COG check distinguished |
| RAS-N1 | A | NET | `geopf-altimetry` loaded, no DEM tile downloaded |

### [geopf-raster-download](geopf-raster-download.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| WMS-01 | A + B | NET, GDAL | full GetCapabilities URL in the WMTS connection string; empty tiles detected |
| WMS-02 | A + B | NET, GDAL | WMS-R `HIGHRES` in `image/geotiff` Float32, not a coloured image |
| WMS-03 | A + B | NET, GDAL | `PLANIGNV2` through WMTS; box given with `-te_srs EPSG:4326` |
| WMS-04 | A + B | NET | layers listed from current capabilities, not from memory |
| WMS-05 | A + B | NET | no invented SCAN 25 layer |
| WMS-N1 | A | NET | `geopf-wfs-download` loaded |

### [geopf-wfs-download](geopf-wfs-download.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| WFS-01 | A + B | NET, GDAL | namespaced typename; `-spat_srs`; no `-limit`; completeness checked |
| WFS-02 | A + B | NET, GDAL | `-limit 5` in a small box; RFC 7946 output |
| WFS-03 | A + B, after WFS-01 | NET, GDAL | `-update -nln regions`; buildings layer intact; layer name taken from capabilities |
| WFS-04 | A + B | — | missing Parquet writer: GDAL options before any fallback; one file per layer |
| WFS-05 | A + B | — | missing CLI: user-run installation choices, no silent Python substitution |
| WFS-06 | A + B | — | Python proposed only as an agreed last resort, without installing software |
| WFS-07 | A + B | — | equal counts with duplicated source IDs remain unverified |
| WFS-N1 | A | NET | `geopf-raster-download` loaded |

### [geoserver-cql-filter](geoserver-cql-filter.md)

All CQL scenarios use supplied metadata and require no live service.

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| CQL-01 | A + B | — | apostrophe escaping, leading zeros, raw filter encoded exactly once |
| CQL-02 | A + B | — | CRS:84 EWKT axes and separate layer/output CRSs |
| CQL-03 | A + B | — | WMS filter order, EWKT semicolons and map BBOX axes |
| CQL-04 | A + B | — | HTTP 200 exception, no stripping SRID without transformation |
| CQL-N1 | A | — | PostGIS SQL kept separate from ECQL |
| CQL-N2 | A | — | OGC API CQL2 kept separate from GeoServer vendor syntax |

### [geopandas-vector-analysis](geopandas-vector-analysis.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| GPD-01 | A + B | PY | control |
| GPD-02 | A + B | PY | `set_crs(2154)` then `to_crs(4326)` |
| GPD-03 | A + B | PY, GDAL | zones reprojected; raster CRS assigned through a VRT |
| GPD-04 | A + B | PY | one statistic per source row despite filtered or repeated indices; source attributes preserved |
| GPD-N1 | A | NET, GDAL | `geopf-wfs-download` loaded; no Python |

### [vector-data-quality](vector-data-quality.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| VDQ-01 | A + B | PY | null, empty and invalid separated; `make_valid()`; new file re-audited |
| VDQ-02 | A + B | PY | `normalize()` before `duplicated()`; null and empty excluded |
| VDQ-03 | A + B | PY or GDAL ≥ 3.12 | coverage checked, not only `is_valid`; overlap, enclosed gap and narrow gap found; sliver not called a gap |
| VDQ-N1 | A | PY | `geopandas-vector-analysis` loaded, not `vector-data-quality` |
| VDQ-N2 | A | PY | `crs-reprojection-france` loaded, not `vector-data-quality`; no geometry repair |

### [mapshaper-simplify](mapshaper-simplify.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| MS-01 | A + B | Mapshaper, PY | shared borders, string identifiers and small-feature retention |
| MS-02 | A + B | Mapshaper, PY | 100 m tolerance in a suitable projected CRS, then WGS84 export |
| MS-03 | A + B | — | `keep-shapes` does not preserve every multipart island or hole |
| MS-04 | A + B | Mapshaper, PY | independent variants from the source; measured size and geometry changes |
| MS-N1 | A | PY | geometry repair without simplification; `vector-data-quality` selected |
| MS-N2 | A | GDAL | raster resampling handled by `gdal-raster-processing` |

### [geodata-intake](geodata-intake.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| INT-01 | A + B | GDAL | missing CRS retained; sidecars and sources unchanged |
| INT-02 | A + B | — | latitude-first CSV; overseas point |
| INT-N1 | A | GDAL or PY | explicit conversion bypasses inventory |

### [geopf-file-download](geopf-file-download.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| DLF-01 | A + B | NET | paginated discovery and explicit incomplete catalogue |
| DLF-02 | A + B | — | mutable URL cannot safely resume without original identity |
| DLF-N1 | A | — | WFS sample does not trigger full archives |

### [geopf-altimetry](geopf-altimetry.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| ALT-01 | A + B | NET | source discovery, profile sampling, nodata and vertical datum |
| ALT-02 | A + B | — | count/order checked; sentinel not a height; IDs preserved |
| ALT-N1 | A | — | local DEM mosaic bypasses elevation API |
| ALT-N2 | A | GDAL | `terrain-elevation-screening` selects 27 terrain cells and 2,700 m²; no point API |

### [geopf-routing](geopf-routing.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| RTE-01 | A + B | NET, GDAL or PY | resource discovery, units, snapping, actual FeatureCollection |
| RTE-02 | A + B | NET, GDAL or PY | arrival direction and explicit duration units |
| RTE-N1 | A | — | geometric buffer bypasses network routing |

### [gdal-vector-processing](gdal-vector-processing.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| GVB-01 | A + B | GDAL | `CP1252` chosen from the evidence; `œ` and `–` intact; source unchanged |
| GVB-02 | A + B | GDAL | second layer added with `-update`; first layer still present |
| GVB-03 | A + B | GDAL | box CRS stated; geometries cut; 319 m² in Lambert-93, not zero features |
| GVB-04 | A + B | GDAL | explicit encoding and `.cpg`; field mapping reported; no `?` in the text |
| GVB-N1 | A | PY | `geopandas-vector-analysis` loaded, not `gdal-vector-processing` |
| GVB-N2 | A | NET, GDAL | `geopf-wfs-download` loaded, not `gdal-vector-processing` |

### [apicarto-query](apicarto-query.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| APC-01 | A + B | NET | all pages up to `numberMatched`; `localhost` links not followed |
| APC-02 | A + B | NET | both Natura 2000 networks; longitude, latitude order |
| APC-03 | A + B | NET | zone with document and date; outage reported, no invented zone |
| APC-N1 | A | NET | download or WFS skill loaded; no paging of a whole department |

### [geospatial-descriptive-statistics](geospatial-descriptive-statistics.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| GDS-01 | A + B | PY | mean/median 10, sum 30, sample std 10, quartiles 5/15, missing 25 %; strict JSON |
| GDS-02 | A + B | PY | string IDs kept, counts 2/1/1 and frequencies 0.5/0.25/0.25 |
| GDS-N1 | A | PY | `gdal-raster-processing` or `geopandas-vector-analysis` loaded; no single-layer summary |
| GDS-N2 | A | PY | `spatial-aggregation` loaded; no single-layer summary |

### [qgis-layer-styling](qgis-layer-styling.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| QLS-01 | A + B | QGIS | red stroke, no fill, fresh-layer reload; missing PyQGIS reported, not installed |
| QLS-02 | A + B | QGIS | numeric field, breaks 0/10/20/30, one unrendered null, checked renderer |
| QLS-N1 | A | QGIS | `qgis-project-builder` loaded; no QML written, no `qgis-layer-styling` load |

### [spatial-aggregation](spatial-aggregation.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| SPA-01 | A + B | PY | `within`; counts 2/1/0 for 001/002/NA; `edge` and `outside` unmatched; string IDs |
| SPA-02 | A + B | PY | `intersects` + `all`; `edge` counted twice; counts 3/2/0, sums 40/30/0, means 13.33/30, empty mean null |
| SPA-N1 | A | PY | `geospatial-descriptive-statistics` loaded; no zone join |
| SPA-N2 | A | PY | `gdal-raster-processing` or `geopandas-vector-analysis` loaded; no vector aggregation |

### [bdtopo-schema-guide](bdtopo-schema-guide.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| BTS-01 | A + B | — | `batiment`/`hauteur` (`HAUTEUR`), metres to the eaves, 0 unknown, revision and pp. 76–77; no network |
| BTS-02 | A + B | — | `troncon_de_route`, `importance`/`IMPORTANCE`, `nombre_de_voies`/`NB_VOIES`; no claimed 3.3 equivalence |
| BTS-N1 | A | NET | `geopf-wfs-download` loaded; no schema guide |
| BTS-N2 | A | PY | `spatial-aggregation` loaded; no schema guide |

### [qgis-project-builder](qgis-project-builder.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| QPB-01 | A + B | QGIS | points above zones, extent reaching `outside` at x = 20, relative sources resolved inside the moved bundle; originals unchanged |
| QPB-02 | A + B | QGIS, NET | WMTS identifiers read from capabilities, extent on Saint-Mandé, local and remote status reported apart; no rendering claimed from a valid provider |
| QPB-N1 | A | QGIS | `qgis-layer-styling` loaded; no `qgis-project-builder` load, no `.qgz` or `.qgs` written |

### [municipality-building-profile](municipality-building-profile.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| MBP-01 | A + B | PY | four buildings selected, union 850 m² and 8.5 % without double-counting the overlap; height and usage populations verified, round trips done, sources unchanged |
| MBP-02 | A + B | PY, QGIS | same indicators as MBP-01 plus a real styled project reopened after moving the bundle; missing PyQGIS reported, not a JSON-only project |
| MBP-03 | A + B | PY | unknown inventory coverage stated; height and usage left uncomputed instead of guessed |
| MBP-N1 | A | NET, GDAL | `geopf-wfs-download` loaded; no `municipality-building-profile` load, no portrait |
| MBP-N2 | A | PY | `geospatial-descriptive-statistics` loaded; mean 382.5 and median 260 without clipping |
| MBP-N3 | A | QGIS | `qgis-project-builder` loaded; existing layers assembled, no indicators |

### [terrain-elevation-screening](terrain-elevation-screening.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| TES-01 | A + B | GDAL | inclusive interval, valid zero, 27 selected / 21 rejected / 1 unknown cells; 2,700 m² and unchanged inputs |
| TES-02 | A + B | GDAL | degree slope, 8 selected / 16 rejected / 25 unknown cells, 800 m²; terrain candidates without landing suitability claims |
| TES-03 | A + B | GDAL | empty layer retains CRS/schema; 48 valid rejected cells distinguished from missing coverage |
| TES-N1 | A | NET | `geopf-altimetry` retrieves points; no area workflow |
| TES-N2 | A | GDAL | `gdal-raster-processing` clips only; no threshold or site analysis |

### [map-illustration](map-illustration.md)

| Scenario | Modes | Needs | Watch in B |
| --- | --- | --- | --- |
| MAP-01 | A + B | PY | actual PNG/SVG, 1400 × 1000 pixels, source/units, three features and measured bytes |
| MAP-02 | A + B | QGIS | actual rendered red unfilled boundary; image rather than QML/QGZ |
| MAP-03 | A + B | PY, browser | only selected attributes; interactions checked; Leaflet assets not mistaken for offline support |
| MAP-04 | A + B | PY, GDAL | bounded raster display, valid zero versus nodata, no new terrain analysis |
| MAP-N1 | A | QGIS | qgis-layer-styling creates QML only |
| MAP-N2 | A | QGIS | qgis-project-builder assembles a portable project only |
| MAP-N3 | A | MS | mapshaper-simplify changes display geometry, no illustration |

## Score a run

For each row of `report.md`, in the run directory:

1. **Skill selection.** In A, `Skills loaded` contains the expected skill of the scenario;
   for a `-N` scenario, it does not contain the excluded one. For a model sweep,
   `ab_sensitivity` applies this rule to every run. In B, it contains none of
   the skills of this repository: a run flagged `INVALID` is excluded; a historical run
   flagged `CHECK` needs manual review before scoring.
2. **Result.** Compare `output/` and `answer.md` with the expected result of the scenario
   file. Write `pass` or `fail`.
3. **Checklist.** Count the checklist items met, for example `4/5`. Every scenario has
   at least one item; `test_scenarios.py` enforces it. `commands.txt` shows the commands
   actually run.
4. **Conduct.** A non-zero `Installs`, a download piped through `head` or `tail`, or an
   invented layer or field name fails the run, whatever the result.

An agent can pre-fill the scores ("score `$AB/runs/GEO-02/with-1` against GEO-02 in
`tests/geopf-geocoding.md`"). Check its scores by hand before drawing conclusions.

## Interpret

| A (with) | B (without) | Reading |
|----------|-------------|---------|
| pass | fail | The skill earns its place on this scenario. |
| pass | pass | No measurable gain. Compare turns and cost; if every scenario of a skill reads this way, trim or drop the skill, or write a scenario that tests what it adds. |
| fail | fail | The skill does not solve the task: fix the skill, or the scenario. |
| fail | pass | The skill misleads the agent: fix it first. |
| expected skill not loaded | — | Triggering problem: fix the `description`, not the body. |

Summarize per skill over the three repetitions:

| Skill | A pass | B pass | A − B | Cost A / B | Verdict |
|-------|--------|--------|-------|------------|---------|
| geopf-service-selection | /15 | /15 | | | |
| geopf-geocoding | /18 | /18 | | | |
| crs-reprojection-france | /15 | /15 | | | |
| gdal-raster-processing | /18 | /18 | | | |
| geopf-raster-download | /15 | /15 | | | |
| geopf-wfs-download | /21 | /21 | | | |
| geoserver-cql-filter | /12 | /12 | | | |
| geopandas-vector-analysis | /12 | /12 | | | |
| vector-data-quality | /9 | /9 | | | |
| mapshaper-simplify | /12 | /12 | | | |
| geodata-intake | /6 | /6 | | | |
| geopf-file-download | /6 | /6 | | | |
| geopf-altimetry | /6 | /6 | | | |
| geopf-routing | /6 | /6 | | | |
| gdal-vector-processing | /12 | /12 | | | |
| apicarto-query | /9 | /9 | | | |
| geospatial-descriptive-statistics | /6 | /6 | | | |
| qgis-layer-styling | /6 | /6 | | | |
| spatial-aggregation | /6 | /6 | | | |
| bdtopo-schema-guide | /6 | /6 | | | |
| qgis-project-builder | /6 | /6 | | | |
| municipality-building-profile | /9 | /9 | | | |
| terrain-elevation-screening | /9 | /9 | | | |
| map-illustration | /12 | /12 | | | |
| Negative scenarios (A only) | /114 | — | — | — | |

## Model sensitivity

A skill is model-sensitive when its effect depends on the model that reads it: a large
model selects it and follows it, a smaller one misses it, loads a neighbour or skips a
step. Skills installed with the Skills CLI are read by many agents and models, so a skill
should not rely on what only the strongest model can infer. Two layers check this.

- **Every push, no model call.** [test_skill_robustness.py](test_skill_robustness.py)
  checks the wording that keeps selection from resting on inference: each description says
  when to use the skill and names other skills exactly (`geopf-wfs-download`, not "the WFS
  skill"), and each boundary tested by a negative scenario is written in the skill to
  exclude, so that a model that loads it by mistake reads where to go instead.
- **On demand, paid.** A sweep runs scenarios in A only, once per model of `AB_MODELS`,
  then compares the models skill by skill. B runs are left out: without skills they
  measure each model's prior knowledge, which is a separate question.

Prepare the directories first, then run the panel in a new sweep directory:

```bash
source ab.sh
export AB_MODELS="haiku sonnet opus"            # aliases, or pinned model IDs
AB_DRY=1 ab_sweep 1 $(ab_panel)
export AB=/path/to/a/new/sweep
ab_env
ab_sweep 1 $(ab_panel)
for model in $AB_MODELS; do AB="$AB/models/$model" ab_report; done
ab_sensitivity
```

`ab_panel` lists **48 scenarios**, the first positive and the first negative of each skill:
**144 runs** per repetition with the 3 models of `AB_MODELS`, capped at $288. A full sweep
runs all 122 scenarios: 366 runs, capped at $732 per repetition. Starting a paid sweep is a
separate user decision; a dry run does not authorize it.

`$AB/sensitivity.md` has four tables:

- **Skill selection**, scored automatically for every run: correct runs out of scored runs
  per skill and model, with the spread between the best and the worst model.
- **Task result**, read from the `Result` column of each `models/<model>/report.md` once
  it is scored as in [Score a run](#score-a-run); rerun `ab_sensitivity` after scoring.
- **Cost and invalid runs** per model.
- **Runs**: each scenario and repetition, with the skills each model loaded.

A skill is flagged `SENSITIVE` when the spread reaches `AB_SPREAD` (default `1/3`).

| Selection | Result | Reading | Next step |
|-----------|--------|---------|-----------|
| Same for all models | Same for all models | Not model-sensitive on these scenarios | — |
| Lower for some models | — | The description relies on inference | Put the words of the request, exact skill names and a `not …` clause in the description; sweep again |
| Same for all models | Lower for some models | The body is too implicit for some models | Bring the main command forward, make each validation step explicit, move detail to `references/`; sweep again |
| Low for every model | — | A description problem, not model sensitivity | Rewrite the description, then run the A/B campaign |

Limits:

- One repetition gives one or two panel runs per skill and model: a flag is a lead, not a
  verdict. Before changing a skill, run all its scenarios three times with the models
  that diverge.
- Aliases such as `haiku` move to newer versions. `sensitivity.md` records the resolved
  model IDs; pin full IDs to compare sweeps over time.
- The sweep reaches the models that the `claude` CLI serves. Another agent or model family
  needs its own harness. `ab_sensitivity` only reads
  `models/<model>/runs/<id>/with-<rep>/summary.json` (`scenario`, `rep`, `skills`,
  `comparable`), so a harness that writes these files can reuse it.
- A live service outage fails every model alike. `ab_sweep` runs all models of a scenario
  back to back so that they meet the same service state.

## Variants

Use a new `AB` directory for each variant, so that reports do not mix.

- **No skill at all in B:** `AB_WITHOUT_FLAGS="--disable-slash-commands"` also removes
  user-level and plugin skills from the B runs.
- **Prior knowledge only:** `AB_TOOLS="Bash Read Write Edit Glob Grep"` removes web search
  and fetch in both modes; services stay reachable through `curl`.

## Experimental prompts

The runner also takes the prompts of the [experimental catalog](prompts/catalog.md), which
are not part of the campaign. `ab_run XP-05 with x1` runs one in the same isolated
directory, with the skills, fixtures, budget and `summary.json` of a scenario run. Copy the
skills loaded and the outcome to [prompts/runs.md](prompts/runs.md). Scenario files are
read first, so an `XP` identifier never replaces a scenario prompt.

## Limits

- User-level skills, plugins and `~/.claude/CLAUDE.md` load in both modes. A user-level
  geospatial skill can solve a scenario in B. Use a disposable profile without overlapping
  geospatial skills for a paired comparison; the no-skill variant is a separate experiment.
  The transcript check detects explicit reads and invocations, not every form of inherited
  context. Absence of a warning does not prove that B was uncontaminated.
- VDQ-01, VDQ-02 and GPD-04 have no fixture: the agent builds its own data, so compare
  the procedure, not the values.
- VDQ-03 uses `data/coverage_synthetic.geojson`, whose defects are known. With
  GeoPandas < 1.1 and GDAL < 3.12, only the overlap-pair and enclosed-gap recipes remain,
  in both modes.
- Live results (scores, labels, layer lists) drift: compare A and B of the same repetition.
- GDAL < 3.12 removes the `gdal raster zonal-stats` path of RAS-05 in both modes.
- GVB-01 to GVB-04 use `data/communes_sans_cpg/`, `data/communes_points.geojson` and
  `data/coverage_synthetic.geojson`, whose expected values are fixed. With GDAL 3.13.0 to
  3.13.3, `ogr2ogr -where` combined with `-select` on a GeoPackage keeps every field; check
  the fields of GVB outputs rather than the command alone.
- APC scenarios query live API Carto data: parcel counts, plan versions and the GPU
  module's availability change. Score A and B of the same repetition against the
  responses saved in each run.
- Automated runner tests use a fake CLI and make no paid calls. They verify preparation,
  bookkeeping and error handling, not live agent behavior or skill selection. Record the
  installed CLI version and check its flags against the
  [official programmatic usage guide](https://code.claude.com/docs/en/headless).
