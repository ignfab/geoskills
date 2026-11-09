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

## XP-02 — Find the latest ADMIN EXPRESS edition

> Quelle est la dernière édition d'ADMIN EXPRESS COG disponible pour la France
> métropolitaine, et dans quels formats et projections est-elle proposée ? Ne télécharge
> rien.

- **Family:** `1-discover`
- **Expected skills:** `geopf-download-files`
- **Watch:** the Atom catalog paged until the resource is found; edition, formats and CRSs
  read from the feed; no archive downloaded.
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
- **Expected skills:** none
- **Watch:** no skill covers QGIS projects yet. Record what the agent does without one: a
  WMTS layer discovered or invented, a project file that opens, relative data paths.
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
