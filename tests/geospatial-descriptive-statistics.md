# geospatial-descriptive-statistics

## GDS-01 — Finite numeric summaries

> Résume les hauteurs 0, 10, 20 et une valeur manquante dans un tableau synthétique. Donne moyenne, médiane, quartiles, somme, écart-type et taux de valeurs manquantes dans des rapports JSON, CSV et Markdown sous `output/`.

**Expected skill:** `geospatial-descriptive-statistics`.

**Expected result:** 3 valid values and 1 missing (25 %); mean and median 10, sum 30,
sample standard deviation 10 (`ddof=1`), linear quartiles 5 and 15. The prompt names no
file: the agent builds the table. `test_geospatial_descriptive_statistics.py` checks the
same values on the bundled helper.

- [ ] counts the missing value separately and computes statistics on the 3 finite values
- [ ] gives the expected values and states the standard-deviation convention and the
  quartile method
- [ ] writes JSON, CSV and Markdown under `output/`; the JSON reopens with a strict parser
  (no `NaN` or `Infinity`)
- [ ] checks that valid and missing counts add up to the 4 rows
- [ ] installs nothing

## GDS-02 — Categories and identifiers

> Résume les catégories 01001, 01001, 02002 et une valeur manquante sans perdre les zéros initiaux. Enregistre les effectifs et fréquences dans `output/`.

**Expected skill:** `geospatial-descriptive-statistics`.

**Expected result:** `01001` twice (0.5), `02002` once (0.25) and one missing value
(0.25), frequencies computed over all four rows.

- [ ] keeps the codes as strings, with their leading zeros
- [ ] reports the missing value as its own category instead of dropping it
- [ ] gives counts 2/1/1 and frequencies 0.5/0.25/0.25, summing to 4 rows and 1
- [ ] saves the counts and frequencies under `output/`

## GDS-N1 — Raster zonal statistics

> Calcule l’altitude moyenne d’un raster par commune et joins-la aux polygones.

**Expected skill:** `gdal-raster-processing` or `geopandas-vector-analysis`, not
`geospatial-descriptive-statistics`: raster zonal statistics are not a summary of one
table.

- [ ] computes zonal statistics with the zones and the raster in the same CRS
- [ ] does not summarize a single attribute table instead

## GDS-N2 — Cross-layer counts

> Compte les bâtiments par commune à partir de deux couches.

**Expected skill:** `spatial-aggregation`, not `geospatial-descriptive-statistics`:
counting objects of one layer per zone of another is a cross-layer aggregation.

- [ ] matches buildings to municipalities with a spatial join before counting
- [ ] does not present a single-layer summary as the answer
