---
name: crs-reprojection-france
description: Chooses and converts between French coordinate reference systems (Lambert-93 / EPSG:2154, the CC42–CC50 conic zones, RGF93, WGS84, Web Mercator, the old NTF Lambert zones and the overseas UTM systems) with ogr2ogr, gdalwarp, cs2cs, gdaltransform and pyproj, and avoids the usual pitfalls (lat/lon axis order, missing .prj, NTF grids, NGF altitudes). Use when the user wants to reprojeter, changer de projection or de système de coordonnées, convert coordinates to or from Lambert 93, Lambert II étendu, coniques conformes, GPS or WGS84, find the right EPSG code for France or a DOM-TOM, or fix data that lands in the wrong place.
---

# French coordinate reference systems

Pick the right CRS for French data and reproject vectors, rasters or single points.

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

- Lambert-93 coordinates in mainland France: X from about 100,000 to 1,250,000, Y from about
  6,000,000 to 7,150,000. A Y value around 2,000,000 means Lambert II étendu (EPSG:27572).
- Coordinates between −180 and 180 are degrees. If the points end up off the coast of
  Somalia, latitude and longitude are swapped. If they all land near 0°N 0°E (Gulf of
  Guinea), degree values were read as metres.
- Data "in the wrong place" but with plausible values usually has a **missing or wrong
  CRS**. Assign it with `-a_srs` (vector: `ogr2ogr -a_srs`; raster: `gdal_translate -a_srs`)
  instead of reprojecting it.

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
