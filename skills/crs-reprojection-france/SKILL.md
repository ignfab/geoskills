---
name: crs-reprojection-france
description: Chooses French coordinate reference systems and transforms vectors, rasters, points and heights with GDAL and PROJ. Use to reprojeter or changer de système de coordonnées, choose an EPSG code for Lambert-93, coniques conformes, Lambert II étendu or overseas territories, convert GPS heights to NGF altitudes, or diagnose a missing or incorrect projection.
---

# French coordinate reference systems

Pick the right CRS for French data and reproject vectors, rasters or single points.

## Prerequisites

GDAL and PROJ command-line tools (`ogr2ogr`, `gdalwarp`, `gdaltransform`, `cs2cs`,
`projinfo`), or pyproj in Python. If a tool is missing, give the user the install command and let them run it; do not
install software yourself.

## Which EPSG code?

| Use | CRS | EPSG |
|-----|-----|------|
| Mainland France and Corsica, legal projection | RGF93 v1 / Lambert-93 | **2154** |
| Large-scale mainland work, conic zones (CC42 in the south to CC50 in the north) | RGF93 v1 / CC42 … CC50 | 3942 … 3950 |
| GPS, web APIs, GeoJSON | WGS 84 (lon/lat) | 4326 |
| Web map tiles (OpenLayers, Leaflet, MapLibre) | WGS 84 / Pseudo-Mercator | 3857 |
| Mainland geographic coordinates | RGF93 v1 (lon/lat) | 4171 |
| Legacy data (before about 2010) | NTF (Paris) / Lambert zone II, "Lambert II étendu" | 27572 |
| Guadeloupe, Martinique | RGAF09 / UTM zone 20N | 5490 |
| French Guiana | RGFG95 / UTM zone 22N | 2972 |
| Réunion | RGR92 / UTM zone 40S | 2975 |
| Mayotte | RGM04 / UTM zone 38S | 4471 |
| Saint-Pierre-et-Miquelon | RGSPM06 / UTM zone 21N | 4467 |

CC zone number = the latitude of the zone centre: CC46 (EPSG:3946) covers 45°N–47°N
(Lyon, Clermont-Ferrand). Check any code with `projinfo EPSG:<code>`.

## Reproject

Vector, with ogr2ogr (use `-s_srs` only if the source has no CRS or a wrong one):

```bash
ogr2ogr -f GPKG -t_srs EPSG:2154 out_l93.gpkg in.shp
```

Raster, with gdalwarp (see the `gdal-raster-basics` skill for resampling and nodata):

```bash
gdalwarp -t_srs EPSG:2154 -r bilinear -co COMPRESS=DEFLATE in.tif out_l93.tif
```

Single points. `gdaltransform` and `ogr2ogr` take **lon lat**, but `cs2cs` follows the
EPSG axis order, which is **lat lon** for EPSG:4326:

```bash
echo "2.3522 48.8566" | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:2154
echo "48.8566 2.3522" | cs2cs EPSG:4326 EPSG:2154          # lat lon
echo "2.3522 48.8566" | cs2cs -r EPSG:4326 EPSG:2154       # lon lat, with -r
```

Python, with pyproj. Always pass `always_xy=True` to get lon/lat order:

```python
from pyproj import Transformer

to_l93 = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
x, y = to_l93.transform(2.3522, 48.8566)   # (652469.02, 6862035.26)
```

## Quick sanity checks

- Coordinate ranges are clues, not proof: Lambert-93 commonly has X about 100,000 to
  1,250,000 and Y about 6,000,000 to 7,150,000. A Y near 2,000,000 may suggest Lambert II
  étendu; small values may be degrees or local projected coordinates.
- Confirm a suspected CRS from the producer's metadata or a known control point before
  assigning it. A misplaced dataset can also have swapped axes or incorrect georeferencing.
- Use `-a_srs` only to correct CRS metadata when the coordinates already belong to that
  confirmed CRS. Use `-s_srs <confirmed_source> -t_srs <target>` to correct the source
  metadata and transform coordinates in one operation.

## Validate the output

- Transform a control point whose coordinates you know and compare. For example, Notre-Dame
  de Paris: 2.3499, 48.8530 (EPSG:4326) gives 652296.97, 6861636.36 (EPSG:2154).
- Check the output extent (`ogrinfo -so`, `gdalinfo`) against the usual ranges of the
  target CRS (see *Quick sanity checks*).
- State the units: metres for a projected CRS, degrees for EPSG:4326 or 4171. Never report
  an area or a distance computed in degrees or in EPSG:3857.

## References

- [references/pitfalls.md](references/pitfalls.md) — axis order, assigning versus
  reprojecting, NTF → RGF93 grids, RGF93 v1/v2b, altitudes (NGF-IGN69, IGN78), Web Mercator
  distortion.
- [references/overseas.md](references/overseas.md) — CRS, geographic and vertical systems for
  each overseas territory.

## Additional resources

- PROJ `cs2cs`: <https://proj.org/apps/cs2cs.html>
- IGN geodetic systems: <https://geodesie.ign.fr/>
- EPSG registry: <https://epsg.org/>
