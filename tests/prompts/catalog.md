# Experimental prompt catalog

Prompts to try against the skills, with the family they exercise. Most target the families
with few or no skills and the chains behind business needs. Runs are recorded in
[runs.md](runs.md); the [README](README.md) explains the workflow and the template.

## XP-01 — Choose an elevation product for slopes

> Je dois calculer des pentes sur la commune de Saint-Mandé. Quel produit altimétrique de
> l'IGN choisir, à quelle résolution, et par quel service le récupérer ? Ne télécharge rien.

- **Family:** `1-discover`
- **Expected skills:** `geopf-services`
- **Watch:** products, coverage and resolutions taken from discovery requests rather than
  memory; a justified choice between products; a hand-off to `geopf-altimetry`,
  `geopf-wms-wmts` or `geopf-download-files` named but not run; nothing downloaded.
- **Status:** open

## XP-02 — Choose the boundary edition for a statistics year

> J'ai des statistiques INSEE par commune au 1er janvier 2024. Quelles limites communales
> de l'IGN, et quelle édition, dois-je utiliser pour que les codes des communes
> correspondent ? Justifie ce choix et ne télécharge rien.

- **Family:** `1-discover`
- **Expected skills:** `geopf-download-files`
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
- **Expected skills:** `geopf-geocoding`, `geopf-routing`, then `geopandas-basics`
- **Watch:** the town hall geocoded, not guessed; pedestrian profile and time unit taken from
  the service capabilities; areas computed in Lambert-93 against `data/saint_mande.geojson`
  (about 90.6 ha); both areas reported with the share.
- **Status:** open

## XP-06 — Urban plan zone and Natura 2000 for a list of addresses

> Pour chaque adresse de `data/adresses.csv`, indique si elle se trouve dans un site
> Natura 2000 et dans quelle zone du plan local d'urbanisme. Produis un tableau dans
> `output/` qui garde toutes les lignes, y compris celles qui n'ont pas pu être géocodées.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-geocoding`, then `apicarto`
- **Watch:** eight rows kept, unmatched and empty ones included; both Natura 2000 networks
  queried; every page of each API Carto response read; municipalities without a digital
  urban plan reported, not guessed.
- **Status:** open

## XP-07 — Municipality portrait

> Fais un portrait de la commune de Saint-Mandé : superficie, altitudes minimale, moyenne et
> maximale, et part du territoire couverte par des espaces naturels protégés. Cite chaque
> source avec sa date.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-wfs-download`, `geopf-altimetry` or `gdal-raster-basics`, then
  `apicarto`
- **Watch:** boundary and area taken from ADMIN EXPRESS, not from memory; elevation
  statistics from a named resource and resolution; an empty protected-area result reported
  as zero; source editions cited.
- **Status:** open

## XP-08 — Boundary change between two editions

> Les limites de la commune de Saint-Mandé ont-elles changé entre deux éditions
> d'ADMIN EXPRESS COG ? Compare la plus récente avec celle d'il y a cinq ans et chiffre les
> écarts de surface.

- **Family:** `6-workflows`
- **Expected skills:** `geopf-wfs-download` or `geopf-download-files`, then
  `geopandas-basics`
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
