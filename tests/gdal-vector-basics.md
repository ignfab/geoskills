# gdal-vector-basics

## GVB-01 — Legacy Shapefile without `.cpg`

> Convertis `data/communes_sans_cpg/communes.shp` en GeoPackage dans
> `output/communes.gpkg`. Les noms des communes et les remarques doivent s'afficher
> correctement.

**Expected skill:** `gdal-vector-basics`

**Expected result:** a GeoPackage layer of 3 points in EPSG:2154 named `Saint-Mandé`,
`L'Haÿ-les-Roses` and `Cœuvres-et-Valsery`, with `code_insee` `02201` kept as a string. The
remarks keep `–`, `«` and `œ`.

- [ ] inspects the source and notices the empty `SOURCE_ENCODING` or the invalid UTF-8
  warnings
- [ ] reads with `-oo ENCODING=CP1252`, not `ISO-8859-1`, which turns `œ` and `–` into
  control characters
- [ ] checks the converted text, not only the exit status
- [ ] leaves `data/` unchanged: no `.cpg` or other sidecar added to the source

## GVB-02 — Add a layer to a GeoPackage

> Crée `output/projet.gpkg` avec une couche `communes` issue de
> `data/communes_sans_cpg/communes.shp`, puis ajoute les parcelles de
> `data/coverage_synthetic.geojson` dans une couche `parcelles` du même fichier.

**Expected skill:** `gdal-vector-basics`

**Expected result:** one GeoPackage with two layers: `communes` (3 points) and `parcelles`
(9 polygons), both in EPSG:2154.

- [ ] adds the second layer with `-update` (or `gdal vector convert --update`), not with a
  plain `ogr2ogr` that recreates the file
- [ ] lists both layers and their counts after the second command
- [ ] reads the Shapefile with an explicit encoding
- [ ] writes a conformant geometry type, for example with `-nlt PROMOTE_TO_MULTI`

## GVB-03 — Clip with a longitude/latitude box

> Découpe les parcelles de `data/coverage_synthetic.geojson` selon le rectangle compris
> entre les longitudes 2,35975 et 2,35998 et les latitudes 48,82932 et 48,82962. Écris le
> résultat en Lambert-93 dans `output/parcelles_decoupees.gpkg` et indique les surfaces
> avant et après le découpage.

**Expected skill:** `gdal-vector-basics`

**Expected result:** parcels `P01` and `P05` are cut, about 307.4 m² and 11.8 m² (319.2 m²
in total), in EPSG:2154. The sliver `P09` and the other parcels are outside the box.

- [ ] states the CRS of the box (`-spat_srs EPSG:4326` with `-clipsrc spat_extent`, a
  WGS84 clip dataset, or `gdal vector clip --bbox-crs`)
- [ ] does not pass longitudes to a numeric `-clipsrc` box in Lambert-93, which returns no
  feature
- [ ] cuts the geometries instead of keeping whole parcels (1200 m² with `-spat` alone)
- [ ] computes areas in Lambert-93, not in degrees

## GVB-04 — Shapefile export for legacy software

> Exporte `data/communes_points.geojson` en Shapefile dans `output/shapefile/` pour un
> logiciel qui ne lit que ce format. Les accents et le « œ » doivent être conservés ;
> indique la correspondance des noms de champs.

**Expected skill:** `gdal-vector-basics`

**Expected result:** a Shapefile of 3 points in EPSG:4326 with a `.cpg` and a `.prj`.
`Cœuvres-et-Valsery` and the dashes of `remarque` read back unchanged. Field names of 10
characters or fewer are chosen and mapped, or GDAL's truncated names are reported.

- [ ] sets the encoding explicitly (`-lco ENCODING=UTF-8`, or `CP1252` if justified); the
  default ISO-8859-1 turns `œ` and `–` into `?`
- [ ] reports the field mapping; `nom_offi_1` is not left unexplained
- [ ] reopens the Shapefile and checks its count, CRS and text

## GVB-N1 — Negative: Python workflow

> Charge `data/saint_mande.geojson` dans un GeoDataFrame et calcule sa surface en
> hectares.

**Expected skill:** `geopandas-basics`, not `gdal-vector-basics`.

- [ ] reprojects to EPSG:2154 before computing the area (about 90.6 ha)

## GVB-N2 — Negative: Géoplateforme download

> Télécharge les communes du Val-de-Marne depuis la Géoplateforme au format GeoPackage.

**Expected skill:** `geopf-wfs-download`, not `gdal-vector-basics`: the data must first be
discovered and downloaded from the WFS.

- [ ] discovers the ADMIN EXPRESS municipality layer from the WFS capabilities
- [ ] filters on the Val-de-Marne (department `94`) on the server side
