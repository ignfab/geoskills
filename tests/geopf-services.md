# geopf-services

These are manual skill-selection and reasoning scenarios. They need no data download,
account or local GIS tools; consult official guides when web access is available and
distinguish documentation-based advice from live-verified availability.

## GSV-01 — Overview by deliverable

> Je découvre les services de la Géoplateforme. Quels services choisir pour afficher une
> carte, récupérer des objets vectoriels, télécharger des fichiers, chercher une adresse
> et faire des calculs géographiques ? Donne une vue d'ensemble avec les points d'entrée
> et les limites importantes, sans lancer de téléchargement.

**Expected skill:** `geopf-services`.

- [ ] distinguishes map images, vector features, vector tiles, files and calculations
- [ ] covers WMS-R/V, WMTS, TMS, WFS, downloads and extraction
- [ ] includes dataset discovery via CSW/search and keeps it separate from address lookup
- [ ] includes geocoding, autocomplete, elevation, routing, isochrones and validation
- [ ] provides current official documentation/discovery links and explains authenticated services
- [ ] does not install tools, download datasets or claim live checks that were not performed

## GSV-02 — Images are not analysis features

> Je veux afficher rapidement les bâtiments sur une carte, changer leur couleur dans
> le navigateur, puis calculer leur surface exacte à partir des objets complets.
> Peut-on tout faire avec le WMS vecteur ou les tuiles vectorielles de la Géoplateforme ?
> Compare les services et indique les étapes suivantes sans récupérer de données.

**Expected skill:** `geopf-services`.

- [ ] explains that WMS-V renders images, not editable vector features
- [ ] recommends TMS for client-side styling and distinguishes it from WMTS image tiles
- [ ] rejects clipped/generalized tiles as a complete source for exact feature areas
- [ ] recommends WFS or dataset files for analysis, then a suitable projected CRS
- [ ] points to `geopf-wfs-download` for feature retrieval without inventing a layer name

## GSV-03 — Downloads, extraction and standards validation

> J'hésite entre des archives départementales, le WFS et une extraction sur mesure pour
> obtenir des données vectorielles de la Géoplateforme sur un territoire à cheval sur
> trois départements. Je veux choisir les champs et le format. Je dois aussi contrôler
> la conformité d'une archive d'urbanisme au standard PLU. Je n'ai pas encore de compte :
> compare les solutions, les droits nécessaires et la façon de vérifier les résultats.
> Ne crée aucun compte, ne lance aucune tâche et n'envoie aucun fichier.

**Expected skill:** `geopf-services`.

- [ ] compares existing packages, bounded WFS queries and custom extraction without assuming which is faster
- [ ] describes paginated download discovery rather than constructing edition-specific filenames
- [ ] explains extraction authentication and account-specific accessible data
- [ ] distinguishes standards validation from local geometry repair and identifies its authentication requirement
- [ ] requires completed jobs, inspected files/reports and conformance findings rather than treating a job ID as success
- [ ] does not request secrets, launch login, submit jobs or upload data

## GSV-04 — Search and calculation services

> Pour une application, je dois suggérer des adresses pendant la saisie, retrouver une
> adresse depuis un point, obtenir l'altitude de points et un profil altimétrique,
> calculer un trajet piéton et afficher la zone accessible en quinze minutes.
> Quels services de la Géoplateforme utiliser et quelles métadonnées vérifier ?
> Je souhaite uniquement des recommandations, pas d'appels de calcul.

**Expected skill:** `geopf-services`.

- [ ] distinguishes autocomplete suggestions from reverse geocoding and routes the latter to `geopf-geocoding`
- [ ] selects the elevation API, checking resource coverage, vertical reference and no-data values
- [ ] separates routing from isochrones and rejects a simple circular buffer for network reachability
- [ ] discovers operation-specific resources/profiles and checks CRS, direction and time/distance units
- [ ] provides official discovery/schema links without inventing supported parameters or submitting calculations

## GSV-05 — Find a dataset before selecting a delivery service

> Je ne connais pas le nom exact de la donnée à utiliser pour une étude. Je veux chercher
> les jeux de données de la Géoplateforme, lire leur provenance, leur couverture et leur
> licence, puis trouver leurs liens de téléchargement ou leurs flux. Est-ce que le
> géocodeur convient ? Explique le rôle du catalogue, du CSW et du service de recherche,
> sans inventer de nom de couche ni télécharger de données.

**Expected skill:** `geopf-services`.

- [ ] distinguishes dataset/offer discovery from address geocoding
- [ ] selects catalogue/search for finding offerings and CSW for metadata records
- [ ] gives CSW 2.0.2 capabilities, `GetRecords` pagination and `GetRecordById`
- [ ] follows distribution links and then checks the chosen service's current capabilities
- [ ] does not invent a search API contract or claim a metadata record is a downloaded dataset

## GSV-N1 — Negative: local reprojection

> J'ai déjà un fichier local en Lambert-93 et je veux le reprojeter en WGS84.
> Explique la marche à suivre, sans rechercher ni télécharger de données.

**Expected skill:** `crs-reprojection-france`, not `geopf-services`.

- [ ] treats the task as local CRS work rather than Géoplateforme service selection
- [ ] does not query remote service metadata or recommend an API unnecessarily

## GSV-N2 — Negative: an explicit WFS workflow

> J'ai déjà choisi le WFS de la Géoplateforme pour exporter des bâtiments en GeoPackage.
> Explique comment préparer ogr2ogr et découvrir la couche et ses champs, sans comparer
> les autres services et sans lancer le téléchargement.

**Expected skill:** `geopf-wfs-download`, not `geopf-services`.

- [ ] loads the specialized WFS workflow directly
- [ ] checks tool/driver capabilities and discovers metadata without installing software
