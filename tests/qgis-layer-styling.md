# qgis-layer-styling

## QLS-01 — Polygon outline

> Applique un contour rouge sans remplissage à `data/saint_mande.geojson` et enregistre un style QGIS QML réutilisable sous `output/`. Vérifie le rechargement sans modifier la source.

**Expected skill:** `qgis-layer-styling`.

**Expected result:** a new `.qml` under `output/` holding a single-symbol renderer with a
red (`#ff0000`) polygon stroke and no fill (not a fill made transparent with opacity 0,
which would also hide the stroke). Without PyQGIS, the agent stops and reports it instead
of writing QML from memory. `test_qgis_layer_styling.py` checks the same round trip.

- [ ] discovers the layer, its geometry type and its CRS before styling
- [ ] produces a single-symbol polygon style: red stroke, `no_fill`, stated width and units
- [ ] reloads the QML on a fresh layer and compares the renderer before and after
- [ ] leaves `data/saint_mande.geojson` unchanged and writes no sidecar next to it
- [ ] when PyQGIS is missing, gives the install command and installs nothing

## QLS-02 — Numeric classes

> Crée une couche synthétique avec les hauteurs 0, 10, 20, 30 et une valeur manquante. Crée un style QGIS gradué en trois intervalles égaux, indique les seuils et les valeurs non représentées.

**Expected skill:** `qgis-layer-styling`.

**Expected result:** a graduated renderer on the numeric height field with breaks
0/10/20/30, three ordered ranges and one null feature left unrendered and reported.

- [ ] stores the heights in a numeric field and builds the layer itself (the prompt names
  no file)
- [ ] gives the breaks 0, 10, 20 and 30 and explains which range takes a shared break
- [ ] reports the one missing value as not rendered
- [ ] checks the ordered breaks after reloading the QML

## QLS-N1 — Project assembly

> Crée un projet QGIS avec deux couches et une emprise initiale, sans créer de nouveau style.

**Expected skill:** `qgis-project-builder`, not `qgis-layer-styling`: the request
assembles a project and excludes new styles.

- [ ] does not load `qgis-layer-styling` and writes no `.qml`
- [ ] asks for or discovers the two layers instead of inventing them
