# Output formats

| Format      | `-f` value       | Typical extension  | Notes |
|-------------|------------------|--------------------|-------|
| GeoPackage  | `GPKG`           | `.gpkg`            | Single file, SQLite-based, widely supported. Recommended default. |
| GeoJSON     | `GeoJSON`        | `.geojson`         | Good for the web; large datasets get heavy. |
| GeoParquet  | `Parquet`        | `.parquet`         | Columnar, good for analytics; needs the Parquet driver. |
| Shapefile   | `ESRI Shapefile` | directory + `.shp` | Legacy: 10-character field names, 2 GB limit. Prefer GPKG. |
| GML         | `GML`            | `.gml`             | XML, interoperable, verbose. |

Check that a driver is available: `ogr2ogr --formats | grep -i <name>`.

## GeoPackage (GPKG)

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GPKG batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

Add a new layer to an existing GeoPackage with `-update` and an explicit layer name:

```bash
ogr2ogr -f GPKG -update -nln regions territoire.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "ADMINEXPRESS-COG.LATEST:region"
```

Use `-append -nln <existing_layer>` only to add features to an existing layer with a
compatible schema. Repeating an append may duplicate features or fail on existing IDs.

## GeoJSON

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GeoJSON -lco RFC7946=YES batiments.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

`-lco RFC7946=YES` produces standard GeoJSON in WGS84 longitude/latitude, reprojecting
when necessary. The driver otherwise allows legacy GeoJSON with another CRS.
BD TOPO geometry may include a third coordinate; GDAL may then identify the output as
WGS84 3D (EPSG:4979). Use `-dim XY` only if the requested deliverable is explicitly 2D,
and do not infer a trustworthy vertical datum from the presence of a Z value alone.

## GeoParquet

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f Parquet \
  -lco GEOMETRY_NAME=geometry \
  -lco COMPRESSION=SNAPPY \
  batiments.parquet \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

Requires a GDAL build with the Parquet driver (`ogr2ogr --formats | grep -i Parquet`).

## Shapefile

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f "ESRI Shapefile" batiments_shp \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

The output is a **directory** holding `.shp`, `.dbf`, `.shx` and `.prj`.

## GML

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GML batiments.gml \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```
