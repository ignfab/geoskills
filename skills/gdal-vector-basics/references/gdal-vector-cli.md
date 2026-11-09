# The `gdal vector` commands

GDAL 3.11 introduced a single `gdal` command with named sub-commands. The examples below
were checked with GDAL 3.13 on 2026-10-29. The command is still **provisional**: it prints a
warning saying that names and behavior may change. Check `gdal vector <command> --help`
before using an option, and keep `ogr2ogr` when the user's GDAL is older or a script must
stay stable.

## Differences that matter

- `gdal vector convert` **refuses** an existing output unless you pass `--overwrite`,
  `--update`, `--append` or `--overwrite-layer`. `ogr2ogr` silently recreates it.
- Options are long and named (`--dst-crs`, `--where`, `--output-layer`), and open options
  are written `--oo KEY=VALUE`.
- A pipeline chains steps with `!` and writes once, without intermediate files.

## Inspect and convert

```bash
gdal vector info --format text communes.shp
gdal vector convert --oo ENCODING=CP1252 --output-layer communes communes.shp communes_cli.gpkg
```

## Pipelines

Read a legacy Shapefile, reproject it, filter it and write one GeoPackage layer:

```bash
gdal vector pipeline read --oo ENCODING=CP1252 communes.shp \
  ! reproject --dst-crs EPSG:4326 \
  ! filter --where "code_insee LIKE '94%'" \
  ! write --output-layer communes communes_94_wgs84.gpkg
```

`select --fields` lists the fields to keep **and the geometry field**. A Shapefile
geometry has no name: list it as `_ogr_geometry_`, or the output has no geometry
(`Geometry: None`). `select --exclude --fields remarque` removes fields instead.

## Clip, merge and split

Clip to the polygons of another dataset, reprojected when it declares a CRS, or to a box
whose CRS is stated with `--bbox-crs`:

```bash
gdal vector clip --like zone.geojson --output-layer parcels parcels.geojson parcels_clip_cli.gpkg
gdal vector clip --bbox 2.35975,48.82932,2.35998,48.82962 --bbox-crs EPSG:4326 \
  --output-layer parcels parcels.geojson parcels_bbox_cli.gpkg
```

Merge several files into one layer with a source column:

```bash
gdal vector concat --mode single --output-layer parcels \
  --source-layer-field-name source --source-layer-field-content "{DS_BASENAME}" \
  sheets/sheet_1.gpkg sheets/sheet_2.gpkg parcels_merged.gpkg
```

Write one file per value of a field (`--scheme flat` gives readable file names):

```bash
gdal vector partition --field code_insee --scheme flat -f GPKG communes_points.geojson parts
```

The same family includes `reproject`, `filter`, `sql`, `explode-collections`,
`set-geom-type`, `make-valid`, `check-geometry` and `simplify`. For geometry validity and
coverage checks, follow the `vector-data-quality` skill; for simplification of shared
borders, the `mapshaper-simplify` skill.

Reference: <https://gdal.org/programs/gdal_vector.html>
