# spatial-aggregation scenarios

## SPA-01 — Complete zone counts

> Compte les points de `data/aggregation_objects.geojson` par zone de `data/aggregation_zones.geojson`, avec le prédicat d’inclusion stricte. Garde les zones vides, signale les points sans zone et exporte un GeoPackage et un CSV dans `output/`.

Expected: `spatial-aggregation`; counts 2/1/0 for 001/002/NA; edge and outside unmatched; string IDs preserved.

## SPA-02 — Explicit boundary duplicates

> Avec les deux fichiers `data/aggregation_objects.geojson` et `data/aggregation_zones.geojson`, calcule par zone la somme et la moyenne de `height`. Compte un point dans toutes les zones qu’il touche et signale les affectations multiples.

Expected: `spatial-aggregation`; intersects/all; edge counted twice, counts 3/2/0, sums 40/30/0, means 40/3 and 30, empty mean null.

## SPA-N1 — One-table distribution

> Calcule seulement la moyenne et les quantiles des hauteurs dans cette couche, sans regroupement spatial.

Expected: `geospatial-descriptive-statistics`; no spatial-aggregation load.

## SPA-N2 — Raster means

> Calcule la valeur moyenne d’un MNT par polygone, sans couche de points ou de bâtiments.

Expected: `gdal-raster-basics` or `geopandas-basics`; no vector aggregation skill.
