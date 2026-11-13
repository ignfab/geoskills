# geopf-altimetry

## ALT-01 — A small elevation profile

> Avec la Géoplateforme, produis dans `output/` un profil de terrain de vingt points entre
> les coordonnées longitude 2,337306, latitude 48,849319 et longitude 2,367776, latitude
> 48,852891. Indique la ressource choisie, les unités et les éventuelles valeurs manquantes.

**Expected skill:** `geopf-altimetry`.

**Expected result:** 20 samples along a line of about 2.2 km in central Paris, with
plausible terrain altitudes in metres, from a resource discovered in the API metadata.
`test_live_enrichment.py` runs the same profile request.

- [ ] discovers the resource and its metadata before the calculation
- [ ] uses `elevationLine` with 20 samples, in longitude, latitude order
- [ ] treats `-99999` as missing data, never as an altitude
- [ ] reports the resource, units and vertical reference, or says the reference is unknown
- [ ] does not claim centimetric accuracy or call the values ellipsoidal heights

## ALT-02 — Preserve missing elevations

> Sans appeler de service, joins la réponse `data/elevations_synthetic.json` aux points de
> `data/elevation_points.csv` dans `output/altitudes.csv`. Préserve toutes les lignes et
> leurs identifiants. La ressource est `synthetic-terrain` et son référentiel vertical
> n'est pas connu. Signale les altitudes manquantes et explique les contrôles effectués.

**Expected skill:** `geopf-altimetry`.

**Expected result:** two rows, IDs `001` and `002`; altitude 42 for the first; the second
returned the `-99999` sentinel and has no altitude. `test_enrichment.py` runs the
documented join on these two fixtures.

- [ ] keeps both rows and the string IDs `001` and `002`
- [ ] leaves the second altitude empty and flags it, without writing `-99999` as a height
- [ ] checks that the returned coordinates match the input points, in the same order
- [ ] records the resource `synthetic-terrain` and keeps the vertical reference unknown
- [ ] makes no network call

## ALT-N1 — Negative: local DEM processing

> Explique comment assembler les deux dalles de `data/mnt_dalles/` en un raster local.
> Leur projection source confirmée est EPSG:2154. Aucun appel réseau n'est nécessaire.

**Expected skill:** `gdal-raster-basics`, not `geopf-altimetry`.

- [ ] builds a local mosaic (`gdalbuildvrt` with `-a_srs EPSG:2154`)
- [ ] makes no elevation API request
