# geospatial-descriptive-statistics scenarios

## GDS-01 — Finite numeric summaries

> Résume les hauteurs 0, 10, 20 et une valeur manquante dans un tableau synthétique. Donne moyenne, médiane, quartiles, somme, écart-type et taux de valeurs manquantes dans des rapports JSON, CSV et Markdown sous `output/`.

Expected: `geospatial-descriptive-statistics`; mean/median 10, sum 30, sample std 10, quartiles 5/15, missing 25%; strict JSON.

## GDS-02 — Categories and identifiers

> Résume les catégories 01001, 01001, 02002 et une valeur manquante sans perdre les zéros initiaux. Enregistre les effectifs et fréquences dans `output/`.

Expected: `geospatial-descriptive-statistics`; string IDs, counts 2/1/1 and frequencies .5/.25/.25.

## GDS-N1 — Raster zonal statistics

> Calcule l’altitude moyenne d’un raster par commune et joins-la aux polygones.

Expected: `gdal-raster-basics` or `geopandas-basics`; no descriptive-statistics skill.

## GDS-N2 — Cross-layer counts

> Compte les bâtiments par commune à partir de deux couches.

Expected: Spatial aggregation workflow; no single-layer descriptive summary.
