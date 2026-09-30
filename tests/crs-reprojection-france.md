# crs-reprojection-france

## CRS-01 — GPS points to Lambert-93

> Convertis les points de data/points_gps.csv en Lambert 93. Signale les points hors de
> sa zone d'usage et propose un système adapté pour ceux-là.

**Expected skill:** `crs-reprojection-france`

**Expected result:**

| Point | EPSG:2154 |
|-------|-----------|
| Notre-Dame de Paris | 652296.97, 6861636.36 |
| Capitole de Toulouse | 574357.38, 6279620.75 |
| Préfecture de La Réunion | **not in Lambert-93.** In RGR92 / UTM 40S (EPSG:2975): 338568.32, 7690475.44 |

- [ ] reads the columns by name: the file has `latitude` **before** `longitude`
- [ ] passes lon/lat in the order the tool expects (`gdaltransform` lon lat, `cs2cs` lat lon
  or `-r`, pyproj `always_xy=True`)
- [ ] flags Lambert-93 as unsuitable for the Réunion point (the projected result would
  be about 10179785, 546780) and proposes EPSG:2975 with clearly labelled coordinates
- [ ] mainland reference coordinates agree within 0.1 m; overseas datum assumptions are stated

## CRS-02 — Legacy Lambert II étendu

> J'ai des coordonnées en Lambert II étendu dans data/points_lambert2e.csv. Convertis-les en
> Lambert 93 le plus précisément possible.

**Expected skill:** `crs-reprojection-france`

**Expected result:**

| id | EPSG:27572 | EPSG:2154 with the IGN grid | Without the grid |
|----|------------|-----------------------------|------------------|
| 1 | 600000, 2428000 | 651313.03, 6861349.81 | 651311.67, 6861349.50 |
| 2 | 536000, 1841000 | 582461.10, 6275414.00 | 582460.95, 6275415.72 |

- [ ] uses EPSG:27572 as the source CRS
- [ ] inspects the selected operation and grid availability; setting `PROJ_NETWORK=ON`
  or listing a candidate alone does not prove that a grid was used
- [ ] with a grid, agrees within 0.1 m; otherwise reports a lower-accuracy fallback or
  inability to perform the requested accurate conversion
- [ ] mentions the metre-scale difference without a grid, without claiming centimetric accuracy

## CRS-03 — Shapefile without a .prj

> Le shapefile data/monuments_sans_prj/monuments.shp s'affiche au mauvais endroit dans QGIS.
> Corrige-le et exporte-le en GeoJSON WGS84 dans output/monuments.geojson. Les métadonnées
> du jeu de test sont dans data/README.md.

**Expected skill:** `crs-reprojection-france`

**Expected result:** the coordinates (X ≈ 648 000–652 000, Y ≈ 6 861 000–6 865 000) are
recognised as Lambert-93. Output in EPSG:4326:

| Monument | lon, lat |
|----------|----------|
| Notre-Dame de Paris | 2.3499, 48.8530 |
| Tour Eiffel | 2.2945, 48.8584 |
| Sacre-Coeur | 2.3431, 48.8867 |

- [ ] identifies the missing `.prj`, treats the coordinate ranges as a clue, and confirms
  Lambert-93 with the fixture metadata or a known point (the Eiffel Tower must land at
  2.2945, 48.8584) before assigning it
- [ ] **assigns** EPSG:2154 (`-s_srs EPSG:2154 -t_srs EPSG:4326`, or `-a_srs` first) instead
  of reprojecting from an assumed WGS84
- [ ] explains the difference between assigning and reprojecting

## CRS-04 — GPS height to NGF altitude

> J'ai un point en RGF93 v1 3D (EPSG:4965), latitude 48.8530, longitude 2.3499, hauteur
> ellipsoïdale 100 m, près de Notre-Dame de Paris. Quelle est son altitude NGF ?

**Expected skill:** `crs-reprojection-france`

**Expected result:** about **56.20 m** NGF-IGN69 (EPSG:4965 → EPSG:5698, geoid grid
`fr_ign_RAF18.tif`).

- [ ] uses the stated RGF93 v1 3D source CRS (EPSG:4965)
- [ ] uses a vertical transformation with the IGN geoid grid
- [ ] checks the vertical operation; an unchanged 100 m at this point is not a valid result
- [ ] agrees within 0.1 m when the RAF18 grid is available; otherwise reports the missing
  dependency rather than fabricating an altitude

For a generic GPS height without a datum/height type, the agent should first establish
those assumptions and avoid reporting a survey-grade result.

## CRS-05 — Area of a municipality

> Calcule la superficie de la commune de Saint-Mandé à partir de data/saint_mande.geojson.

**Expected skill:** `crs-reprojection-france`

**Expected result:** about **90.6 ha** (0.906 km²), computed in Lambert-93.

- [ ] reprojects to EPSG:2154 (or uses a geodesic area) before measuring
- [ ] does not measure in EPSG:4326 degrees, nor in EPSG:3857 (209 ha, about 2.3 times too
  large)

## CRS-N1 — Negative: no CRS work

> Trie data/points_gps.csv par nom et écris le résultat dans output/points_tries.csv.

**Expected skill:** not `crs-reprojection-france`.

- [ ] the coordinates are copied unchanged
