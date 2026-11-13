# qgis-project-builder

## QPB-01 — Portable local project

> Assemble `data/aggregation_objects.geojson` et `data/aggregation_zones.geojson` dans un projet QGIS portable sous `output/bundle/`, avec les points au-dessus des zones et des chemins relatifs. Vérifie sa réouverture après déplacement du dossier complet.

**Expected skill:** `qgis-project-builder`.

**Expected result:** a `.qgz` (or `.qgs`) under `output/bundle/` with two valid layers in
EPSG:2154: the 5 points above the 3 zones. Copies of both GeoJSON files sit inside the
bundle and the project stores relative paths to them. The automatic extent covers every
feature, about x 0 to 20 and y 0 to 4 in metres plus a margin: the points are aligned on
y = 1 and `outside` lies at x = 20, beyond the zones. After the whole bundle is moved, both
layers reopen from the moved copies. Without PyQGIS, the agent stops and reports it
instead of writing project XML from memory. `test_qgis_project_builder.py` checks
relocation and the extent of aligned points on its own synthetic layers.

- [ ] discovers the geometry types, feature counts and declared CRS of both files first
- [ ] copies the inputs into `output/bundle/` and leaves `data/` unchanged, with no sidecar
- [ ] orders the layers points first (top), zones second, and reopens the project to check it
- [ ] the extent includes the `outside` point at x = 20
- [ ] moves the whole bundle, makes the original location unavailable, and checks that the
  reopened layers resolve inside the moved directory
- [ ] when PyQGIS is missing, gives the install command and installs nothing

## QPB-02 — Project over optional basemap

> Crée un projet QGIS avec `data/saint_mande.geojson`, un fond Plan IGN si disponible et une emprise cohérente. Enregistre le QGZ sous `output/` et distingue la validité des données locales de celle du fond distant.

**Expected skill:** `qgis-project-builder`.

**Expected result:** a `.qgz` under `output/` with the Saint-Mandé boundary above an
optional Plan IGN WMTS layer, and an extent centred on the municipality, not on the
basemap coverage. The WMTS layer, style, format and tile matrix set come from the
capabilities read during the run. The report keeps two statuses apart: the local layer
reopened, and the basemap was valid, rendered, or omitted with a warning.

- [ ] reads the WMTS capabilities and takes the Plan IGN identifier, style, format and
  tile matrix set from them, not from memory
- [ ] places the boundary above the basemap and sets an extent on Saint-Mandé
- [ ] reopens the saved project and checks the local layer
- [ ] reports the local result and the remote basemap separately; a valid provider is not
  presented as proof that tiles render
- [ ] if the service fails, keeps the local project and says the basemap was omitted
- [ ] adds no credential or API key to the project

## QPB-N1 — Style only

> Enregistre uniquement un style QML gradué pour cette couche, sans créer de projet QGIS.

**Expected skill:** `qgis-layer-styling`, not `qgis-project-builder`: the request asks for
a style file and excludes a project.

- [ ] does not load `qgis-project-builder` and writes no `.qgz` or `.qgs`
- [ ] asks which layer and numeric field to style, since the prompt names neither
