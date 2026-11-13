# spatial-aggregation

## SPA-01 — Complete zone counts

> Compte les points de `data/aggregation_objects.geojson` par zone de `data/aggregation_zones.geojson`, avec le prédicat d’inclusion stricte. Garde les zones vides, signale les points sans zone et exporte un GeoPackage et un CSV dans `output/`.

**Expected skill:** `spatial-aggregation`.

**Expected result:** with `within`, counts 2/1/0 for zones `001`/`002`/`NA`; the
border point `edge` and the point `outside` are unmatched. Both layers are in
EPSG:2154. Reference computed with `aggregate.py --predicate within --policy error`.

- [ ] discovers layer names, the zone identifier field and both CRSs before joining
- [ ] uses the `within` predicate and keeps the empty zone `NA` with a count of 0
- [ ] reports `edge` and `outside` as unmatched; 3 matched + 2 unmatched = 5 input points
- [ ] keeps the zone codes as strings (`001`, not `1`)
- [ ] writes a GeoPackage and a CSV under `output/` and reopens them

## SPA-02 — Explicit boundary duplicates

> Avec les deux fichiers `data/aggregation_objects.geojson` et `data/aggregation_zones.geojson`, calcule par zone la somme et la moyenne de `height`. Compte un point dans toutes les zones qu’il touche et signale les affectations multiples.

**Expected skill:** `spatial-aggregation`.

**Expected result:** with `intersects` and policy `all`, `edge` is assigned to both `001`
and `002`: counts 3/2/0 (5 assignments for 4 matched points), sums 40/30/0, means
13.33 (40/3) and 30, null mean for the empty zone `NA`; the missing height in `002` is
counted as missing, not as 0. Reference computed with `aggregate.py --predicate intersects
--policy all --field height`.

- [ ] chooses `intersects` with an explicit multiple-assignment policy and names `edge`
  as assigned twice
- [ ] gives counts 3/2/0, sums 40/30/0 and means 13.33 and 30
- [ ] leaves the mean of `NA` null instead of 0 and reports the missing height
- [ ] reconciles 5 assignments with 4 matched and 1 unmatched point

## SPA-N1 — One-table distribution

> Calcule seulement la moyenne et les quantiles des hauteurs dans cette couche, sans regroupement spatial.

**Expected skill:** `geospatial-descriptive-statistics`, not `spatial-aggregation`.

- [ ] summarizes a single layer without any zone join
- [ ] does not load `spatial-aggregation`

## SPA-N2 — Raster means

> Calcule la valeur moyenne d’un MNT par polygone, sans couche de points ou de bâtiments.

**Expected skill:** `gdal-raster-basics` or `geopandas-basics`, not `spatial-aggregation`:
averaging a raster per polygon is a zonal statistic, not a vector aggregation.

- [ ] treats the request as raster zonal statistics
- [ ] does not load `spatial-aggregation`
