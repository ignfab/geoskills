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

## VDQ-N1 — Negative: ordinary spatial analysis

> Associe chaque adresse à la commune qui la contient avec une jointure spatiale.

**Expected skill:** `geopandas-basics`, not `vector-data-quality`, unless invalid geometries
or data-quality failures are also reported.
