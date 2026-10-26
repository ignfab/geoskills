# A/B testing the skills

This protocol measures what each skill adds. Every positive scenario in `tests/<skill>.md`
is run twice under the same conditions: **A** with the skills of this repository installed,
**B** without them. A higher pass rate in A is evidence of added value on those scenarios;
when both pass, compare effort and cost as well as output quality.

The scenario files remain the reference for prompts, expected results and checklists.
This file adds the procedure, a runner and a scoring grid.

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
  `gdal raster zonal-stats` path of RAS-05;
- PROJ with the IGN grids `fr_ign_ntf_r93.tif` (CRS-02) and `fr_ign_RAF18.tif` (CRS-04),
  for example with `projsync --source-id fr_ign`;
- `python3 -m pip install -r tests/requirements-geospatial.txt` for the GPD and VDQ
  scenarios;
- Mapshaper 0.7.83 and compatible Node.js for the MS scenarios; see
  [Mapshaper requirements](../skills/mapshaper-simplify/README.md#requirements);
- network access to `data.geopf.fr` for the GEO, WFS and WMS scenarios.

A missing tool fails both modes and hides the effect of the skill. `ab_env` records the
versions at the top of the report so that such runs can be excluded.

## Runner

Save the block below as `ab.sh`, outside the repository, check the variables at the top,
then load it with `source ab.sh`.

```bash
export GEOSKILLS="${GEOSKILLS:-$HOME/projects/geoskills}"  # the repository clone
export AB="${AB:-$HOME/geoskills-ab/$(date +%F)}"          # outside the repository
export AB_MODEL="${AB_MODEL:-opus}"              # same model/version in both modes
export AB_BUDGET="2"                            # USD cap per run
export AB_TOOLS="Bash Read Write Edit Glob Grep WebFetch WebSearch"
export AB_DENY="Bash(sudo *) Bash(pip install *) Bash(pip3 install *) Bash(python3 -m pip install *) Bash(conda install *) Bash(mamba install *) Bash(apt *) Bash(apt-get *) Bash(brew install *) Bash(npm install *)"
export AB_EXTRA_FLAGS=""                        # extra claude flags, both modes
export AB_WITHOUT_FLAGS=""                      # extra claude flags, B runs only

POSITIVE="GEO-01 GEO-02 GEO-03 GEO-04 GEO-05 CRS-01 CRS-02 CRS-03 CRS-04 CRS-05
RAS-01 RAS-02 RAS-03 RAS-04 RAS-05 WMS-01 WMS-02 WMS-03 WMS-04 WMS-05
WFS-01 WFS-02 WFS-04 WFS-05 WFS-06 CQL-01 CQL-02 CQL-03 CQL-04 GPD-01 GPD-02 GPD-03 GPD-04 VDQ-01 VDQ-02 MS-01 MS-02 MS-03 MS-04"
NEGATIVE="GEO-N1 CRS-N1 RAS-N1 WMS-N1 WFS-N1 CQL-N1 CQL-N2 GPD-N1 VDQ-N1 MS-N1 MS-N2"

# Print the French prompt of a scenario, read from tests/*.md.
ab_prompt() {
  python3 - "$1" "$GEOSKILLS"/tests/*.md <<'PY'
import re, sys
want, paths = sys.argv[1], sys.argv[2:]
for path in paths:
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
  local id=$1 mode=$2 rep=${3:-1} after=${4:-} prompt flags=$AB_EXTRA_FLAGS status=0
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
    cp -r "$GEOSKILLS"/skills/* "$dir/.claude/skills/" || return 1
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
ours = {p.name for p in pathlib.Path(os.environ["GEOSKILLS"], "skills").iterdir()}
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
summary = {
    "scenario": d.parent.name, "mode": mode, "rep": rep, "model": model,
    "skills": skills, "skill_file_reads": len(skill_files),
    "install_attempts": len(installs),
    "turns": result.get("num_turns"), "cost_usd": result.get("total_cost_usd"),
    "duration_s": round(result.get("duration_ms", 0) / 1000),
    "exit_code": exit_code,
    "ok": exit_code == 0 and bool(result) and not result.get("is_error"),
}
(d / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(d / "answer.md").write_text(str(result.get("result", "")) + "\n", encoding="utf-8")
(d / "commands.txt").write_text("\n\n".join(cmds) + "\n", encoding="utf-8")
leak = mode == "without" and (skill_files or set(skills) & ours)
flag = "  <-- CHECK: skill used in a run without skills" if leak else ""
print(f"{summary['scenario']} {mode}-{rep}: model={model} skills={','.join(skills) or '-'} "
      f"turns={summary['turns']} cost={summary['cost_usd']} "
      f"time={summary['duration_s']}s installs={len(installs)}{flag}")
sys.exit(0 if summary["ok"] else 1)
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
    out.append(f"| {s['scenario']} | {s['mode']} | {s['rep']} | {', '.join(s['skills']) or '-'} "
               f"| {s['turns']} | {s['cost_usd']} | {s['duration_s']} | {s['install_attempts']} "
               f"| {'' if s['ok'] else 'ERROR'} | | |")
for mode in ("with", "without"):
    cost = sum(s["cost_usd"] or 0 for s in rows if s["mode"] == mode)
    out.append(f"\nTotal cost {mode}: {cost:.2f} $")
(root / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(root / "report.md")
PY
}
```

| Function | Role |
|----------|------|
| `ab_env` | Records the date, model, tool versions and IGN grids in `$AB/environment.txt`. |
| `ab_prompt <id>` | Prints the prompt of a scenario, read from `tests/*.md`. |
| `ab_run <id> <with\|without> [rep] [after]` | Creates `$AB/runs/<id>/<mode>-<rep>/`, copies `data/` (and the skills in A), copies the output of the `after` run, runs `claude -p` and keeps `transcript.jsonl`. |
| `ab_campaign [rep]` | One repetition of every scenario. |
| `ab_summary <dir>` | Writes `summary.json`, `commands.txt` (Bash commands run) and `answer.md` (final answer). Flags a B run that used a skill of this repository. |
| `ab_report` | Writes `$AB/report.md`: the environment and one row per run, with blank columns to score. |

`claude -p` cannot ask for permission, so the allowed tools are listed in `AB_TOOLS`. The
agent can run shell commands and reach the web. The deny list and install counter cover
common spellings, not every possible installer invocation; they are not a sandbox.
Run the campaign in a disposable environment and cap the cost with `AB_BUDGET`.
`AB_DRY=1` prepares a run directory without starting the agent.
Preparation or agent failures stop the campaign; inspect the failing run before using a
new repetition or campaign directory. Missing prerequisites must not count as skill failures.

## Run the campaign

Prepare all directories without calling an agent first:

```bash
source ab.sh
AB_DRY=1 ab_campaign 1
```

Then set `export AB=/path/to/a/new/campaign` for actual agent calls. One repetition has **91 runs**:
40 positive scenarios in both modes and 11 negatives in A. At the example budget of $2 per
run, the caps total $182 per repetition and $546 for three repetitions. Starting the paid
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
GeoPandas stack. *Watch in B* is the trap the skill is meant to prevent: if the skill is
useful, B fails there. *Control* scenarios are expected to pass in both modes; a skill
whose scenarios are all controls adds nothing measurable.

### [geopf-geocoding](geopf-geocoding.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| GEO-01 | A + B | NET | `data.geopf.fr/geocodage` rather than another geocoder or an API key |
| GEO-02 | A + B | NET | one `POST /search/csv`; `postcode=` given a column name; encoding trap on row 1; rows 6–8 flagged |
| GEO-03 | A + B | NET | lon/lat order (point 3 is in Réunion) |
| GEO-04 | A + B | NET | `index=parcel` and `truegeometry` promoted: a `Point` output fails |
| GEO-05 | A + B | — | control |
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

### [gdal-raster-basics](gdal-raster-basics.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| RAS-01 | A + B | GDAL | control: missing CRS reported |
| RAS-02 | A + B | GDAL | EPSG:2154 assigned to the tiles; cutline reprojected on the fly; COG; no sidecar on the sources |
| RAS-03 | A + B | GDAL | `-tap -r average`, not the default `near` |
| RAS-04 | A + B | GDAL | control |
| RAS-05 | A + B | GDAL ≥ 3.12 or PY | zones reprojected to EPSG:2154, not the DEM; `count = 0` caught |
| RAS-N1 | A | NET | `geopf-wms-wmts` loaded |

### [geopf-wms-wmts](geopf-wms-wmts.md)

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
| WFS-N1 | A | NET | `geopf-wms-wmts` loaded |

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

### [geopandas-basics](geopandas-basics.md)

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
| VDQ-N1 | A | PY | `geopandas-basics` loaded, not `vector-data-quality` |

### [mapshaper-simplify](mapshaper-simplify.md)

| Scenario | Modes | Needs | Watch in B |
|----------|-------|-------|------------|
| MS-01 | A + B | Mapshaper, PY | shared borders, string identifiers and small-feature retention |
| MS-02 | A + B | Mapshaper, PY | 100 m tolerance in a suitable projected CRS, then WGS84 export |
| MS-03 | A + B | — | `keep-shapes` does not preserve every multipart island or hole |
| MS-04 | A + B | Mapshaper, PY | independent variants from the source; measured size and geometry changes |
| MS-N1 | A | PY | geometry repair without simplification; `vector-data-quality` selected |
| MS-N2 | A | GDAL | raster resampling handled by `gdal-raster-basics` |

## Score a run

For each row of `report.md`, in the run directory:

1. **Skill selection.** In A, `Skills loaded` contains the expected skill of the scenario;
   for a `-N` scenario, it does not contain the excluded one. In B, it contains none of
   the skills of this repository: a run flagged `CHECK` is contaminated and discarded.
2. **Result.** Compare `output/` and `answer.md` with the expected result of the scenario
   file. Write `pass` or `fail`.
3. **Checklist.** Count the checklist items met, for example `4/5`. `commands.txt` shows
   the commands actually run.
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
| geopf-geocoding | /15 | /15 | | | |
| crs-reprojection-france | /15 | /15 | | | |
| gdal-raster-basics | /15 | /15 | | | |
| geopf-wms-wmts | /15 | /15 | | | |
| geopf-wfs-download | /18 | /18 | | | |
| geoserver-cql-filter | /12 | /12 | | | |
| geopandas-basics | /12 | /12 | | | |
| vector-data-quality | /6 | /6 | | | |
| mapshaper-simplify | /12 | /12 | | | |
| Negative scenarios (A only) | /33 | — | — | — | |

## Variants

Use a new `AB` directory for each variant, so that reports do not mix.

- **No skill at all in B:** `AB_WITHOUT_FLAGS="--disable-slash-commands"` also removes
  user-level and plugin skills from the B runs.
- **Prior knowledge only:** `AB_TOOLS="Bash Read Write Edit Glob Grep"` removes web search
  and fetch in both modes; services stay reachable through `curl`.

## Limits

- User-level skills, plugins and `~/.claude/CLAUDE.md` load in both modes. A user-level
  geospatial skill can solve a scenario in B. Use a disposable profile without overlapping
  geospatial skills for a paired comparison; the no-skill variant is a separate experiment.
  The transcript check detects explicit reads and invocations, not every form of inherited
  context. Absence of a warning does not prove that B was uncontaminated.
- VDQ-01 and VDQ-02 have no fixture: the agent builds its own data, so compare the
  procedure, not the values.
- Live results (scores, labels, layer lists) drift: compare A and B of the same repetition.
- GDAL < 3.12 removes the `gdal raster zonal-stats` path of RAS-05 in both modes.
- Automated runner tests use a fake CLI and make no paid calls. They verify preparation,
  bookkeeping and error handling, not live agent behavior or skill selection. Record the
  installed CLI version and check its flags against the
  [official programmatic usage guide](https://code.claude.com/docs/en/headless).
