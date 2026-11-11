# qgis-project-builder scenarios

## QPB-01 — Portable local project

> Assemble `data/aggregation_objects.geojson` et `data/aggregation_zones.geojson` dans un projet QGIS portable sous `output/bundle/`, avec les points au-dessus des zones et des chemins relatifs. Vérifie sa réouverture après déplacement du dossier complet.

Expected: `qgis-project-builder`; two valid layers, point layer above zones, relative sources resolve inside moved bundle; originals unchanged.

## QPB-02 — Project over optional basemap

> Crée un projet QGIS avec `data/saint_mande.geojson`, un fond Plan IGN si disponible et une emprise cohérente. Enregistre le QGZ sous `output/` et distingue la validité des données locales de celle du fond distant.

Expected: `qgis-project-builder`; discovered WMTS metadata, explicit local/remote status, no invented identifiers or false tile-rendering claim.

## QPB-N1 — Style only

> Enregistre uniquement un style QML gradué pour cette couche, sans créer de projet QGIS.

Expected: `qgis-layer-styling`; no qgis-project-builder load or QGZ output.
