# CRS pitfalls with French data

## 1. Axis order (latitude/longitude)

Since PROJ 6 and GDAL 3, EPSG:4326 officially means **latitude first**. Tools differ:

| Tool | Order for EPSG:4326 |
|------|---------------------|
| `ogr2ogr`, `gdalwarp`, `gdaltransform`, `ogrinfo` (command line) | lon, lat (traditional GIS order) |
| GeoJSON (RFC 7946), Géoplateforme geocoding API | lon, lat |
| `cs2cs` | **lat, lon**, or lon, lat with `-r` |
| pyproj `Transformer.from_crs(...)` | **lat, lon**, or lon, lat with `always_xy=True` |
| GDAL Python API (`osr.SpatialReference`) | **lat, lon**, unless `srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)` |
| WFS 2.0 / GML with `urn:ogc:def:crs:EPSG::4326` | lat, lon (GDAL's WFS driver swaps it for you) |
| `CRS:84`, `OGC:CRS84` | always lon, lat |

Symptom: points appear near the Horn of Africa (lat and lon swapped around 2°E / 47°N) or the
reprojection fails with "infinite" coordinates.

GDAL Python, lon/lat order:

```python
from osgeo import osr

src = osr.SpatialReference()
src.ImportFromEPSG(4326)
src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
```

## 2. Assigning a CRS versus reprojecting

| Situation | Command |
|-----------|---------|
| The file has **no** CRS, or a wrong one, but the coordinates are correct | *Assign*: `ogr2ogr -a_srs EPSG:2154 out.gpkg in.shp`, `gdal_translate -a_srs EPSG:2154 in.tif out.tif` |
| The file has a correct CRS and you want another one | *Reproject*: `ogr2ogr -t_srs EPSG:4326 ...`, `gdalwarp -t_srs ...` |
| The file has no CRS and you want another one | Both at once: `ogr2ogr -s_srs EPSG:2154 -t_srs EPSG:4326 ...` |

A Shapefile without a `.prj` has no CRS. Some tools then silently assume WGS84.

Use coordinate ranges to shortlist candidate CRSs, then confirm with source metadata or
a known point; the ranges alone cannot identify a datum or its realisation:

| X range | Y range | Probably |
|---------|---------|----------|
| −5 to 10 | 41 to 51.5 | Degrees, mainland France (EPSG:4326 or 4171) |
| 100,000 to 1,250,000 | 6,000,000 to 7,150,000 | Lambert-93 (EPSG:2154) |
| 1,100,000 to 2,300,000 | 1,100,000 to 9,400,000. The millions digit gives the zone: Y ≈ (NN − 41) × 10⁶ + 200,000 at the zone centre | CC zone EPSG:39NN |
| 0 to 1,200,000 | 1,600,000 to 2,700,000 | NTF extended Lambert II (EPSG:27572) |
| −600,000 to 1,100,000 | 5,000,000 to 6,700,000 | Web Mercator (EPSG:3857) |

## 3. NTF → RGF93 (legacy Lambert I, II, III, IV)

Old IGN data, cadastre and PLU data before about 2010 often use NTF (Paris) / extended Lambert II
(EPSG:27572). The accurate NTF → RGF93 transformation needs an IGN grid:
`fr_ign_gr3df97a.tif`, which PROJ picks first, or `fr_ign_ntf_r93.tif`. EPSG gives about 1 m
accuracy with the grid. Without it, PROJ uses a Helmert transformation that is off by a
further 1–2 m.

```bash
projinfo -s EPSG:27572 -t EPSG:2154 -o PROJ --hide-ballpark   # shows which grids are used
```

If the grid is missing, PROJ silently falls back to a less accurate transformation. Get the
grids in one of these ways:

```bash
projsync --source-id fr_ign                 # download the IGN grids once
export PROJ_NETWORK=ON                      # or fetch them on demand from cdn.proj.org
conda install -c conda-forge proj-data      # or install every grid
```

Check the result on a known point: `600000 2428000` in EPSG:27572 gives about
`651313.03 6861349.81` in EPSG:2154 with the grid, and `651311.67 6861349.50` without it.

## 4. RGF93 v1, v2 and v2b

IGN has published updated realisations of RGF93: v2 replaced v1 in 2010, and v2b replaced
v2 in 2021. EPSG:2154 is
**RGF93 v1** / Lambert-93. The v2b equivalent is EPSG:9794, and the geographic CRS is
EPSG:9782. The differences are a few centimetres, so keep EPSG:2154 unless you do geodetic or
survey-grade work.

## 5. Altitudes

| Area | Vertical system | EPSG |
|------|-----------------|------|
| Mainland France | NGF-IGN69 | 5720 |
| Corsica | NGF-IGN78 | 5721 |
| Lambert-93 + NGF-IGN69, as a compound CRS | | 5698 |
| Lambert-93 + NGF-IGN78, as a compound CRS | | 5699 |

For GPS heights, first check whether the device reports ellipsoidal or geoid-corrected
heights. Ellipsoidal heights differ from NGF altitudes by about 40–55 m in mainland
France (the geoid undulation). The conversion uses an IGN geoid grid. For EPSG:5698, PROJ
picks `fr_ign_RAF18.tif`. Check which grid a transformation needs with
`projinfo -s EPSG:4965 -t EPSG:5698 -o PROJ --hide-ballpark`:

```bash
# lat lon ellipsoidal_height (RGF93 v1 3D)  ->  X Y altitude (Lambert-93 + NGF-IGN69)
echo "48.8566 2.3522 100" | cs2cs EPSG:4965 EPSG:5698
# 652469.02  6862035.26  56.20
```

At this mainland test point, an unchanged height suggests that the vertical transformation
was not applied. Inspect the selected operation and grid availability (see section 3).
The example assumes RGF93 v1 ellipsoidal coordinates (EPSG:4965); generic GPS/WGS84
coordinates require a stated datum/epoch assumption and do not justify centimetric accuracy.

## 6. Web Mercator distortion

EPSG:3857 is only meant for display. Its distances are too large by a factor of 1/cos(lat)
(about ×1.5 in Paris), and its areas by 1/cos²(lat) (about ×2.3). Never compute a length or an area in EPSG:3857: use
Lambert-93 (or the local UTM zone overseas).

```sql
-- PostGIS
SELECT ST_Area(ST_Transform(geom, 2154)) FROM parcelles;
```

## 7. Resolving a CRS with gdalsrsinfo

```bash
gdalsrsinfo -e in.shp            # try to match the .prj to an EPSG code
gdalsrsinfo EPSG:2154 -o proj4   # PROJ string
ogrinfo -so in.gpkg layer | grep -A2 "Layer SRS"
```
