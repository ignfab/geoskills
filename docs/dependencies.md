# Runtime dependencies

Installing a skill copies instructions, references and helper scripts. It does not
install their GIS software. A family is a way to discover related skills, not a software
bundle: use only the prerequisites of the selected operation and its validation steps.
The skill installer itself may require downloads; this guide concerns runtime tools.

## Start with the available environment

1. Identify the input, requested output and steps that will actually run. Reading a
   schema, requesting JSON, processing a DEM and exporting a QGIS project have different
   needs even when they appear in one workflow.
2. Check the existing tools, versions and required drivers/imports in the environment
   that will execute those steps. Reuse a compatible environment across skills; do not
   create one per skill or per family by default.
3. If a required tool is missing, give the user a command for that tool only. Agents
   never install software or run interactive setup. Pip, Conda and system package
   commands are alternatives appropriate to the selected environment, not a sequence.
4. Check optional packages only when their feature is requested. Missing optional QGIS
   does not prevent an analytic report; missing a required geometry checker does leave
   spatial validation incomplete. Report that distinction.

Keep QGIS/PyQGIS in its own compatible Python/Qt environment. Likewise, use matching GDAL
CLI tools, Python bindings and data files when a workflow needs them together. A Python
package with bundled GDAL does not guarantee an `ogr2ogr` executable or its drivers.
Do not bypass real dependencies with `--no-deps` or upgrade a working stack for an unused
feature. Package managers resolve transitive dependencies; the download volume depends
on platform, versions and the local cache, so package counts are not size estimates.

## By family

The family pages list every skill's base requirements and conditional additions.

| Family | Starting point | Add only for the selected operation |
| --- | --- | --- |
| [Discover](../skills/1-discover/README.md#runtime-dependencies) | Bundled documentation; no GIS runtime | Standard-library Python lookup or HTTP client for live metadata |
| [Access](../skills/2-access/README.md#runtime-dependencies) | HTTP client/standard-library helpers for APIs; GDAL CLI for WFS and raster extraction | Matching archive reader, requested format driver and spatial validation tools |
| [Prepare](../skills/3-prepare/README.md#runtime-dependencies) | Existing GDAL/PROJ, or the relevant Python route | Requested drivers, transformation grids, advanced quality checks or Python GDAL utilities |
| [Analyze](../skills/4-analyze/README.md#runtime-dependencies) | HTTP tools for services, Pandas for CSV, GeoPandas for vector analysis | PyArrow for GeoParquet; rasterstats for raster zonal statistics; spatial checks for API geometries |
| [Publish](../skills/5-publish/README.md#runtime-dependencies) | One renderer: Python static, Python HTML or existing QGIS; Mapshaper for simplification | Numeric HTML colours, raster preview or external web assets when selected |
| [Workflows](../skills/6-workflows/README.md#runtime-dependencies) | GeoPandas for the building portrait; GDAL/Python/NumPy for terrain screening | Online acquisition and QGIS delivery only when required |

## Packages that should stay conditional

- **GeoPandas:** Pip's base package covers vector processing; do not request
  `geopandas[all]` for that task. On Conda-forge, use `geopandas-base` plus `pyogrio` and
  `pyproj` for file I/O and reprojection without the plotting extras of `geopandas`.
  Keep required native libraries and check imports in the chosen environment.
  [GeoPandas installation](https://geopandas.org/en/stable/getting_started/install.html),
  [Conda-forge package recipe](https://github.com/conda-forge/geopandas-feedstock/blob/main/recipe/meta.yaml).
- **GDAL:** Conda-forge's `libgdal-core` supplies native CLI tools and core drivers;
  `gdal` adds Python bindings/utilities. Choose `gdal` for recipes using `gdal_calc.py`,
  `gdal_polygonize.py` or `osgeo`; add `libgdal-arrow-parquet` only for a missing requested
  Arrow/Parquet driver. Python's `pyarrow` does not enable that CLI driver. Avoid the
  all-driver `libgdal` metapackage and full containers as a default setup.
  [GDAL package documentation](https://gdal.org/en/stable/download.html#conda).
- **PROJ grids:** discover the operation's missing file, preview with
  `projsync --file "$GRID_FILE" --dry-run`, then fetch that complete filename. Do not
  synchronize all IGN grids or install all `proj-data` for a single transformation.
  [PROJ download options](https://proj.org/en/stable/apps/projsync.html).
- **Illustration:** static vector images use GeoPandas/Matplotlib; uniform HTML uses
  GeoPandas/Folium; numeric HTML colours also use Matplotlib. QGIS project rendering
  reuses QGIS's environment. None of these routes requires all rendering stacks.

## Contributor test environments

[`tests/requirements.txt`](../tests/requirements.txt) supplies the structural validator's
PyYAML dependency. [`tests/requirements-geospatial.txt`](../tests/requirements-geospatial.txt)
is an optional, deliberately broader environment for running tests across several skills,
not the prerequisites for using a skill or installing a family. For a focused local check,
reuse the relevant runtime and run that test module; missing optional tools produce skips.
CI retains its broader environment to exercise all supported routes.

When adding or editing a skill, keep its `SKILL.md` prerequisites self-contained, its
README consistent, and its family's dependency table up to date. Distinguish the base
route, conditional additions, version/driver checks and user-run installation commands.
Only READMEs link to this repository-wide guide: installed skills must work independently.
