# geodata-intake

## INT-01 — Inventory an unfamiliar delivery

> Examine les fichiers `data/monuments_sans_prj/` et `data/mnt_dalles/` sans les modifier.
> Fais un inventaire dans `output/inventaire.md` : formats, couches, champs, dimensions,
> systèmes de coordonnées déclarés et métadonnées manquantes. Ne déduis pas une projection
> à partir des seules coordonnées. Propose la prochaine étape sans transformer les données.

**Expected skill:** `geodata-intake`.

**Expected result:** one logical Shapefile (3 points, no `.prj`) and two ESRI ASCII raster
tiles (72 × 195 pixels for `dalle_ouest.asc`, 10 m, nodata `-99999`, no `.prj`). The files
declare no CRS, and the report keeps that absence explicit.

- [ ] counts the Shapefile once, not its `.shp`, `.shx` and `.dbf` as three datasets
- [ ] reports the missing CRS of both deliveries instead of assigning or guessing one
- [ ] separates what the files declare from producer metadata (`data/README.md`) if it reads it
- [ ] creates no `.prj`, `.aux.xml` or statistics sidecar in `data/`
- [ ] proposes the next step (confirm the CRS, then assign it) without transforming the data

## INT-02 — Inspect a spatial CSV

> Examine `data/points_gps.csv` et explique dans `output/diagnostic.md` comment préparer
> ces données pour une analyse géographique. Vérifie les noms des colonnes et les ordres
> de grandeur, sans reprojeter ni réécrire le fichier.

**Expected skill:** `geodata-intake`.

**Expected result:** three points named by the `nom` column, with `latitude` **before**
`longitude`; two are in mainland France and one is in Réunion.

- [ ] reads the coordinate columns by name and notices that latitude comes first
- [ ] checks the value ranges and flags the Réunion point (latitude about −20.9)
- [ ] does not label every point as mainland Lambert-93 material
- [ ] leaves `data/points_gps.csv` unchanged and writes no reprojected copy

## INT-N1 — Negative: explicit conversion

> Convertis `data/saint_mande.geojson` en `output/commune.gpkg`, en conservant son système
> de coordonnées et ses attributs.

**Expected skill:** `gdal-vector-basics` (or `geopandas-basics`), not `geodata-intake`: the
user asks for one direct conversion, not an inventory of a delivery.

- [ ] converts directly, keeping EPSG:4326 and the attributes
- [ ] does not write a delivery inventory report
