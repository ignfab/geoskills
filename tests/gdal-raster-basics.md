# gdal-raster-basics

## RAS-01 — Inspect a raster

> Donne-moi les caractéristiques de data/mnt_dalles/dalle_ouest.asc : taille, résolution,
> système de coordonnées, nodata, altitude min et max.

**Expected skill:** `gdal-raster-basics`

**Expected result:** 72 × 195 pixels, 10 m, origin 656700 / 6861300, nodata `-99999`,
min ≈ 40.40 m, max ≈ 59.97 m, **no CRS**.

- [ ] uses `gdalinfo` (with `-stats` for min/max)
- [ ] says that the file has no CRS, and that the coordinates look like Lambert-93

## RAS-02 — Mosaic, clip and write a COG

> Assemble les dalles de data/mnt_dalles/, découpe le MNT sur la commune de Saint-Mandé
> (data/saint_mande.geojson) et produis un COG dans output/mnt_saint_mande.tif. Les
> métadonnées des dalles sont dans data/README.md.

**Expected skill:** `gdal-raster-basics`

**Reference result** with an explicit aligned grid (`-tr 10 10 -tap`) (`gdalinfo -stats output/mnt_saint_mande.tif`):

- EPSG:2154, 10 m pixels, 126 × 175 pixels, origin 656790 / 6861200
- `LAYOUT=COG`, a nodata value set (`-9999` or `-99999`)
- min ≈ 39.30 m, max ≈ 54.08 m, mean ≈ 50.15 m

Keep 10 m resolution. A different explicitly chosen pixel alignment can change dimensions
by a pixel or two and slightly change extrema; assess coverage, clipping and nodata, not
just an exact size. The automated reference recipe checks statistics within 0.05 m and
9046 valid pixels. With GDAL 3.10.3, implicit crop rounding produced 124 × 173 pixels and
9043 valid pixels: three edge pixels were outside that smaller output extent.

Checklist:

- [ ] builds a VRT with `gdalbuildvrt`
- [ ] notices that the tiles have no `.prj`, confirms the CRS from `data/README.md` or
  another authoritative source, then **assigns** EPSG:2154
  (`gdalbuildvrt -a_srs EPSG:2154`). Without it, `gdalwarp` fails with `Cannot compute
  bounding box of cutline. Cannot find source SRS`.
- [ ] clips with `-cutline ... -crop_to_cutline` and sets `-dstnodata`
- [ ] lets GDAL reproject the EPSG:4326 cutline on the fly, instead of reprojecting the DEM
- [ ] writes a COG (`-of COG`) with compression; the `LAYOUT=COG` marker is a quick check,
  not a complete structural validation
- [ ] does not add CRS or statistics sidecars to the source fixtures

## RAS-03 — Aggregate to a coarser grid

> Produis une version à 25 m du MNT des dalles de data/mnt_dalles/ (moyenne des pixels),
> alignée sur une grille de 25 m, dans output/mnt_25m.tif.

**Expected skill:** `gdal-raster-basics`

**Expected result:** 25 m pixels, 58 × 78 pixels, origin 656700 / 6861300 (multiples of 25).

- [ ] uses `-tr 25 25 -tap -r average`
- [ ] does not use the default `near` resampling; the automated check compares a pixel
  against the weighted mean of its source pixels

## RAS-04 — Hillshade

> Crée un ombrage (hillshade) du MNT de data/mnt_dalles/ dans output/ombrage.tif.

**Expected skill:** `gdal-raster-basics`

**Expected result:** a single-band Byte raster, same extent and resolution as the mosaic
(145 × 195 pixels, 10 m).

- [ ] uses `gdaldem hillshade` on a VRT of the tiles
- [ ] assigns EPSG:2154, or at least mentions that the tiles have no CRS

## RAS-05 — Zonal statistics

> Calcule les statistiques zonales (altitude moyenne, min, max) du MNT de data/mnt_dalles/
> sur la commune de Saint-Mandé (data/saint_mande.geojson), en CSV dans output/stats.csv.

**Expected skill:** `gdal-raster-basics`

**Expected result:** one CSV row for Saint-Mandé with mean ≈ 50.15 m, min ≈ 39.30 m,
max ≈ 54.08 m (count 9046 pixels with default centre-based inclusion). Fractional or
all-touched inclusion gives different valid statistics and must be labelled explicitly.

- [ ] uses `gdal raster zonal-stats` (GDAL ≥ 3.12), `rasterstats`, or a masked crop and
  statistics for this single polygon on older GDAL; states the pixel inclusion rule
- [ ] **reprojects the zones to EPSG:2154 first** — `zonal-stats` does not reproject them,
  mismatched CRS silently yields empty statistics (`count = 0`)
- [ ] assigns EPSG:2154 to the tiles, which have no `.prj`
- [ ] does not compute statistics on the raster in EPSG:4326 (reprojecting the DEM instead
  of the zones changes the values)

## RAS-N1 — Negative: download, not processing

> Télécharge l'orthophoto du centre de Toulouse.

**Expected skill:** `geopf-wms-wmts` (see [WMS-01](geopf-wms-wmts.md#wms-01--orthophoto-extract-in-lambert-93)).
`gdal-raster-basics` may be loaded as well for the conversion, but not instead.
