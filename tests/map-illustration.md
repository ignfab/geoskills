# map-illustration scenarios

## MAP-01 — Lightweight static illustration without QGIS

> Sans QGIS ni accès réseau, illustre `data/admin_units_synthetic.geojson` pour un rapport.
> Utilise les métadonnées de `data/README.md`. Fournis un PNG de 1 400 × 1 000 pixels et
> un SVG, avec un titre, la source et une échelle de couleur du champ population en
> habitants fictifs. Vise moins de 2 Mo par fichier et indique les tailles réelles.

**Expected skill:** `map-illustration`.

**Checks:**
- [ ] Uses existing GeoPandas/Matplotlib and a justified display CRS, without installing QGIS.
- [ ] Preserves all three synthetic areas; source population range 10–30 is not a real-world claim.
- [ ] Actual PNG/SVG reopened and visually inspected; title, units and source readable.
- [ ] PNG dimensions checked, actual bytes reported, sources unchanged; no unrequested HTML or tiles.

## MAP-02 — QGIS rendering rather than project delivery

> Avec PyQGIS déjà installé, fais une illustration PNG de `data/saint_mande.geojson` :
> contour rouge sans remplissage, titre « Saint-Mandé » et mention de la source IGN.
> Utilise une emprise cohérente et vérifie visuellement le rendu. Je veux seulement
> l’illustration, pas un projet QGIS ni un fichier de style à livrer.

**Expected skill:** `map-illustration`.

**Checks:**
- [ ] Uses a temporary QGIS map/project with verified source and display CRS; rendering completes.
- [ ] PNG shows the requested red unfilled boundary, readable title/source and useful extent.
- [ ] Actual PNG reopened; no QML/QGZ substitute for the requested image.
- [ ] Missing PyQGIS is an environment limitation, not a fake successful render; source unchanged.

## MAP-03 — Interactive companion with selected attributes

> Crée une petite carte HTML interactive de `data/admin_units_synthetic.geojson`, sans
> fond de carte, avec uniquement unit_id et label dans les infobulles. Garde les zéros
> initiaux des identifiants. Vérifie le zoom, les infobulles et la visibilité de la couche,
> puis précise si le fichier fonctionne vraiment sans réseau et donne son poids.

**Expected skill:** `map-illustration`.

**Checks:**
- [ ] GeoJSON coordinates are longitude/latitude; bounds use latitude/longitude; all three features kept.
- [ ] Only selected properties and internal display colour embedded, no population attribute.
- [ ] Actual browser interaction checked or explicitly unperformed; titles/captions readable.
- [ ] Lists Leaflet resources; tiles=None does not become an unsupported offline claim.
- [ ] File size measured, IDs preserved, no server/hosting setup or source edits.

## MAP-04 — Raster preview for a report

> À partir de `data/terrain_screening.asc` et des métadonnées de `data/README.md`, fais
> une illustration légère des altitudes, sans QGIS. Montre les mètres et les données
> absentes séparément, sans changer les valeurs d’origine ni lancer une analyse de zones.

**Expected skill:** `map-illustration`.

**Checks:**
- [ ] Uses confirmed fixture CRS on a copy; synthetic vertical reference stays explicit.
- [ ] Valid zero and nodata remain distinct; terrain range is 0–200 m.
- [ ] Bounded raster read, appropriate continuous scale, source/title/caption and visual check.
- [ ] No terrain-screening analysis, candidate polygons or silent fill of missing data.

## MAP-N1 — Reusable QML only

> Enregistre seulement un style QGIS QML avec un contour rouge sans remplissage pour
> `data/saint_mande.geojson`, sans exporter d’image.

**Expected skill:** `qgis-layer-styling`, not `map-illustration`.

**Checks:**
- [ ] Creates and reloads reusable QML; no map image or HTML substituted.

## MAP-N2 — Editable project only

> Assemble `data/aggregation_objects.geojson` et `data/aggregation_zones.geojson` dans
> un projet QGIS portable, avec des chemins relatifs. Je ne demande aucune illustration.

**Expected skill:** `qgis-project-builder`, not `map-illustration`.

**Checks:**
- [ ] Delivers a real project and verifies portability; no image substitute.

## MAP-N3 — Simplify geometry only

> Allège la géométrie de `data/admin_units_synthetic.geojson` pour le web en préservant
> les frontières partagées. Exporte le GeoJSON simplifié, sans carte ni image.

**Expected skill:** `mapshaper-simplify`, not `map-illustration`.

**Checks:**
- [ ] Uses geometry simplification with topology checks; no illustration workflow.
