# I/O and CRS

## Reading and writing

GeoPandas ≥ 1.0 defaults to **pyogrio** (GDAL). Supported formats depend on the GDAL
drivers bundled with that engine; inspect them with `pyogrio.list_drivers()`:

```python
import geopandas as gpd

gdf = gpd.read_file("data.gpkg")                     # GPKG (single layer)
gdf = gpd.read_file("data.gpkg", layer="communes")   # GPKG (named layer)
gdf = gpd.read_file("data.shp")                      # Shapefile
gdf = gpd.read_file("data.geojson")                  # GeoJSON

gdf.to_file("out.gpkg")                              # GPKG, recommended default
gdf.to_file("out.gpkg", layer="resultat")            # add a layer to a GPKG
gdf.to_crs(4326).to_file("out.geojson", RFC7946="YES")  # standard GeoJSON
```

Restrict a read to go faster on a big file:

```python
gdf = gpd.read_file("big.gpkg", columns=["code_insee"], bbox=(650000, 6860000, 660000, 6870000))
gdf = gpd.read_file("big.gpkg", where="population > 10000")
gdf = gpd.read_file("big.gpkg", max_features=100)
```

With the pyogrio engine, `bbox` coordinates must be in the source layer CRS.
`max_features` limits the result; do not report a limited read as a complete dataset.

## GeoParquet

Columnar, compressed, fast — good for analytics and intermediate results. Requires
`pyarrow`:

```python
gdf.to_parquet("data.parquet")
gdf = gpd.read_parquet("data.parquet")
```

The CRS survives the round-trip (`gdf.crs` is preserved), unlike with a `.csv` export.

## Reading Géoplateforme WFS directly

Bounded `GetFeature` URL (recommended — explicit and cacheable):

```python
url = ("https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
       "&TYPENAMES=BDTOPO_V3:batiment&OUTPUTFORMAT=application/json"
       "&COUNT=1000&BBOX=43.603,1.443,43.606,1.446,urn:ogc:def:crs:EPSG::4326")
batiments = gpd.read_file(url)
```

**The CRS and axis order are explicit here:** WFS 2.0 with
`urn:ogc:def:crs:EPSG::4326` uses latitude, longitude. Do not infer the order from an empty
result or swap axes blindly. Check the capabilities, CRS notation and the intended area.
The response is capped at 1000 features; if it reaches that limit, use pagination (for
example the GDAL WFS driver) to obtain a complete extract.

Through the GDAL WFS driver (paging handled for you):

```python
gdf = gpd.read_file("WFS:https://data.geopf.fr/wfs/ows",
                    layer="ADMINEXPRESS-COG.LATEST:region", max_features=50)
```

For repeated or very large extractions, download once to GPKG with `ogr2ogr` instead (see
the `geopf-wfs-download` skill) and read the local file.

## Remote files

GeoPandas reads GDAL virtual file systems directly:

```python
gdf = gpd.read_file("/vsicurl/https://example.com/data/communes.gpkg")
gdf = gpd.read_file("/vsizip/archive.zip/communes.shp")
```

## `set_crs` versus `to_crs`

The same distinction as assigning versus reprojecting in GDAL (see the
`crs-reprojection-france` skill):

```python
gdf = gdf.set_crs(2154)    # ASSIGN: declare what the coordinates already are (no change)
gdf = gdf.to_crs(2154)     # REPROJECT: transform the coordinates
```

- For missing or wrong CRS metadata, confirm the source CRS from metadata or a known
  control point before using `set_crs`. Use `allow_override=True` only when replacing a
  declaration known to be wrong; plausible coordinate ranges alone are not sufficient.
- Data must be combined with a layer in another CRS → `to_crs`.
- Check with `gdf.crs`; two layers must match before `sjoin`, `overlay` or `clip`
  (`pts.to_crs(communes.crs)`).
