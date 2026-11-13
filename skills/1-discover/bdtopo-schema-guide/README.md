# bdtopo-schema-guide

**Family:** [1. Discover and select](../README.md).

Version-aware BD TOPO semantics for buildings and roads, with traceable IGN sources. The
skill answers data-model questions (which class and field describe a concept, with its
type, units, special values and Shapefile name) from a curated offline snapshot of IGN's
BD TOPO content specification, model 3.5, July 2026 revision. Every answer cites the model
version, document revision and pages, and lists what remains unverified.

## When to use it

- Find the class and field that describe building height, and what a zero height means.
- Identify the road-segment class and its fields for importance and number of lanes,
  with their documented Shapefile names.
- Check whether a field documented for model 3.5 can be assumed identical in an older
  export, such as 3.3 (without a source for that model, the answer is "unverified").
- Understand field types, units and special values before computing statistics on
  BD TOPO data.
- Compare the static model with what a live WFS layer advertises (GetCapabilities and
  DescribeFeatureType), without downloading features.

## When to use another skill

- Download a BD TOPO layer that is already identified, from the WFS:
  [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md)
- Download ready-made BD TOPO archives:
  [`geopf-file-download`](../../2-access/geopf-file-download/README.md)
- Count buildings per municipality, or compute other territorial indicators from local
  layers: [`spatial-aggregation`](../../4-analyze/spatial-aggregation/README.md)

## What you get

- An answer naming the class, fields, geometry, documented type, units and special values,
  format-specific identifiers, source URL, model version, document revision and pages,
  then the unresolved facts and the next access or analysis skill (named, not run).
- Optionally, JSON from `scripts/lookup.py`: `documented` with the field facts and source,
  or `unverified` for any version, revision, class, field or format outside the snapshot.
- Coverage: `batiment` (`hauteur`, `nature`, `usage_1`) and `troncon_de_route` (`nature`,
  `importance`, `nombre_de_voies`), with PostgreSQL and Shapefile names. Administrative
  classes and other themes are outside the subset.

Before reporting, the agent checks that each class and field resolves to the snapshot or
to a newly cited official source, that the answer addresses the actual concept, and that
enumerations are labeled partial where applicable (only road importance, 1–6, is
complete). It never invents an output CRS or feature count; for a supplied file it reports
only what the file's metadata shows.

This is a small documented subset, not a full schema validator or migration tool. Unknown
versions/fields return `unverified`, never guessed mappings: a field missing from the
subset is not proof that it is absent or renamed, and a guessed field is never uppercased
or truncated automatically. Source PDFs are referenced, not redistributed. Model 3.5 and
document revision July 2026 are separate from delivery dates.

## Requirements

- No GIS tools or network for bundled reference lookup. The optional helper uses Python 3's
  standard library; Markdown remains usable without Python.
- Online metadata checks can use existing `curl` against the Géoplateforme WFS
  (`https://data.geopf.fr/wfs/ows`); the documented requests carry no API key. User-run
  Debian/Ubuntu installation: `sudo apt install curl`.
- The agent never installs software and never runs interactive login or setup commands.

## MCP servers

Optional. With the [Geocontext](https://github.com/ignfab/geocontext) MCP server
connected, the agent first reads the properties of the WFS type (names, types, allowed
values) from the schema catalogue bundled with that server. It names that source, reports
it apart from the versioned model, which stays the reference for the model version, the
document revision and the special values, and checks the live service when the answer must
reflect it. Without the server, or when a call fails, nothing changes. See
[MCP servers](../../../docs/mcp-servers.md).

## Installation

```bash
npx skills add ignfab/geoskills --skill bdtopo-schema-guide
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/1-discover`.

## Example

> Without network access or downloads, explain for the BD TOPO 3.5 model documented in
> July 2026 which class and field describe building height, what zero means, and cite the
> source.

Expected answer: class `batiment`, field `hauteur` (`HAUTEUR` in Shapefile), in meters
from the lowest adjacent ground to the highest eaves edge (not the roof ridge); zero means
unknown or not significant; model 3.5, July 2026 revision, pages 76–77. The offline lookup:

```bash
python3 scripts/lookup.py --version 3.5 --revision 2026-07 --class batiment --field hauteur
python3 scripts/lookup.py --version 3.5 --revision 2026-07 --class troncon_de_route --field NB_VOIES --format shapefile
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Version selection, lookup and answer validation. |
| [references/sources-and-versions.md](references/sources-and-versions.md) | Sources: provenance (URL, revision, checked date, SHA-256) and refresh procedure. |
| [references/themes-and-classes.md](references/themes-and-classes.md) | Classes: building/road selection, geometry and source pages. |
| [references/attributes-and-enums.md](references/attributes-and-enums.md) | Attributes: names, units and special values, before downstream statistics. |
| [references/formats-and-services.md](references/formats-and-services.md) | Formats/services: model, edition, format and live WFS schema kept apart. |
| [references/schema-3.5-2026-07.json](references/schema-3.5-2026-07.json) | Versioned JSON subset: exact curated facts with page references. |
| [scripts/lookup.py](scripts/lookup.py) | Offline, fail-closed lookup in the versioned subset. |

## Tests

French agent scenarios: [tests/bdtopo-schema-guide.md](../../../tests/bdtopo-schema-guide.md)
(2 positive + 2 negative). Offline: [test_bdtopo_schema_guide.py](../../../tests/test_bdtopo_schema_guide.py)
(lookups, unknown versions or fields never inferred, every entry traced to a source). No
live test.

## Related skills

- [`geospatial-descriptive-statistics`](../../4-analyze/geospatial-descriptive-statistics/README.md)
  summarizes a layer's attributes; it points to this skill (or producer metadata) to tell
  a BD TOPO sentinel zero, such as an unknown height, from a valid zero.
- [`spatial-aggregation`](../../4-analyze/spatial-aggregation/README.md) computes
  territorial indicators; this skill optionally clarifies the BD TOPO fields it summarizes.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  uses this skill's versioned subset to verify height and usage semantics when it applies.
