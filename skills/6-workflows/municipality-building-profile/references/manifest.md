# Input manifest

Paths resolve relative to this JSON file. The names below are examples, **not assumed
service fields**. Discover names from each file; GeoPackage inputs require `layer` even
when there is only one layer. The output directory is a separate, unused path.

```json
{
  "municipality": {
    "path": "data/municipalities.gpkg", "layer": "municipalities",
    "id_field": "code", "id": "94067",
    "source": "Boundary delivery name", "edition": null, "accessed_on": null
  },
  "buildings": {
    "path": "data/buildings.gpkg", "layer": "buildings", "id_field": "id",
    "geometry_scope": "whole_objects",
    "source": "Building delivery name", "edition": null, "accessed_on": null,
    "completeness": {"status": "unknown", "evidence": null}
  },
  "analysis_crs": "EPSG:2154",
  "height": {
    "field": "height", "unit": "m", "missing_values": [],
    "semantics": "Replace with the documented height definition and special-value policy",
    "source": "Replace with the applicable delivery specification and page"
  },
  "usage": {
    "field": "usage",
    "semantics": "Replace with the selected attribute's documented meaning",
    "source": "Replace with the applicable delivery specification and page"
  }
}
```

`height` and `usage` are optional: remove them when not requested or when semantics cannot
be verified, and explain why the corresponding indicators are absent. A requested field
that does not exist is an error. Use `null` for unknown source dates/editions, not invented
metadata. Never include authenticated URLs or credentials in provenance fields.

Set `analysis_crs` to a suitable existing/requested local projected CRS (authority code
or WKT). The helper accepts known compatible linear units, including feet, and converts
all area fields to m²; height units remain a separate requirement. It rejects geographic
CRSs, EPSG:3857, unknown/incompatible axis units and a municipality outside a known area
of use. This does not establish that every other projection is suitable; justify the
choice. EPSG:2154 above is a metropolitan-France example, not a hard-coded default.

`geometry_scope` must be `whole_objects`. Completeness is `complete`, `partial` or
`unknown` (default). `complete` requires a nonempty evidence string, such as matching
source/export counts and IDs on the bounded extraction, or a documented complete local
fixture. The helper records this declaration; it does not contact a service to prove it.

Height policy is explicit. `missing_values: []` preserves valid zeroes. When the applicable
BD TOPO documentation defines zero as unknown/not significant, record that source and use
`missing_values: [0]`. Do not apply this code to unrelated sources or versions by habit.
All statistics use metre heights, not geometry Z values. Blank/null, sentinel and invalid
(nonnumeric, negative without a declared code, or nonfinite) heights are counted separately.

Choose one usage field and retain its labels/codes. Do not merge primary/secondary fields
or infer an official use from a generic nature code. Empty strings and null are a missing
category; literal strings such as `NA` and `001` remain categories.
