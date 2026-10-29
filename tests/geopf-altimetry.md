# geopf-altimetry scenarios

## ALT-01 — A small elevation profile

> Avec la Géoplateforme, produis dans `output/` un profil de terrain de vingt points entre
> les coordonnées longitude 2,337306, latitude 48,849319 et longitude 2,367776, latitude
> 48,852891. Indique la ressource choisie, les unités et les éventuelles valeurs manquantes.

Expected: discover resource and detail metadata, `elevationLine`, 20 returned samples,
lon/lat order, sentinel handling and no claim of centimetric accuracy/ellipsoidal heights.

## ALT-02 — Preserve missing elevations

> Sans appeler de service, joins la réponse `data/elevations_synthetic.json` aux points de
> `data/elevation_points.csv` dans `output/altitudes.csv`. Préserve toutes les lignes et
> leurs identifiants. La ressource est `synthetic-terrain` et son référentiel vertical
> n'est pas connu. Signale les altitudes manquantes et explique les contrôles effectués.

Expected: two rows, IDs `001` and `002`, altitude 42 for the first and missing for the
second (`-99999`); unknown vertical reference retained, returned coordinates checked.

## ALT-N1 — Local DEM processing

> Explique comment assembler les deux dalles de `data/mnt_dalles/` en un raster local.
> Leur projection source confirmée est EPSG:2154. Aucun appel réseau n'est nécessaire.

Expected: `gdal-raster-basics`, no point-elevation API requests or `geopf-altimetry` load.
