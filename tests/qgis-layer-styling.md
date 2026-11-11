# qgis-layer-styling scenarios

## QLS-01 — Polygon outline

> Applique un contour rouge sans remplissage à `data/saint_mande.geojson` et enregistre un style QGIS QML réutilisable sous `output/`. Vérifie le rechargement sans modifier la source.

Expected: `qgis-layer-styling`; red polygon stroke, no fill, fresh-layer reload; missing PyQGIS reported without installation.

## QLS-02 — Numeric classes

> Crée une couche synthétique avec les hauteurs 0, 10, 20, 30 et une valeur manquante. Crée un style QGIS gradué en trois intervalles égaux, indique les seuils et les valeurs non représentées.

Expected: `qgis-layer-styling`; numeric field, breaks 0/10/20/30, one unrendered null, checked renderer.

## QLS-N1 — Project assembly

> Crée un projet QGIS avec deux couches et une emprise initiale, sans créer de nouveau style.

Expected: Project workflow; no QML generation or qgis-layer-styling load.
