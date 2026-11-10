# 1. Discover and select

**Question:** which data should be used for this request?

Find the candidate datasets and services, then select one by coverage, resolution, edition
and fitness for the request, before anything is downloaded.

| Skill | Use it to |
| --- | --- |
| [geopf-services](geopf-services/README.md) | Choose a Géoplateforme API for dataset discovery, maps, vector features, downloads, geocoding and geographic calculations. |

## Also relevant

- [geopf-download-files](../2-access/geopf-download-files/README.md) selects a territory,
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
