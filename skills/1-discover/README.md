# 1. Discover and select

**Question:** which data should be used for this request?

Find the candidate datasets and services, then select one by coverage, resolution, edition
and fitness for the request, before anything is downloaded. Understand versioned data
models and attribute meanings before choosing fields.

| Skill | Use it to |
| --- | --- |
| [geopf-service-selection](geopf-service-selection/README.md) | Choose a Géoplateforme API for dataset discovery, maps, vector features, downloads, geocoding and geographic calculations. |
| [bdtopo-schema-guide](bdtopo-schema-guide/README.md) | Understand versioned BD TOPO building/road classes, field meanings and format mappings using sourced offline references. |

## Runtime dependencies

Reuse existing tools and check only the selected operation. Installing this family does
not install a GIS stack; see the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions |
| --- | --- | --- |
| `bdtopo-schema-guide` | Bundled Markdown/JSON; no runtime needed to read it | Python 3 standard library for the lookup helper; HTTP client for current online sources |
| `geopf-service-selection` | Documentation and service metadata; no local GIS runtime | Existing browser/HTTP client for discovery; curl for CLI examples |

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
