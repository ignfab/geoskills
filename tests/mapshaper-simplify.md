# mapshaper-simplify

Use the synthetic EPSG:4326 fixture `data/admin_units_synthetic.geojson`. Its three
features are invented; `unit_id` values are strings with leading zeros. See
[fixture metadata](data/README.md). Automated tests cover commands and invariants; the
scenarios below separately check agent selection and judgment.

## MS-01 — Simplify adjacent administrative polygons

> Allège les limites dans data/admin_units_synthetic.geojson avec Mapshaper pour une
> carte web, en gardant 20 % des sommets supprimables. Conserve les trois entités et leurs
> identifiants, garde les frontières communes et écris dans output/unites.geojson.

**Expected skill:** `mapshaper-simplify`

- [ ] checks tool availability without installing software
- [ ] inspects metadata before choosing layers, fields and CRS
- [ ] simplifies the neighboring polygons together with `keep-shapes`
- [ ] explains that 20% does not specify final file size or feature count
- [ ] preserves string identifiers, including leading zeros, and the small island feature
- [ ] reopens output; checks validity, bounds, feature count and shared borders
- [ ] reports measured vertex/file-size changes and leaves the source unchanged

## MS-02 — Metric tolerance

> Simplifie data/admin_units_synthetic.geojson avec une tolérance de 100 mètres, puis
> exporte le résultat en longitude et latitude dans output/unites-100m.geojson.

**Expected skill:** `mapshaper-simplify`, with `crs-reprojection-france` if needed.

- [ ] confirms the fixture is in mainland France before choosing EPSG:2154
- [ ] uses Douglas-Peucker in a suitable metric CRS, then exports WGS84 GeoJSON
- [ ] does not use `planar` on longitude/latitude as a substitute for reprojection
- [ ] compares geometry and area in the same projected CRS

## MS-03 — Multipart islands

> Pour des communes composées de plusieurs îles, est-ce que l'option keep-shapes garantit
> que toutes les îles et tous les trous seront conservés après simplification ?

**Expected skill:** `mapshaper-simplify`

**Expected result:** explains the largest-original-bounding-box limitation for multipart
features, recommends comparing parts/holes, and does not promise complete preservation.

## MS-N1 — Negative: geometry repair

> Répare les auto-intersections de mes polygones sans réduire le détail des limites.

**Expected skill:** `vector-data-quality`; no simplification or unconditional `-clean`.

## MS-N2 — Negative: raster resampling

> Réduis la résolution de mon modèle numérique de terrain de 1 mètre à 10 mètres.

**Expected skill:** `gdal-raster-basics`, not `mapshaper-simplify`.
