# 2. Access and extract

**Question:** how do I retrieve the right subset?

Fetch only the files, features or pixels the request needs, from the Géoplateforme, API
Carto or another GeoServer: downloads, WFS and raster extracts, server-side filters and
geocoding. Calculation services that derive new values (elevations, routes, reachable
areas) are in [4. Analyze and derive](../4-analyze/README.md).

| Skill | Use it to |
| --- | --- |
| [geopf-download-files](geopf-download-files/README.md) | Paginated Atom discovery, edition selection, foreground transfers, safe resume and integrity checks. |
| [geopf-wfs-download](geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) with `ogr2ogr` and check export counts and source IDs. |
| [geopf-wms-wmts](geopf-wms-wmts/README.md) | Download raster layers (orthophotos, Plan IGN, elevation) from the Géoplateforme WMTS / WMS-R with GDAL. |
| [geoserver-cql-filter](geoserver-cql-filter/README.md) | Write GeoServer WFS/WMS ECQL filters, including URL encoding and CRS:84 geometries with EWKT. |
| [apicarto](apicarto/README.md) | Query API Carto for parcels, urban-planning zones and easements, protected areas and RPG parcels at a point, in an area or by code, with complete pagination. |
| [geopf-geocoding](geopf-geocoding/README.md) | Geocode addresses, POIs and parcels, and review CSV matches, ambiguity and unmatched rows. |

## Also relevant

- [bdtopo-schema-guide](../1-discover/bdtopo-schema-guide/README.md) clarifies model meanings
  before extraction; service identifiers still come from live metadata.
- [geopf-services](../1-discover/geopf-services/README.md) chooses the access route before
  any of these skills runs.
- [gdal-vector-basics](../3-prepare/gdal-vector-basics/README.md) filters, clips and queries
  local vector files with SQL.
- [geopandas-basics](../4-analyze/geopandas-basics/README.md) reads small WFS extracts
  directly into Python.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access
```

Previous: [1. Discover and select](../1-discover/README.md) ·
Next: [3. Prepare and check](../3-prepare/README.md) · [All families](../../README.md#skills)
