# terrain-elevation-screening scenarios

## TES-01 — Inclusive altitude screen over a local AOI

> Avec `data/terrain_screening.asc` et `data/terrain_screening_aoi.geojson`, repère les
> zones d’altitude comprise entre 0 et 100 mètres, bornes incluses. Les métadonnées sont
> dans `data/README.md`. Fournis le raster d’altitude, le masque, les polygones et un bilan
> de couverture dans `output/terrain/`, sans réseau ni modification des sources.

**Expected skill:** `terrain-elevation-screening`.

**Checks:**
- [ ] Reads fixture metadata; assigns EPSG:2154 on a copy, preserves synthetic vertical reference.
- [ ] 49 AOI cells, 48 valid elevations; mask has 27 selected, 21 rejected, 1 unknown.
- [ ] Inclusive bounds retain valid zero and 100; nodata is never selected; area 2,700 m².
- [ ] Reopens rasters/polygons, verifies CRS/grid/AOI containment and unchanged inputs.
- [ ] Reports method, source, resolution and coverage; no point-API calls or invented accuracy.

## TES-02 — Preliminary helicopter terrain screen

> Pour préparer le repérage d’une zone d’atterrissage d’hélicoptère, utilise les données
> fictives `data/terrain_screening.asc` et `data/terrain_screening_aoi.geojson` et leurs
> métadonnées dans `data/README.md`. Applique uniquement mes critères d’étude : altitude
> entre 0 et 100 mètres inclus, pente au plus 5 degrés et zone continue d’au moins 500 m².
> Exporte les candidats et indique ce qui reste à vérifier. Ne télécharge rien.

**Expected skill:** `terrain-elevation-screening`.

**Checks:**
- [ ] Uses user-supplied study thresholds without presenting them as aviation limits.
- [ ] Computes slope in metre x/y/z units, degrees, with no edge/nodata interpolation.
- [ ] Mask has 8 selected, 16 rejected, 25 unknown cells; one candidate of 800 m² remains.
- [ ] Distinguishes altitude from above-ground/obstacle height; area from usable footprint.
- [ ] Labels terrain candidates; leaves obstacle, surface, approach and operational assessment to pilot/operator; no landing suitability/clearance claim.

## TES-03 — No qualifying elevations

> Sur `data/terrain_screening.asc` et `data/terrain_screening_aoi.geojson`, avec les
> métadonnées de `data/README.md`, garde les altitudes de 300 à 400 mètres inclus. Fournis
> le résultat et explique la différence entre aucune zone retenue et des données absentes.

**Expected skill:** `terrain-elevation-screening`.

**Checks:**
- [ ] Zero selected, 48 rejected and 1 unknown cell; empty candidate layer with CRS retained.
- [ ] Does not relax bounds, fill nodata, or replace the result with a point sample.
- [ ] Reports valid coverage and empty selection distinctly; retains numeric criteria and artifacts.

## TES-N1 — A few point elevations only

> Donne seulement l’altitude du sol pour les coordonnées de `data/elevation_points.csv`
> avec le service de la Géoplateforme. Je ne veux pas de recherche de zones.

**Expected skill:** `geopf-altimetry`, not `terrain-elevation-screening`.

**Checks:**
- [ ] Discovers the elevation resource and preserves point IDs and missing results.
- [ ] No area screening, DEM download or candidate polygons.

## TES-N2 — Raster clipping alone

> Découpe seulement `data/mnt_dalles/dalle_ouest.asc` selon `data/saint_mande.geojson`.
> Le raster est en Lambert-93, confirmé par `data/README.md`. Je veux un GeoTIFF, sans
> filtre d’altitude ni recherche de zones.

**Expected skill:** `gdal-raster-basics`, not `terrain-elevation-screening`.

**Checks:**
- [ ] Uses confirmed source CRS, reads nodata and validates the clipped raster.
- [ ] No thresholds, slope analysis or candidate-site workflow.
