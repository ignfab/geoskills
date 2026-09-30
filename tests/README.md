# Skill tests

This directory contains automated regression tests and manual agent scenarios. Automated
tests check commands, data and helpers; manual scenarios check skill selection and agent
decisions. Passing command tests does not prove that an agent will select the right skill.

The prompts are in French on purpose: French trigger words are part of what is being
tested (see the `description` of each skill).

## Contents

| File | Skill |
|------|-------|
| [geopf-geocoding.md](geopf-geocoding.md) | `geopf-geocoding` |
| [crs-reprojection-france.md](crs-reprojection-france.md) | `crs-reprojection-france` |
| [gdal-raster-basics.md](gdal-raster-basics.md) | `gdal-raster-basics` |
| [geopf-wms-wmts.md](geopf-wms-wmts.md) | `geopf-wms-wmts` |
| [geopf-wfs-download.md](geopf-wfs-download.md) | `geopf-wfs-download` |
| [geopandas-basics.md](geopandas-basics.md) | `geopandas-basics` |
| [data/README.md](data/README.md) | Fixture provenance, CRS and missing-metadata traps |

Test data in `data/`:

| File | Content |
|------|---------|
| `adresses.csv` | 8 addresses split across columns: valid, without postcode, overseas, unknown, empty |
| `points.csv` | 3 points (lon, lat) to reverse-geocode |
| `points_gps.csv` | 3 GPS points, **latitude before longitude**, one of them in Réunion |
| `points_lambert2e.csv` | 2 points in NTF Lambert II étendu (EPSG:27572) |
| `monuments_sans_prj/` | Shapefile of 3 Paris monuments in Lambert-93, **without a `.prj`** |
| `saint_mande.geojson` | Boundary of Saint-Mandé (INSEE 94067), EPSG:4326, from ADMIN EXPRESS |
| `mnt_dalles/` | 10 m DEM of Saint-Mandé (RGE ALTI) split into 2 ESRI ASCII tiles, **without a `.prj`** |

`saint_mande.geojson` and `mnt_dalles/` are extracts of IGN data (ADMIN EXPRESS, RGE ALTI),
distributed under the [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).

The original manual references were supplied for GDAL 3.13. The stored fixture values
were also checked with GDAL 3.10.3 / PROJ 9.6.2 on 2026-09-30. Local fixture checks use
explicit tolerances; live scores, labels and layer availability are observations that may
change. Do not require a service to reproduce a historical bug to pass a test.

## Automated checks

From the repository root, with Python ≥ 3.9:

```bash
python3 -m pip install -r tests/requirements.txt
python3 .github/validate-skills.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

- `test_validation.py`: real YAML parsing, empty/invalid metadata, duplicate keys, missing
  files and reference reachability.
- `test_split_csv.py`: record and byte limits, BOM, multiline/quoted fields, leading zeros,
  malformed input and preservation of existing files.
- `test_workflows.py`: local GDAL/PROJ recipes (axis order, overseas CRS, missing `.prj`,
  area, mosaic, clip, COG marker, weighted averaging, hillshade and vertical transforms).
- `test_geopandas.py`: spatial join, CRS and format round trips, and zonal-statistics
  attachment after filtering an index.
- `test_live.py`: bounded geocoding, WFS, WMS and WMTS smoke tests; skipped by default.

GDAL ≥ 3.1 and PROJ CLI tools are required for local geospatial checks. Install the optional
Python workflows with `python3 -m pip install -r tests/requirements-geospatial.txt`.
Missing tools/packages produce explicit skips; a tool that is installed but cannot start
is an error. CI sets `GEOSKILLS_REQUIRE_GDAL=1` so missing CLI tools fail the job.
Tests use temporary directories, disable PROJ networking and do not modify source fixtures.
If `gdalinfo --version` fails (for example, an undefined `sqlite3_total_changes64` symbol),
repair the active GDAL/SQLite environment or use a clean environment before rerunning.
The tests deliberately do not hide a broken installation.

The NTF and vertical tests skip if the required IGN grids are unavailable locally; install
those grids separately to enable them. The `LAYOUT=COG` check is not a full COG validator.

To run the live tests deliberately:

```bash
GEOSKILLS_LIVE=1 python3 -m unittest discover -s tests -p 'test_live.py' -v
```

This sends the eight fixture addresses in `data/adresses.csv` to the public IGN geocoder,
queries the three public test coordinates and a cadastral parcel, and downloads small
WFS/raster extracts. Do not replace those fixtures with private data for a live run.
Network/service failures are reported as failures, not silently treated as passed tests.
Live calls are bounded by timeouts and small extents and do not run in routine CI.

To check CLI discovery without installing skills (Node.js required):

```bash
npx skills add . --list
```

## Manual agent setup

Requirements depend on the scenario: GDAL/PROJ, `curl`, and optionally GeoPandas,
`rasterstats` and `pyarrow`. The newer `gdal raster zonal-stats` command specifically
requires GDAL ≥ 3.12; older GDAL can test a masked single-zone crop or rasterstats.

Install the skills in this directory, from the local clone:

```bash
cd tests
npx skills add .. -a claude-code -y
```

Or from a branch pushed to GitHub:

```bash
npx skills add "ignfab/geoskills#<branch>" -a claude-code -y
```

The CLI installs the skills for the selected agent and may use shared directories or
symlinks. Inspect its reported paths; after editing, refresh the installation if it is a
copy. Generated agent directories are ignored by git (see [.gitignore](.gitignore)).

## Running a scenario

1. Start a **new** agent session from `tests/` (`cd tests && claude`), because skills are
   loaded when a session starts.
2. Create `output/`, keep the fixtures unchanged, then send the scenario prompt as is.
   To avoid statistics sidecars on source rasters, use `GDAL_PAM_ENABLED=NO` for read-only
   inspection or inspect temporary copies.
3. Check that the expected skill was loaded, then compare the result with the expected
   values and go through the checklist.
4. The prompts ask the agent to write its files to `output/`, which is ignored by git.
   Use a fresh output directory for each run to avoid stale-file false positives.

A scenario passes when the right skill is loaded, the result matches, and none of the
pitfalls listed in its checklist is hit. The `-N` scenarios are negative: the skill should
**not** be loaded, or should hand over to another skill.

## Automated agent runs

[run_evals.py](run_evals.py) runs the same scenarios headlessly through the Claude CLI. It
needs only Python 3 and `claude`; GDAL must be on the `PATH` for the GDAL and CRS
scenarios.

```bash
python3 run_evals.py --list                 # parsed scenarios, free
python3 run_evals.py GEO-01                 # one scenario
python3 run_evals.py 'CRS-*' --no-grade     # only check which skills load
python3 run_evals.py                        # every scenario
```

For each scenario, the runner:

1. creates a temporary workspace **outside the repository**, with a copy of the skills in
   `.claude/skills/`, a copy of `data/` and an empty `output/`, so that the repository's
   `CLAUDE.md` does not influence the agent and every run starts clean;
2. sends the prompt with `claude -p`, allowing only file tools, `curl`, `python3` and the
   GDAL/PROJ commands (see `AGENT_TOOLS` in the script);
3. checks the **trigger** from the transcript: the skill named on the `Expected skill` line
   must be loaded (unless marked `optional`), and a skill written as ``not `name` `` must not;
4. unless `--no-grade`, asks a **separate** Claude session to grade each checklist item and
   the expected result from the transcript and the files in `output/`.

Results go to `eval-results/<timestamp>/` (ignored by git): `summary.json`, and for each
scenario `events.ndjson`, `answer.md` and `grading.json`. The exit code is non-zero when a
scenario fails.

Each run costs API credit: `--budget-usd` (default 2) caps an agent run and
`--grader-budget-usd` (default 0.5) a grading. GEO-01 cost about USD 0.15. Scenarios run
in isolated workspaces, so a scenario cannot rely on a file written by another one.

## Cleanup

Automated tests clean their temporary directories automatically. For manual runs, remove
only artifacts and skill installations created for that run, from the `tests/` directory;
avoid a broad `skills remove --all` when unrelated skills are installed.
