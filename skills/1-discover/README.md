# 1. Discover and select

**Question:** which data should be used for this request?

Find the candidate datasets and services, then select one by coverage, resolution, edition
and fitness for the request, before anything is downloaded. Understand versioned data
models and attribute meanings before choosing fields.

| Skill | Use it to |
| --- | --- |
| [geopf-service-selection](geopf-service-selection/README.md) | Choose a Géoplateforme API for dataset discovery, maps, vector features, downloads, geocoding and geographic calculations. |
| [bdtopo-schema-guide](bdtopo-schema-guide/README.md) | Understand versioned BD TOPO building/road classes, field meanings and format mappings using sourced offline references. |

## Choose between them

- To decide which Géoplateforme service answers a need (dataset discovery, map display,
  vector features, downloads, geocoding or calculations), use `geopf-service-selection`. It explains
  and recommends; an access or calculation skill then does the work.
- To understand what a BD TOPO class or field means for a given version, including its
  special values, use `bdtopo-schema-guide`. It reads bundled, sourced references offline;
  layer and field identifiers still come from the live service metadata.
- Both answer before anything is downloaded; neither downloads data.

## What they need

Reuse existing tools and check only the selected operation. Installing this family does
not install a GIS stack; see the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions | Network |
| --- | --- | --- | --- |
| `bdtopo-schema-guide` | Bundled Markdown/JSON; no runtime needed to read it | Python 3 standard library for the lookup helper; HTTP client for current online sources | None |
| `geopf-service-selection` | Documentation and service metadata; no local GIS runtime | Existing browser/HTTP client for discovery; curl for CLI examples | Official guides and service metadata |

**Optional MCP server.** With [Geocontext](https://github.com/ignfab/geocontext)
connected, both skills use it first: to answer simple questions without a file, and to
read the properties of a WFS type from the schema catalogue bundled with that server. See
[MCP servers](../../docs/mcp-servers.md).

## Also relevant

- [municipality-building-profile](../6-workflows/municipality-building-profile/README.md)
  combines source interpretation, analysis and optional QGIS delivery for one municipality.
- [geopf-file-download](../2-access/geopf-file-download/README.md) selects a territory,
  edition, format and CRS from the Download API metadata.
- [geopf-altimetry](../4-analyze/geopf-altimetry/README.md) selects an elevation resource by
  product, coverage and resolution.
- [geodata-intake](../3-prepare/geodata-intake/README.md) reports what a received delivery
  actually contains.

## Not covered yet

- Comparing candidate products by resolution, edition and fitness for the request.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/1-discover
```

Next: [2. Access and extract](../2-access/README.md) · [All families](../../README.md#skills)
