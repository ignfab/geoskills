---
name: bdtopo-schema-guide
description: Explain versioned IGN BD TOPO classes, attribute meanings, types and special values from official specifications, with offline references for buildings and roads. Use to select or understand the data model before access; not to download identified layers, validate an entire production schema or compute territorial indicators.
---

# BD TOPO schema guide

Answer semantic model questions with a class, fields, source version/revision and explicit
unknowns. This is a curated **buildings and roads** subset, not every BD TOPO class.
Downloads belong to `geopf-wfs-download` or `geopf-file-download`; local counts belong to
`spatial-aggregation`. No network call is needed for the offline path.

## MCP servers

Optional. When the [Geocontext](https://github.com/ignfab/geocontext) MCP server is
connected (tools often prefixed `mcp__geocontext__`), use it first to find a WFS type and
read its properties: `gpf_search_types` finds the type from French keywords, and
`gpf_describe_type` returns the property names, types, descriptions and allowed values
(`gpf_wfs_search_types` and `gpf_wfs_describe_type` in Geocontext 0.9). They come from a
schema catalogue bundled with the server, not from the service itself: name that source,
report it apart from the versioned model, and use step 4 when the answer must reflect the
live service. The versioned model stays the source for the model version, the document
revision and the special values; when the catalogue and the model differ, report the
difference instead of merging them. Without Geocontext, or when a call fails, follow step
4 as written. Never install, configure or start an MCP server yourself.

## Prerequisites

Read the bundled Markdown/JSON without GIS software. The optional lookup needs Python 3
standard library only. Never install software or run interactive login/setup. If Python
is absent, use the references directly; no installation is necessary for this skill.
Online service verification optionally uses existing `curl` or a web tool. If curl is
missing, the user can run `sudo apt install curl` on Debian/Ubuntu; do not run it yourself.

## Choose the applicable schema

1. Identify product model version, **document revision**, dataset edition and delivery
   format from supplied evidence. None implies the others. If unknown, describe the
   bundled 3.5 / July 2026 snapshot conditionally and ask for metadata before claiming
   compatibility with the user's data. Do not presume the latest document applies.
2. Read [classes](references/themes-and-classes.md) and
   [attributes](references/attributes-and-enums.md). For an exact offline lookup, resolve
   the helper from this skill folder:

```bash
python3 scripts/lookup.py --version 3.5 --revision 2026-07 --class batiment --field hauteur
python3 scripts/lookup.py --version 3.5 --revision 2026-07 --class troncon_de_route --field NB_VOIES --format shapefile
```

3. An unlisted version, class, field or format is **unverified**, not automatically absent
   or renamed. Check the applicable official specification/change history before claiming
   an addition, removal or mapping. Do not auto-uppercase or truncate a guessed field.
4. For online WFS-specific advice, first inspect capabilities and DescribeFeatureType as
   explained in [formats and services](references/formats-and-services.md). Keep the live
   schema observation separate from the static model. Do not download features just to
   answer a documentation question.

## Validate the output

Each recommended class/field must resolve to the selected snapshot or an explicitly cited
new official source. State geometry, documented type/units/special values, format-specific
identifiers, source URL, model version, document revision/date and relevant pages. Check
that the answer addresses the actual concept and that enumerations are labeled partial
where applicable. This task has no output CRS or feature count; never invent them. For a
supplied file, report only the CRS/count observed from metadata. List unresolved facts and
name the next access/analysis skill without requiring its installation or running it.

## References

- [Sources and versions](references/sources-and-versions.md): provenance and refresh procedure.
- [Themes and classes](references/themes-and-classes.md): building/road selection.
- [Attributes and enums](references/attributes-and-enums.md): names, units and special values.
- [Formats and services](references/formats-and-services.md): delivery versus live schema.
- [Versioned subset](references/schema-3.5-2026-07.json): exact curated facts with page references.
