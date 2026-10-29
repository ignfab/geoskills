# Skill tests

This directory contains automated regression tests and manual agent scenarios. Automated
tests check commands, data and helpers; manual scenarios check skill selection and agent
decisions. Passing command tests does not prove that an agent will select the right skill.

The prompts are in French on purpose: they check that a French request triggers a skill
whose `description` is written in English.

## Contents

| File | Skill |
|------|-------|
| [geopf-services.md](geopf-services.md) | `geopf-services` |
| [geopf-geocoding.md](geopf-geocoding.md) | `geopf-geocoding` |
| [crs-reprojection-france.md](crs-reprojection-france.md) | `crs-reprojection-france` |
| [gdal-raster-basics.md](gdal-raster-basics.md) | `gdal-raster-basics` |
| [geopf-wms-wmts.md](geopf-wms-wmts.md) | `geopf-wms-wmts` |
| [geopf-wfs-download.md](geopf-wfs-download.md) | `geopf-wfs-download` |
| [geoserver-cql-filter.md](geoserver-cql-filter.md) | `geoserver-cql-filter` |
| [geopandas-basics.md](geopandas-basics.md) | `geopandas-basics` |
| [vector-data-quality.md](vector-data-quality.md) | `vector-data-quality` |
| [mapshaper-simplify.md](mapshaper-simplify.md) | `mapshaper-simplify` |
| [geodata-intake.md](geodata-intake.md) | `geodata-intake` |
| [geopf-download-files.md](geopf-download-files.md) | `geopf-download-files` |
| [geopf-altimetry.md](geopf-altimetry.md) | `geopf-altimetry` |
| [geopf-routing.md](geopf-routing.md) | `geopf-routing` |
| [data/README.md](data/README.md) | Fixture provenance, CRS and missing-metadata traps |
| [ab-testing.md](ab-testing.md) | Running every scenario with and without the skills, and scoring the difference |
| [review-2026-10-12.md](review-2026-10-12.md) | Recent-skill review, reproduced defects, fixes and validation limits |
| [review-2026-10-27.md](review-2026-10-27.md) | Test audit, added edge cases and remaining coverage limits |
| [review-2026-10-28.md](review-2026-10-28.md) | Four added skills, workflow checks, live evidence and an actual agent pilot |

The dated reviews preserve the checks and limitations observed at the time. Use the
current test inventory and commands below for a new run; a historical pass is not a
current live-service guarantee. The latest review's agent pilot is not a full A/B evaluation.

Test data in `data/`:

| File | Content |
|------|---------|
| `adresses.csv` | 8 addresses split across columns: valid, without postcode, overseas, unknown, empty |
| `points.csv` | 3 points (lon, lat) to reverse-geocode |
| `points_gps.csv` | 3 GPS points, **latitude before longitude**, one of them in Réunion |
| `points_lambert2e.csv` | 2 points in NTF extended Lambert II (EPSG:27572) |
| `monuments_sans_prj/` | Shapefile of 3 Paris monuments in Lambert-93, **without a `.prj`** |
| `saint_mande.geojson` | Boundary of Saint-Mandé (INSEE 94067), EPSG:4326, from ADMIN EXPRESS |
| `admin_units_synthetic.geojson` | Three invented EPSG:4326 polygons: two neighbors with a detailed shared border and a small island feature |
| `coverage_synthetic.geojson` | Nine invented EPSG:2154 parcels, each valid, with an overlap, an enclosed gap, a narrow gap and a sliver |
| `mnt_dalles/` | 10 m DEM of Saint-Mandé (RGE ALTI) split into 2 ESRI ASCII tiles, **without a `.prj`** |
| `classes_synthetic.asc` | Invented 2 × 2 categorical grid, EPSG:2154, valid classes 0/1/5 and nodata 255 |
| `geocoded_synthetic.csv` | Seven invented geocoding results for acceptance, review and unmatched-row checks |
| `elevation_points.csv` | Two invented input points with string identifiers |
| `elevations_synthetic.json` | Corresponding synthetic elevations, including a missing-value sentinel and unknown vertical datum |

`saint_mande.geojson` and `mnt_dalles/` are extracts of IGN data (ADMIN EXPRESS, RGE ALTI),
distributed under the [Licence Ouverte 2.0](https://www.data.gouv.fr/pages/legal/licences/etalab-2-0).

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

- `test_enrichment.py`: WFS count/ID checks, geocoding policies, Atom pagination and
  documented elevation/navigation response handling.
- `test_download_transfers.py`: actual curl downloads and safe/changed-edition range resume
  against a loopback archive server.
- `test_raster_quality.py`: read-only intake, categorical values/nodata/grid, and full COG
  validation (GDAL >= 3.13).
- `test_validation.py`: real YAML parsing, empty/invalid metadata, duplicate keys, missing
  files, required workflow sections and reference reachability.
- `test_ab_runner.py`: complete dry-run scenario coverage, isolated fixture copies and
  prerequisite outputs, rerun protection, failure propagation and exclusion of detected
  contamination/install attempts; agent calls are replaced by a test double.
- `test_cql_requests.py`: documented curl commands against a local HTTP recorder; checks
  parameter encoding, EWKT preservation, WFS sampling and WMS layer ordering. Requires
  `curl` and `bash`; does not validate ECQL parsing or a live GeoServer datastore.
- `test_split_csv.py`: record and byte limits, BOM, multiline/quoted fields, leading zeros,
  malformed input and preservation of existing files.
- `test_workflows.py`: local GDAL/PROJ recipes (axis order, overseas CRS, missing `.prj`,
  area, mosaic, clip, COG marker, weighted averaging, hillshade, zonal statistics on
  GDAL ≥ 3.12, explicit nodata conversion preserving valid zeroes and vertical transforms).
- `test_geopandas.py`: join boundaries, unmatched points and multiple matches, metric
  nearest joins/buffers, overlay areas, CRS and format round trips with nullable fields
  and string identifiers, and zonal-statistics attachment with filtered or repeated indices.
  Checks zero versus nodata/outside, mismatched result counts and attribute collisions.
- `test_vector_quality.py`: invalid-geometry diagnosis and repair, reason grouping, CRS
  area-of-use check, `linework` and `structure` repair methods, normalized geometry
  duplicates, joint attribute/geometry comparisons, null/empty handling, collapsed
  components, polygon quarantine, suspicious valid geometries, severity report, coverage
  overlaps and gaps, and GeoPackage round trip. The `gdal vector check-geometry`,
  `check-coverage` and `make-valid` recipes run on GDAL ≥ 3.12 and skip otherwise.
- `test_mapshaper.py`: percentage and metric simplification, small-feature retention,
  shared borders across layers, TopoJSON arcs, CRS and attribute preservation.
- `test_live.py`: bounded geocoding, WFS, WMS and WMTS smoke tests plus WFS, navigation
  and download-catalogue discovery; skipped by default.
- `test_live_enrichment.py`: advertised Atom pages, point elevations and profiles, route
  and isochrone geometry, WFS pagination/completeness and real GeoServer ECQL checks;
  skipped by default.

GDAL ≥ 3.1 and PROJ CLI tools are required for local geospatial checks. Install the optional
Python workflows with `python3 -m pip install -r tests/requirements-geospatial.txt`.
Missing tools/packages produce explicit skips; a tool that is installed but cannot start
is an error. CI sets `GEOSKILLS_REQUIRE_GDAL=1` so missing CLI tools fail the job.
Tests use temporary directories, disable PROJ networking and do not modify source fixtures.
Mapshaper tests also need the Mapshaper CLI and the optional Python dependencies. With
compatible Node.js installed, users can run `npm install --global mapshaper@0.7.83`.
CI uses Node.js 22 and that pinned Mapshaper version, and sets
`GEOSKILLS_REQUIRE_MAPSHAPER=1` so missing Mapshaper dependencies fail instead of skipping.
The spatial-operation, geometry audit/repair, duplicate-feature and statistics-attachment
regressions execute Python examples from their skill references via `skill_examples.py`.
The nodata, two Mapshaper entry recipes and live service-discovery tests execute the
documented Bash blocks. Changing those examples changes the code under test; other tests
exercise representative workflows, not every documented command.
If `gdalinfo --version` fails (for example, an undefined `sqlite3_total_changes64` symbol),
repair the active GDAL/SQLite environment or use a clean environment before rerunning.
The tests deliberately do not hide a broken installation.

The NTF and vertical tests skip if the required IGN grids are unavailable locally; install
those grids separately to enable them. The `LAYOUT=COG` check is not a full COG validator;
the structural COG regression requires GDAL >= 3.13 with matching Python bindings and is
skipped on older installations.

To run the live tests deliberately:

Use a working GDAL/PROJ environment, `curl`, `bash` and the optional Python dependencies
listed above. In particular, the navigation and paginated WFS checks need GeoPandas.

```bash
GEOSKILLS_LIVE=1 python3 -m unittest discover -s tests -p 'test_live*.py' -v
```

This sends the eight fixture addresses in `data/adresses.csv` to the public IGN geocoder,
queries the three public test coordinates and a cadastral parcel, and downloads small
WFS/raster extracts and service catalogues. The enrichment probes also query two public
elevation points, a 20-sample profile, a short pedestrian route, a five-minute isochrone,
and three communes with one feature per WFS page. Real ECQL tests check attribute/BBOX
predicates and malformed syntax on the IGN service; they do not establish universal EWKT
compatibility. Do not replace those fixtures with private data for a live run.
Network/service failures are reported as failures, not silently treated as passed tests.
Live calls are bounded by timeouts and small extents and do not run in routine CI.
They can also be enabled deliberately in GitHub Actions: **Validate skills → Run workflow →
Also run bounded requests to public IGN services**. The default remains off; pushes and
pull requests never enable network tests through this option.

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

## Cleanup

Automated tests clean their temporary directories automatically. For manual runs, remove
only artifacts and skill installations created for that run, from the `tests/` directory;
avoid a broad `skills remove --all` when unrelated skills are installed.
