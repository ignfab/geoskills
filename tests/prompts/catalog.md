# Experimental prompt catalog

Prompts to try against the skills, with the family they exercise. Most target the families
with few or no skills and the chains behind business needs. Runs are recorded in
[runs.md](runs.md); the [README](README.md) explains the workflow and the template.

## XP-01 — Choose an elevation product for slopes

> Je dois calculer des pentes sur la commune de Saint-Mandé. Quel produit altimétrique de
> l'IGN choisir, à quelle résolution, et par quel service le récupérer ? Ne télécharge rien.

- **Family:** `1-discover`
- **Expected skills:** `geopf-service-selection`
- **Watch:** products, coverage and resolutions taken from discovery requests rather than
  memory; a justified choice between products; a hand-off to `geopf-altimetry`,
  `geopf-raster-download` or `geopf-file-download` named but not run; nothing downloaded.
- **Status:** open

## XP-02 — Choose the boundary edition for a statistics year

> J'ai des statistiques INSEE par commune au 1er janvier 2024. Quelles limites communales
> de l'IGN, et quelle édition, dois-je utiliser pour que les codes des communes
> correspondent ? Justifie ce choix et ne télécharge rien.

- **Family:** `1-discover`
- **Expected skills:** `geopf-file-download`
- **Watch:** the edition chosen for its reference date, not because it is the latest; the
  choice justified from the feed, which describes ADMIN EXPRESS COG as the annual edition
  following the INSEE official geographic code at 1 January (on 2026-11-09 the 2024
  edition was the `3-2` release dated 2024-02-22, and later editions existed); no archive
  downloaded. Listing the editions alone is DLF-01.
- **Status:** open

## XP-03 — Light municipality layer for a web map

> Prépare une couche légère des communes du Val-de-Marne pour une carte web : un GeoJSON de
> moins de 500 Ko qui conserve les frontières communes. Indique ce que la simplification a
> modifié et enregistre le résultat dans `output/`.

- **Family:** `5-publish`
- **Expected skills:** `geopf-wfs-download`, then `mapshaper-simplify`
- **Watch:** layer and fields discovered from the WFS; 47 municipalities kept; shared
  borders preserved; vertex, size and area changes reported; a missing Mapshaper reported to
  the user, not installed.
- **Status:** open

## XP-04 — QGIS project over Plan IGN

> Crée un projet QGIS qui affiche `data/saint_mande.geojson` au-dessus du Plan IGN, avec un
> contour rouge et sans remplissage. Enregistre le projet dans `output/`.

- **Family:** `5-publish`
- **Expected skills:** `qgis-project-builder`
- **Watch:** project reload preserves requested symbology; public WMTS metadata discovered,
  local and remote validity distinguished, relative path scope stated, no source edits or
  installations. `qgis-layer-styling` is optional for a separate reusable QML deliverable.
- **Status:** open

## XP-05 — Ten-minute walk from the town hall

> Quelle part de la commune de Saint-Mandé se trouve à moins de 10 minutes à pied de la
> mairie ? Enregistre la zone accessible et le calcul dans `output/`.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-geocoding`, `geopf-routing`, then `geopandas-vector-analysis`
- **Watch:** the town hall geocoded, not guessed; pedestrian profile and time unit taken from
  the service capabilities; areas computed in Lambert-93 against `data/saint_mande.geojson`
  (about 90.6 ha); both areas reported with the share.
- **Status:** open

## XP-06 — Urban plan zone and Natura 2000 for a list of addresses

> Pour chaque adresse de `data/adresses.csv`, indique si elle se trouve dans un site
> Natura 2000 et dans quelle zone du plan local d'urbanisme. Produis un tableau dans
> `output/` qui garde toutes les lignes, y compris celles qui n'ont pas pu être géocodées.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-geocoding`, then `apicarto-query`
- **Watch:** eight rows kept, unmatched and empty ones included; both Natura 2000 networks
  queried; every page of each API Carto response read; municipalities without a digital
  urban plan reported, not guessed.
- **Status:** open

## XP-07 — Municipality portrait

> Fais un portrait de la commune de Saint-Mandé : superficie, altitudes minimale, moyenne et
> maximale, et part du territoire couverte par des espaces naturels protégés. Cite chaque
> source avec sa date.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-wfs-download`, `geopf-altimetry` or `gdal-raster-processing`, then
  `apicarto-query`
- **Watch:** boundary and area taken from ADMIN EXPRESS, not from memory; elevation
  statistics from a named resource and resolution; an empty protected-area result reported
  as zero; source editions cited.
- **Status:** open

## XP-08 — Boundary change between two editions

> Les limites de la commune de Saint-Mandé ont-elles changé entre deux éditions
> d'ADMIN EXPRESS COG ? Compare la plus récente avec celle d'il y a cinq ans et chiffre les
> écarts de surface.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-wfs-download` or `geopf-file-download`, then
  `geopandas-vector-analysis`
- **Watch:** available editions discovered, not assumed; both geometries in Lambert-93
  before the comparison; the symmetric difference area reported; no national archive
  downloaded when a filtered request is enough.
- **Status:** open

## XP-09 — geospatial-descriptive-statistics boundary check

> Résume les hauteurs 0, 10, 20 et une valeur manquante dans un tableau synthétique. Donne moyenne, médiane, quartiles, somme, écart-type et taux de valeurs manquantes dans des rapports JSON, CSV et Markdown sous `output/`.

- **Family:** `4-analyze`
- **Expected skills:** `geospatial-descriptive-statistics`
- **Watch:** Finite counts, explicit quantiles/ddof, strict JSON and unchanged inputs.
- **Status:** open

## XP-10 — qgis-layer-styling boundary check

> Applique un contour rouge sans remplissage à `data/saint_mande.geojson` et enregistre un style QGIS QML réutilisable sous `output/`. Vérifie le rechargement sans modifier la source.

- **Family:** `5-publish`
- **Expected skills:** `qgis-layer-styling`
- **Watch:** Real QML, independent reload and unchanged source; missing QGIS is an environment limitation.
- **Status:** open

## XP-11 — spatial-aggregation boundary check

> Compte les points de `data/aggregation_objects.geojson` par zone de `data/aggregation_zones.geojson`, avec le prédicat d’inclusion stricte. Garde les zones vides, signale les points sans zone et exporte un GeoPackage et un CSV dans `output/`.

- **Family:** `4-analyze`
- **Expected skills:** `spatial-aggregation`
- **Watch:** Boundary exclusion is explicit; counts reconcile and all zone IDs survive output round-trip.
- **Status:** open

## XP-12 — bdtopo-schema-guide boundary check

> Sans accès réseau ni téléchargement, explique pour le modèle BD TOPO 3.5 documenté en juillet 2026 quelle classe et quel champ décrivent la hauteur des bâtiments, ce que signifie zéro, et cite la source.

- **Family:** `1-discover`
- **Expected skills:** `bdtopo-schema-guide`
- **Watch:** Version/revision and source pages explicit; zero sentinel handled without inventing WFS fields.
- **Status:** open

## XP-13 — qgis-project-builder boundary check

> Assemble `data/aggregation_objects.geojson` et `data/aggregation_zones.geojson` dans un projet QGIS portable sous `output/bundle/`, avec les points au-dessus des zones et des chemins relatifs. Vérifie sa réouverture après déplacement du dossier complet.

- **Family:** `5-publish`
- **Expected skills:** `qgis-project-builder`
- **Watch:** Final and relocated projects reopen with expected sources, order and relative-path scope.
- **Status:** open

## XP-14 — Municipal building profile with portable delivery

> Avec les données locales et les conventions de `data/building_profile_input.json`, fais
> un portrait du bâti de la commune fictive 00001. Fournis les indicateurs, les rapports
> et un projet QGIS portable avec les bâtiments au-dessus d’une limite rouge sans
> remplissage dans `output/portrait/`. Vérifie les fichiers et la réouverture après
> déplacement. Ne télécharge rien et ne modifie pas les sources.

- **Family:** `6-workflows`
- **Expected skills:** `municipality-building-profile`
- **Watch:** A common population for counts/height/usage, union footprint rather than summed overlaps, explicit boundary and sentinel policy, real reopened/moved QGIS project when PyQGIS exists, unchanged sources. Specialized styling/project skills are optional.
- **Status:** open

## XP-15 — Terrain candidates for a helicopter study

> Avec `data/terrain_screening.asc`, `data/terrain_screening_aoi.geojson` et les
> métadonnées de `data/README.md`, prépare une présélection de terrain pour une étude
> d’atterrissage d’hélicoptère. Mes critères d’étude sont une altitude de 0 à 100 mètres
> inclus, une pente maximale de 5 degrés et une surface continue d’au moins 500 m².
> Fournis les rasters, les polygones candidats et un bilan des données manquantes et des
> vérifications restantes. Ne télécharge rien et ne modifie pas les sources.

- **Family:** `6-workflows`
- **Expected skills:** `terrain-elevation-screening`
- **Watch:** Synthetic data only, valid zero and nodata preserved, Horn degree slopes without interpolated edges, 8/16/25 selected/rejected/unknown cells and one 800 m² candidate. Reopened outputs, unchanged sources and explicit unresolved operational assessment. Thresholds are study inputs, not aviation recommendations.
- **Status:** open

## XP-16 — Lightweight static map and interactive companion

> Illustre `data/admin_units_synthetic.geojson` avec un titre et une source indiquant
> qu’il s’agit de données fictives. Sans QGIS, fournis un PNG de 1 400 × 1 000 pixels,
> un SVG et un HTML interactif sans fond de carte, avec seulement unit_id et label dans
> les infobulles. Utilise population comme couleur, en habitants fictifs. Vérifie les
> rendus et les interactions, indique les poids réels et les dépendances réseau.

- **Family:** `5-publish`
- **Expected skills:** `map-illustration`
- **Watch:** Actual static and browser previews, three features, continuous 10–30 scale, readable title/units/source, selected tooltips/IDs, measured bytes and two declared Leaflet assets. No QGIS dependency or unsupported offline claim; unchanged sources.
- **Status:** open

## XP-17 — QGIS illustration export

> Avec QGIS déjà installé, produis une illustration PNG de `data/saint_mande.geojson`,
> avec un contour rouge sans remplissage, un titre « Saint-Mandé » et la source IGN.
> Vérifie le rendu visuellement et donne les dimensions et le poids du fichier.
> Ne livre pas de projet QGIS ni de fichier QML et ne modifie pas les données.

- **Family:** `5-publish`
- **Expected skills:** `map-illustration`
- **Watch:** Real PyQGIS render and PNG preview, correct unfilled red boundary, title/source, projected CRS and sensible extent, no source edits or substitute QGZ/QML deliverable.
- **Status:** open

## XP-18 — Parcel and zoning at a place, with Geocontext connected

> Quelle est la parcelle cadastrale et quel est le zonage du PLU au niveau de la mairie de
> Saint-Mandé (Val-de-Marne) ? Indique le document d'urbanisme en vigueur.

- **Family:** `2-access`
- **Expected skills:** `apicarto-query`
- **Watch:** with the Geocontext MCP server connected, the place located with `geocode`
  and the namesake in another department rejected from `city` and `zipcode`; `cadastre`
  and `urbanisme` used first; the document and its dates reported with the information-only
  caveat; no file written. Without Geocontext, the API Carto route as documented and at
  most a mention that the server exists. In both cases no attempt to install, configure or
  start a server.
- **Status:** open

## XP-19 — Complete building download, with Geocontext connected

> Télécharge les bâtiments de la BD TOPO de la commune de Saint-Mandé dans un GeoPackage en
> Lambert-93, dans `output/`, et vérifie que l'export est complet.

- **Family:** `2-access`
- **Expected skills:** `geopf-wfs-download`
- **Watch:** with the Geocontext MCP server connected, the layer and its fields found with
  the type search and description tools (whatever their names in the connected version),
  the municipality identified with `adminexpress`, and the expected count taken from
  Geocontext before the download (1,741 intersecting buildings on 2026-11-13) then
  compared with the export, with the difference between the two filters explained. The
  download itself made with `ogr2ogr`, never with Geocontext. Without Geocontext, discovery
  with the documented commands.
- **Status:** open

## XP-20 — Export the map open in QGIS, with a QGIS MCP server connected

> Exporte en PNG la carte actuellement ouverte dans mon QGIS, sans modifier mon projet, et
> donne les dimensions et le poids de l'image.

- **Family:** `5-publish`
- **Expected skills:** `map-illustration`
- **Watch:** with a QGIS MCP server connected, its tool list read, the map rendering tool
  used on the open project, the project neither saved nor changed (layers, styles,
  extent), and the image reopened and checked for size and content. Without it, a
  question about the project file or the data, then a documented route. In both cases no
  server or QGIS plugin installed, configured or started.
- **Status:** open

## XP-21 — Buildings per municipality inside PostGIS, with a PostGIS MCP server connected

> Dans ma base PostGIS, compte les bâtiments de la table `batiment` par commune de la table
> `commune` et donne aussi leur hauteur moyenne. Garde les communes sans bâtiment et ne
> modifie rien dans la base.

- **Family:** `4-analyze`
- **Expected skills:** `spatial-aggregation`
- **Watch:** with a PostGIS MCP server connected, the schemas, geometry columns, SRIDs and
  row counts read first; the predicate and the policy for buildings on a border stated;
  municipalities without buildings kept; matched plus unmatched buildings reconciled with
  the total and multiple matches reported; `SELECT` statements only, no table created.
  Without it, a request for an export, then the helper on that file; no database
  credentials asked for.
- **Status:** open
