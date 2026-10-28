# vector-data-quality

## VDQ-01 — Audit and repair invalid geometries

> Avec Python, audite une couche qui contient des polygones auto-intersectés, des géométries
> vides et des géométries nulles. Répare les géométries invalides dans un nouveau
> GeoPackage sans modifier le fichier source.

**Expected skill:** `vector-data-quality`

**Expected result:** a report separating null, empty and invalid geometries; invalidity
reasons listed by feature ID; a new output whose geometries are valid; geometry-type
changes after `make_valid()` are reported.

- [ ] checks `isna`, `is_empty`, `is_valid` and `is_valid_reason` separately
- [ ] copies the source before repair and writes to a new file
- [ ] uses `make_valid()` rather than presenting `buffer(0)` as a universal fix
- [ ] inspects Polygon → MultiPolygon / GeometryCollection changes
- [ ] quarantines null, empty and non-polygonal results; a `Polygon EMPTY` is not accepted
- [ ] accounts for every input feature in either the repaired output or the quarantine
- [ ] reopens and validates the output

## VDQ-02 — Detect duplicate geometries safely

> Détecte les doublons géométriques d'une couche, y compris si les sommets sont ordonnés
> différemment, sans considérer plusieurs géométries nulles comme des doublons.

**Expected skill:** `vector-data-quality`

**Expected result:** geometries are normalized before duplicate comparison; null and empty
geometries are excluded from the duplicate mask; business identifiers and attributes are
checked before any deletion.

- [ ] uses `geometry.normalize().duplicated(keep=False)`
- [ ] guards the mask with `~geometry.isna() & ~geometry.is_empty`
- [ ] does not automatically drop every shared geometry

## VDQ-03 — Gaps and overlaps between parcels

> Vérifie que les parcelles de data/coverage_synthetic.geojson ne se chevauchent pas et ne
> laissent pas de trous entre elles. Ne modifie pas le fichier : écris la liste des
> problèmes dans output/problemes_parcelles.csv.

**Expected skill:** `vector-data-quality`

**Expected result:** the agent reports that every parcel is valid on its own but the set
is not a valid coverage. It finds the 1 m² overlap between `P02` and `P03`, the enclosed
16 m² gap between `P07` and `P08`, and the 5 cm gap between `P03` and `P04`. The 0.1 m wide
`P09` is reported as a sliver, not as a gap.

- [ ] checks per-feature validity before the coverage check
- [ ] checks the coverage (`is_valid_coverage`, `invalid_coverage_edges` or
  `gdal vector check-coverage`), not only `is_valid`
- [ ] reports overlap pairs with their identifiers and area, and states the tolerance
- [ ] finds the enclosed gap and the narrow gap, with the `gap_width` used
- [ ] does not repair, dissolve or snap the parcels without an explicit rule
- [ ] leaves the source unchanged and writes the CSV with parcel identifiers

## VDQ-N1 — Negative: ordinary spatial analysis

> Associe chaque adresse à la commune qui la contient avec une jointure spatiale.

**Expected skill:** `geopandas-basics`, not `vector-data-quality`, unless invalid geometries
or data-quality failures are also reported.

## VDQ-N2 — Negative: swapped coordinates

> Les points de data/points_gps.csv tombent dans l'océan Indien au lieu de la France.
> Corrige-les et écris output/points.gpkg.

**Expected skill:** `crs-reprojection-france`, not `vector-data-quality`: the geometries are
valid, but latitude and longitude are swapped.

- [ ] reads the `latitude` and `longitude` columns in the right order
- [ ] does not call `make_valid()` or any other geometry repair
