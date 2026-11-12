# Municipal building profile: validation review, 2026-11-12

The first skill in `6-workflows`, `municipality-building-profile`, connects input discovery,
explicit building semantics, one municipal analysis population and optional QGIS delivery.
It is implemented in [PR #56](https://github.com/ignfab/geoskills/pull/56).

## Functional checks

- Twelve new offline regressions use independently specified rectangles, overlaps, holes
  and multipart polygons. They check counts, union area, cross-boundary/touch-only handling,
  height sentinels and invalid values, usage categories, missing/partial inputs, CRS/Z
  handling, duplicate IDs/geometries, source hashes and real GeoPackage/CSV/JSON round trips.
- For the main fixture: four selected buildings, 10,000 m² municipality, 850 m² union
  footprint (8.5%), 950 m² summed clipped area and 100 m² overlap excess. Two valid heights
  yield mean/median 15 m; one height is a sentinel and one is missing. Source IDs and the
  literal category `NA` survive export.
- An early empty-inventory run exposed an empty GeoSeries retaining geometry dtype during
  boolean operations. Explicit boolean masks fixed it; the regression now reopens the
  municipality and both empty output layers successfully.
- The full offline suite passed: **172 tests, 25 expected optional/live skips**. The final
  municipality/CRS identification in CSV was also checked by rerunning all 12 new tests.
- Metadata, local links and skill-creator validation passed; the cached Skills CLI 1.7.6
  discovered 22 skills and installed `6-workflows` into a fresh isolated agent directory.
- Three positive and three negative French scenarios are registered with the A/B runner.
  Its dry run verifies registration; this does not claim that every scenario was executed
  by a real agent.

## Independent forward pilot

An independent Codex subagent received only the XP-14 request, copied input files, this
skill and optional styling/project skills, plus the locations of existing environments.
It received no expected numeric answers or repository test code. It ran the unmodified
helpers, independently calculated the geometric results, checked reports/source hashes,
created QML and a real QGZ, and rendered the project in QGIS 3.44.9.

The complete bundle was copied to another location while the original was renamed out
of reach. All three layers reopened with sources inside the relocated directory. The
project retained building-over-boundary ordering, a red unfilled boundary and the expected
layer visibility. Both renders were inspected; inputs and the analytic GeoPackage were
unchanged. The parent agent also inspected the reported values, hashes, source paths and
rendered preview. The actual pilot is logged as XP-14 in [the run log](prompts/runs.md).
Versions, fixture hashes and observed outcomes are in the
[machine-readable evidence](reports/2026-11-12-municipality-building-profile.json).

The pilot highlighted a documentation gap: the analytic helper initially records that it
has not created a QGIS project. After the separate QGIS stage, the evaluator updated the
generated audit/report. The workflow now explicitly requires that reconciliation so final
delivery status agrees with the created and verified project.

## Limits

This is one offline forward pilot, not a paired A/B campaign or an automatic-discovery
benchmark. The subagent's inherited model identifier was not exposed and is recorded as
unknown. No new live WFS extraction was tested for this workflow; acquisition routes
through existing skills and their own checks. Synthetic input provenance and height/usage
conventions were supplied in the manifest; unspecified editions remain unknown.

The helper rejects invalid geometry, duplicate/missing IDs, unknown CRSs and pre-clipped
building input. It records completeness evidence but cannot establish completeness merely
from a supplied file. Counts refer to source objects and are non-additive across municipal
boundaries. No residents, dwellings, floor areas or volumes are inferred. QGIS remains an
optional additional output, requiring its own real reopening/relocation verification.
