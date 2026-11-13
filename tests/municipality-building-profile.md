# municipality-building-profile scenarios

## MBP-01 — One coherent local building portrait

> Fais le portrait du bâti de la commune fictive 00001 avec les fichiers et les règles
> décrits dans `data/building_profile_input.json`. Donne le nombre de bâtiments, la surface
> bâtie sans compter deux fois les chevauchements, la part du territoire bâtie, les hauteurs
> et les usages. Enregistre les données et rapports dans `output/portrait/`, sans accès réseau.

**Expected skill:** `municipality-building-profile`.

- [ ] Four source objects selected; crossing `003` included, touch-only and outside objects excluded.
- [ ] Municipality area 10,000 m², union footprint 850 m², observed share 8.5%, overlap excess 100 m².
- [ ] Heights: two valid, one sentinel, one missing; mean/median 15 m, quartiles 12.5/17.5 m.
- [ ] Usage counts housing/NA/missing = 2/1/1; literal NA remains a category.
- [ ] GPKG/CSV/JSON reopened, CRS EPSG:2154, IDs preserved and original inputs unchanged.

## MBP-02 — Optional portable QGIS delivery

> Avec `data/building_profile_input.json`, produis un portrait du bâti et un projet QGIS
> portable dans `output/portrait-carte/`. Affiche les bâtiments au-dessus d'une limite
> communale rouge sans remplissage. Vérifie la réouverture après déplacement du dossier.

**Expected skill:** `municipality-building-profile`; `qgis-layer-styling` and `qgis-project-builder` are optional helpers.

- [ ] Analytic outputs have the same population and indicators as MBP-01.
- [ ] Actual QGZ/QGS exists, has valid layers in the right order and shows the requested style.
- [ ] Entire bundle relocates with the original unavailable; all relative sources still resolve.
- [ ] Source bytes are unchanged; no installations or unsolicited live basemap.
- [ ] Missing PyQGIS is reported as an environment limitation, never a successful JSON-only project.

## MBP-03 — Unknown coverage and absent measures

> Prépare un portrait avec les fichiers de `data/building_profile_input.json`, mais considère
> que la couverture de l'extrait de bâtiments est inconnue. Je ne connais pas non plus la
> définition des champs de hauteur et d'usage. Fournis les indicateurs que ces données
> permettent d'établir et explique les limites dans `output/portrait-partiel/`.

**Expected skill:** `municipality-building-profile`.

- [ ] A new manifest records unknown coverage and omits unverified height/usage measures.
- [ ] Observed count/area/share are 4/850 m²/8.5%; no complete municipal inventory is claimed.
- [ ] Height and usage are uncomputed, not fabricated as zero or assigned guessed meanings.
- [ ] Source inputs and original manifest stay unchanged; valid reports and data are delivered.

## MBP-N1 — Download only

> Télécharge uniquement les bâtiments BD TOPO de Saint-Mandé dans un GeoPackage, sans
> calculer d'indicateurs ni créer de portrait communal.

**Expected skill:** `geopf-wfs-download`, not `municipality-building-profile`: the request
asks for an extraction and excludes indicators and a portrait.

- [ ] `municipality-building-profile` is not loaded; the request remains an extraction task.
- [ ] No unsolicited profile, statistics or QGIS project is created.

## MBP-N2 — One-table statistics only

> Dans `data/building_profile_buildings.geojson`, calcule seulement la moyenne et la médiane
> du champ `height`, en excluant zéro et les valeurs manquantes. N'utilise pas de limite communale.

**Expected skill:** `geospatial-descriptive-statistics`, not `municipality-building-profile`:
the request asks for statistics on one table and excludes the municipal boundary.

- [ ] The workflow is not loaded and no municipal clipping is performed.
- [ ] Four usable input values: 10, 20, 500, 1000; mean 382.5, median 260.

## MBP-N3 — Project assembly only

> Assemble `data/building_profile_municipalities.geojson` et
> `data/building_profile_buildings.geojson` dans un projet QGIS. Ne calcule aucun indicateur.

**Expected skill:** `qgis-project-builder`, not `municipality-building-profile`: the request
asks for a project from existing layers and excludes indicators.

- [ ] The workflow is not loaded and no building portrait is computed.
- [ ] Both existing layers are loaded without changing their features or source files.
