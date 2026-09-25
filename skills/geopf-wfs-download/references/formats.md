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
ogr2ogr -f GPKG batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

Several layers can be appended to the same file with `-update -append`:

```bash
ogr2ogr -f GPKG -update -append territoire.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "ADMINEXPRESS-COG.2020:region"
```

## GeoJSON

```bash
ogr2ogr -f GeoJSON batiments.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

GeoJSON is expected in EPSG:4326 by consumers; add `-t_srs EPSG:4326` if the source is in
Lambert-93 (EPSG:2154).

## GeoParquet

```bash
ogr2ogr -f Parquet \
  -lco GEOMETRY_NAME=geometry \
  -lco COMPRESSION=SNAPPY \
  batiments.parquet \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

Requires a GDAL build with the Parquet driver (`ogr2ogr --formats | grep -i Parquet`).

## Shapefile

```bash
ogr2ogr -f "ESRI Shapefile" batiments_shp \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

The output is a **directory** holding `.shp`, `.dbf`, `.shx` and `.prj`.

## GML

```bash
ogr2ogr -f GML batiments.gml \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```
