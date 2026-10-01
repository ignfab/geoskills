# geopf-wfs-download

## WFS-01 — Complete bounded building extract

> Télécharge tous les bâtiments BD TOPO intersectant la boîte 1.443, 43.603, 1.446, 43.606
> (longitude/latitude WGS84), dans output/batiments.gpkg.

**Expected skill:** `geopf-wfs-download`.

- [ ] uses the advertised `BDTOPO_V3:batiment` layer and confirms its schema/CRS
- [ ] uses `-spat ... -spat_srs EPSG:4326` or an equivalent server-side spatial filter
- [ ] does not use `-limit` for this request for all buildings in the box
- [ ] checks feature count, geometry and CRS; reports a failed page as incomplete
- [ ] explains that intersecting features retain their whole geometry unless clipping was requested

## WFS-02 — Small sample in standard GeoJSON

> Donne-moi un échantillon de 5 bâtiments BD TOPO autour du Capitole de Toulouse,
> en GeoJSON dans output/echantillon.geojson.

**Expected result:** 1–5 polygon features in WGS84 longitude/latitude, near Toulouse.

- [ ] uses a small bounding box and `-limit 5`; labels the output as a sample
- [ ] produces RFC 7946 GeoJSON, including reprojection if needed
- [ ] does not download the national layer to sample it locally

The automated live test also disables paging and requests a page of five features to
bound transfer. A sample does not establish the count of the complete layer.

## WFS-03 — Add a distinct GeoPackage layer

> Ajoute la couche des régions ADMIN EXPRESS à output/batiments.gpkg, sous le nom regions.

Run after WFS-01. Verify that the existing buildings remain intact and a `regions` layer
is created. Use `-update -nln regions`; reserve `-append` for adding features to an
existing compatible layer. Resolve the actual ADMIN EXPRESS layer name from capabilities.

## WFS-N1 — Negative: raster imagery

> Télécharge l'orthophoto du Capitole de Toulouse.

**Expected skill:** `geopf-wms-wmts`; do not use the WFS for imagery.
