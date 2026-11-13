# 2. Access and extract

**Question:** how do I retrieve the right subset?

Fetch only the files, features or pixels the request needs, from the Géoplateforme, API
Carto or another GeoServer: downloads, WFS and raster extracts, server-side filters and
geocoding. Calculation services that derive new values (elevations, routes, reachable
areas) are in [4. Analyze and derive](../4-analyze/README.md).

| Skill | Use it to |
| --- | --- |
| [geopf-file-download](geopf-file-download/README.md) | Paginated Atom discovery, edition selection, foreground transfers, safe resume and integrity checks. |
| [geopf-wfs-download](geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) with `ogr2ogr` and check export counts and source IDs. |
| [geopf-raster-download](geopf-raster-download/README.md) | Download raster layers (orthophotos, Plan IGN, elevation) from the Géoplateforme WMTS / WMS-R with GDAL. |
| [geoserver-cql-filter](geoserver-cql-filter/README.md) | Write GeoServer WFS/WMS ECQL filters, including URL encoding and CRS:84 geometries with EWKT. |
| [apicarto-query](apicarto-query/README.md) | Query API Carto for parcels, urban-planning zones and easements, protected areas and RPG parcels at a point, in an area or by code, with complete pagination. |
| [geopf-geocoding](geopf-geocoding/README.md) | Geocode addresses, POIs and parcels, and review CSV matches, ambiguity and unmatched rows. |

## Runtime dependencies

Reuse existing tools and check only the selected operation. Installing this family does
not require every tool below; see the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions |
| --- | --- | --- |
| `apicarto-query` | Python 3 standard library for pagination; curl for manual requests | GDAL for the documented spatial validation/conversion |
| `geopf-file-download` | curl and standard-library Python feed inspection | Reader matching the archive (Python can test ZIP); GDAL for spatial content checks |
| `geopf-geocoding` | HTTP client; curl for examples | Standard-library Python for CSV helpers; jq or existing Python for JSON; GDAL for conversion |
| `geopf-raster-download` | GDAL CLI with the requested WMS/WMTS support | Only missing drivers for the selected input/output formats |
| `geopf-wfs-download` | GDAL CLI with WFS and output driver; curl for discovery | Standard-library Python for the GeoPackage audit; Arrow/Parquet driver only for GeoParquet |
| `geoserver-cql-filter` | Service metadata to compose a filter; no local GeoServer | HTTP client for requests; downstream extraction tool for the requested delivery |

A transfer can succeed before spatial validation is possible. Report outstanding checks;
do not declare the dataset validated just because an optional later stage was skipped.

## Also relevant

- [bdtopo-schema-guide](../1-discover/bdtopo-schema-guide/README.md) clarifies model meanings
  before extraction; service identifiers still come from live metadata.
- [geopf-service-selection](../1-discover/geopf-service-selection/README.md) chooses the access route before
  any of these skills runs.
- [gdal-vector-processing](../3-prepare/gdal-vector-processing/README.md) filters, clips and queries
  local vector files with SQL.
- [geopandas-vector-analysis](../4-analyze/geopandas-vector-analysis/README.md) reads small WFS extracts
  directly into Python.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access
```

Previous: [1. Discover and select](../1-discover/README.md) ·
Next: [3. Prepare and check](../3-prepare/README.md) · [All families](../../README.md#skills)
