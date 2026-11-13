# geodata-intake

**Family:** [3. Prepare and check](../README.md).

Read-only inventory of formats, layers, metadata and missing CRS evidence. Given unfamiliar
local files or a mixed delivery (vector files, rasters, CSVs, archives), the skill reports
what each dataset contains and what metadata is missing, then recommends the next
operation, without changing the source.

## When to use it

- Inventory a received delivery before choosing a workflow: formats, layers, fields,
  extents, raster dimensions and declared CRSs.
- Check whether received GIS files are ready to use, and list the metadata they lack.
- Report a missing `.prj` or an undeclared raster CRS without guessing one from the
  coordinates.
- Examine a CSV with coordinates: delimiter, encoding, coordinate column names and order,
  and value ranges.
- List the members of an archive before extracting only the required files.

## When to use another skill

- An already specified vector conversion, encoding fix or clip, such as GeoJSON to
  GeoPackage: [`gdal-vector-processing`](../gdal-vector-processing/README.md) on the command line,
  or [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md) in Python, which also
  covers vector joins and overlays.
- Raster processing: [`gdal-raster-processing`](../gdal-raster-processing/README.md).
- A confirmed reprojection or a French CRS question:
  [`crs-reprojection-france`](../crs-reprojection-france/README.md).
- Geometry repair or a coverage audit (a metadata inventory is not a geometry audit):
  [`vector-data-quality`](../vector-data-quality/README.md).
- A known online service task: use the specialized skill of that service directly.

## What you get

- A table of datasets with their evidence and missing metadata: layer names, schema, CRS
  or `unknown`, extent, feature count or raster dimensions, and file size where obtained,
  followed by the recommended next operation.
- One entry per logical dataset: Shapefile sidecars count as one dataset, and unreadable or
  empty datasets are listed too. Deferred scans are marked `not inspected`.
- Before reporting, the agent reconciles the inventory with the supplied files, flags
  implausible coordinate magnitudes or empty layers without guessing a repair, confirms that
  source files and sidecars are unchanged, and states which checks ran. Raster metadata is
  read with `GDAL_PAM_ENABLED NO`, so no `.aux.xml` sidecar is written next to the source.
- A missing or uncertain CRS stays unknown: coordinate ranges alone do not establish an EPSG
  code, and the agent does not use `-a_srs` to silence the warning. It does not invent
  source dates.
- Only the supplied files are inspected. Archive members are listed before selected files
  are extracted to a separate directory; absolute paths and `..` traversal are rejected, and
  bundled scripts are never executed.

## Requirements

GDAL/OGR CLI for vector/raster metadata and Python 3's standard library for CSV/JSON
recipes. CSV-only inspection needs no GDAL. No GeoPandas, QGIS or GDAL Python bindings
are required. Reuse existing tools. If absent, user-run Debian/Ubuntu commands are
`sudo apt install gdal-bin` or `sudo apt install python3`, only for the selected inputs.
For Conda, the corresponding packages are `libgdal-core` and `python`.
The agent never installs software itself.

Check only the relevant tools with `ogrinfo --version`, `gdalinfo --version` and `python3 --version`.

The skill works on local files and needs no network service or API key. It does not fetch
remote VRT sources or open database connections merely to inventory local files.

## Installation

```bash
npx skills add ignfab/geoskills --skill geodata-intake
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/3-prepare`.

## Example

> Examine the files in `data/monuments_sans_prj/` and `data/mnt_dalles/` without modifying
> them. Write an inventory to `output/inventory.md`: formats, layers, fields, dimensions,
> declared coordinate systems and missing metadata. Do not infer a projection from the
> coordinates alone. Propose the next step without transforming the data.

The inventory starts from metadata, without fetching all features or writing sidecars:

```bash
ogrinfo -ro -so -al -nocount -noextent input.gpkg
```

```bash
gdalinfo --config GDAL_PAM_ENABLED NO -json input.tif > raster-info.json
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Workflow, prerequisites, routing to the next operation and validation. |
| [references/inspection.md](references/inspection.md) | Detailed recipes and edge cases: Shapefile sidecars, CSVs, rasters and VRTs, archives, inspection cost. |

## Tests

- Agent scenarios: [tests/geodata-intake.md](../../../tests/geodata-intake.md), in French
  (2 positive, 1 negative).
- Offline: [test_raster_quality.py](../../../tests/test_raster_quality.py) runs the intake
  recipes, which keep a missing CRS unknown and write no sidecar. No live test.

## Related skills

- [`crs-reprojection-france`](../crs-reprojection-france/README.md) confirms and assigns a
  missing CRS once the producer metadata establishes it.
- [`vector-data-quality`](../vector-data-quality/README.md) audits the geometries that the
  inventory only lists.
- [`gdal-vector-processing`](../gdal-vector-processing/README.md) and
  [`gdal-raster-processing`](../gdal-raster-processing/README.md) carry out the conversion,
  clipping or mosaicking recommended as the next step.
