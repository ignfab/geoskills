# Output formats

| Format      | `-f` value       | Typical extension  | Notes |
|-------------|------------------|--------------------|-------|
| GeoPackage  | `GPKG`           | `.gpkg`            | Single file, SQLite-based, widely supported. Recommended default. |
| GeoJSON     | `GeoJSON`        | `.geojson`         | Good for the web; large datasets get heavy. |
| GeoParquet  | `Parquet`        | `.parquet`         | Columnar, good for analytics; one layer per file; needs a writable Parquet driver. |
| Shapefile   | `ESRI Shapefile` | directory + `.shp` | Legacy: 10-character field names, 2 GB limit. Prefer GPKG. |
| GML         | `GML`            | `.gml`             | XML, interoperable, verbose. |

Inspect the requested driver with `ogrinfo --format <driver>` before downloading;
require vector support and `Create()` capability for the output. If a capability is
missing, follow the [tooling rule](../SKILL.md#tooling-rule) rather than changing tools
or formats silently.

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

Use a GDAL build with the Arrow/Parquet driver and confirm that its creation options
include the chosen compression codec (`ogrinfo --format Parquet`). Installing Python's
`pyarrow` does not enable Parquet in an unrelated GDAL CLI installation.

```bash
ogr2ogr -progress -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f Parquet \
  -lco GEOMETRY_NAME=geometry \
  -lco COMPRESSION=SNAPPY \
  batiments.parquet \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

The GDAL Parquet writer creates **one layer per file**. To export municipalities and
departments, discover both typenames and run one export per typename, for example to
`communes.parquet` and `departments.parquet`. Do not use the GeoPackage multi-layer
`-update -nln` recipe to put both layers in one Parquet file. Reopen each file and check
its count, attributes, CRS and extent independently.

### Missing GDAL or Parquet support

Offer these choices and let the user select an environment. The commands that install
software or download an image are for the **user** to run. The agent does not execute
them. Afterwards, use the same environment for discovery, conversion and validation.

- **Conda / Mamba:** in the intended environment, the user can run
  `conda install -c conda-forge gdal libgdal-arrow-parquet` (or replace `conda` with
  `mamba`). The plugin and GDAL must be compatible; do not mix a Conda plugin with the
  distribution's `ogr2ogr`. Recheck `ogr2ogr --version`, `ogrinfo --format WFS` and
  `ogrinfo --format Parquet` after the user selects the environment.
- **Distribution packages:** the user can run `sudo apt install gdal-bin` on
  Ubuntu/Debian, but only use that installation if it provides the required driver and
  creation options. Reinstalling the same build does not add an omitted driver.
- **Docker:** with Docker already available, offer the official OSGeo **ubuntu-full**
  image. The documented **ubuntu-small** image lacks Parquet. Check the chosen image's
  capabilities rather than assuming that every driver is included. This keeps GDAL in
  the container, without replacing the host installation.

For a reproducible example, use the published release image below. If it is not already
present, give the user `docker pull ghcr.io/osgeo/gdal:ubuntu-full-3.13.3`. Once the image
is available and the user has chosen this option, check it without an implicit pull:

```bash
GDAL_IMAGE=ghcr.io/osgeo/gdal:ubuntu-full-3.13.3
docker run --rm --pull=never "$GDAL_IMAGE" ogrinfo --format WFS
docker run --rm --pull=never "$GDAL_IMAGE" ogrinfo --format Parquet
```

Discover the actual typename, fields and CRS as usual, then adapt this bounded example
in a POSIX shell. Choose an unused output path; the UID/GID options preserve file ownership:

```bash
docker run --rm --pull=never -u "$(id -u):$(id -g)" -v "$PWD:/data" "$GDAL_IMAGE" \
  ogr2ogr -progress -f Parquet -lco COMPRESSION=SNAPPY \
  -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  /data/batiments.parquet "WFS:https://data.geopf.fr/wfs/ows" "BDTOPO_V3:batiment"

docker run --rm --pull=never -u "$(id -u):$(id -g)" -v "$PWD:/data" "$GDAL_IMAGE" \
  ogrinfo -al -so /data/batiments.parquet
```

If neither a suitable GDAL installation nor a GDAL container is usable, explain that
limitation and propose Python only as an agreed last resort. Do not install Python
dependencies or invoke `uv` to bypass the missing driver automatically.

Sources: [GDAL Parquet driver and Conda plugin](https://gdal.org/en/stable/drivers/vector/parquet.html),
[official GDAL images and release tags](https://github.com/OSGeo/gdal/tree/master/docker).

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
