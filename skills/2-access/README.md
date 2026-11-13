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

## Choose between them

- Whole products by territory and edition (archives or tiles): `geopf-file-download`.
- Vector features filtered by area or attribute, converted to the format you need:
  `geopf-wfs-download`. To write or debug a GeoServer `cql_filter` for such a request, use
  `geoserver-cql-filter`.
- Raster images and grids over an extent (orthophotos, Plan IGN, elevation): `geopf-raster-download`.
- What lies at a point or in an area (cadastral parcels, urban-planning zones, easements,
  protected areas, RPG crops), or every parcel of a municipality: `apicarto-query`.
- Coordinates for addresses, places or parcels, reverse geocoding, or a review of results
  that are already geocoded: `geopf-geocoding`.

## What they need

| Skill | Local tools | Network |
| --- | --- | --- |
| `geopf-file-download` | `curl`, Python 3, GDAL, an archive reader (`unzip`, `7z`) | Géoplateforme Download API |
| `geopf-wfs-download` | GDAL with WFS support and the requested output driver, `curl` | Géoplateforme WFS |
| `geopf-raster-download` | GDAL with the WMTS and WMS drivers | Géoplateforme WMTS and WMS-R |
| `geoserver-cql-filter` | None to write a filter; `curl` to send it | The GeoServer you query |
| `apicarto-query` | `curl`, Python 3; GDAL to convert and check results | API Carto; a key only for the wine appellation module (`aoc`) |
| `geopf-geocoding` | `curl`; Python 3 for the helpers | Géoplateforme geocoding API; none to review existing results |

The requests documented by these skills use public endpoints without credentials; only the
API Carto `aoc` module needs a key. Some other Géoplateforme APIs (extraction, standards
validation, usage statistics) require authentication: `geopf-service-selection` describes them, and
the agent leaves any login to you. It never installs a missing tool either: it gives you
the command to run.

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
