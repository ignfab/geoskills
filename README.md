# geoskills

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](https://agentskills.io/)

Agent skills for discovering, retrieving, preparing, analyzing and publishing geospatial
data, with a focus on the IGN Géoplateforme, French coordinate systems and open-source GIS.

The skills are created by [IGN](https://www.ign.fr/), the French national mapping agency
(Institut national de l'information géographique et forestière). The repository aims to
serve as a reference collection of agent skills for geomatics and geospatial data processing.

The repository contains **24 independently installable skills**. It remains experimental:
automated checks and agent pilots are available, but a full comparative evaluation has not
yet established the stability of every skill.

## Scope

Skills give coding agents instructions, local reference material and, where useful,
tested helper scripts. They cover service selection, data extraction, GDAL/PROJ and
GeoPandas processing, BD TOPO semantics, statistics, vector styling and QGIS projects.
Each skill states its prerequisites, limits and output checks. Agents use existing tools,
discover schemas before querying and validate results before reporting success.

Start with the [documentation guide](docs/README.md) to choose between related skills or
find validation evidence. The [landscape study](docs/landscape.md) preserves the dated
comparison with other collections and links to subsequent implementation reviews.

## Skills

Skills are grouped into six families, one folder each under [skills/](skills/). Each family
answers one question. Use the stages needed for the task; the sixth family combines them
into business workflows.

| Family | Question | Skills |
| --- | --- | --- |
| [1. Discover and select](skills/1-discover/README.md) | Which data should be used for this request? | [geopf-services](skills/1-discover/geopf-services/README.md), [bdtopo-schema-guide](skills/1-discover/bdtopo-schema-guide/README.md) |
| [2. Access and extract](skills/2-access/README.md) | How do I retrieve the right subset? | [geopf-download-files](skills/2-access/geopf-download-files/README.md), [geopf-wfs-download](skills/2-access/geopf-wfs-download/README.md), [geopf-wms-wmts](skills/2-access/geopf-wms-wmts/README.md), [geoserver-cql-filter](skills/2-access/geoserver-cql-filter/README.md), [apicarto](skills/2-access/apicarto/README.md), [geopf-geocoding](skills/2-access/geopf-geocoding/README.md) |
| [3. Prepare and check](skills/3-prepare/README.md) | Is the data usable and compatible? | [geodata-intake](skills/3-prepare/geodata-intake/README.md), [crs-reprojection-france](skills/3-prepare/crs-reprojection-france/README.md), [gdal-vector-basics](skills/3-prepare/gdal-vector-basics/README.md), [gdal-raster-basics](skills/3-prepare/gdal-raster-basics/README.md), [vector-data-quality](skills/3-prepare/vector-data-quality/README.md) |
| [4. Analyze and derive](skills/4-analyze/README.md) | What information should be computed? | [geopandas-basics](skills/4-analyze/geopandas-basics/README.md), [geopf-altimetry](skills/4-analyze/geopf-altimetry/README.md), [geopf-routing](skills/4-analyze/geopf-routing/README.md), [geospatial-descriptive-statistics](skills/4-analyze/geospatial-descriptive-statistics/README.md), [spatial-aggregation](skills/4-analyze/spatial-aggregation/README.md) |
| [5. Represent and publish](skills/5-publish/README.md) | How do I make the result usable? | [map-illustration](skills/5-publish/map-illustration/README.md), [mapshaper-simplify](skills/5-publish/mapshaper-simplify/README.md), [qgis-layer-styling](skills/5-publish/qgis-layer-styling/README.md), [qgis-project-builder](skills/5-publish/qgis-project-builder/README.md) |
| [6. Solve a business need](skills/6-workflows/README.md) | How do I chain the steps to reach an objective? | [municipality-building-profile](skills/6-workflows/municipality-building-profile/README.md), [terrain-elevation-screening](skills/6-workflows/terrain-elevation-screening/README.md) |

Each family page describes its skills, lists the skills of other families that also serve
it, and names the gaps.

## Installation

Skills are installed with the [Vercel Skills CLI](https://github.com/vercel-labs/skills),
which reads them directly from this repository.

List available skills before selecting them:

```bash
npx skills add ignfab/geoskills --list
```

Install all skills:

```bash
npx skills add ignfab/geoskills
```

Install a single skill:

```bash
npx skills add ignfab/geoskills --skill geopf-wfs-download
```

Install one family, here the access skills:

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access
```

Family folders only organize this repository: every skill is installed in its own folder,
`<agent>/skills/<skill-name>/`.

Target a specific agent (`claude-code`, `cursor`, `opencode`, ...):

```bash
npx skills add ignfab/geoskills -a claude-code
```

Skills are installed in the current project by default; add `-g` to install them for the
whole user account.

Installing a skill copies its instructions and supporting files. It does not install
GDAL, GeoPandas, QGIS or other GIS software. Check the selected skill's README for runtime
requirements and commands the user can run if a dependency is missing.

## Contributing

New skills go in `skills/<family>/<skill-name>/`, in the family whose question their main
output answers. See [CLAUDE.md](CLAUDE.md) (also exposed as `AGENTS.md` for cross-agent
tooling) for the conventions.

## Validation

See [tests/README.md](tests/README.md) for automated checks, optional live IGN tests and
manual skill-selection scenarios. Exploratory prompts and their runs are traced in
[tests/prompts/](tests/prompts/README.md). Report conventions are described in
[docs/output-reports.md](docs/output-reports.md).

The [2026-11-11 review](tests/review-2026-11-11.md) records five complementary skills,
their merged PRs, functional checks and actual agent pilots. The
[municipal workflow review](tests/review-municipality-building-profile-2026-11-12.md)
records the first business workflow and its portable-QGIS forward pilot. Historical results describe
the tested versions and fixtures; they are not a guarantee of current live-service behavior.

## Résumé (FR)

Ce projet est en phase exploratoire. La stabilité des compétences n’est pas encore garantie.

Les compétences de ce dépôt sont créées par l’[IGN](https://www.ign.fr/) (Institut national
de l’information géographique et forestière). Le dépôt a pour but de servir de référence
pour les compétences de géomatique et de traitement de données géographiques.

`geoskills` est un ensemble expérimental de compétences pour agents de code, destinées à
travailler la donnée géographique. Elles sont regroupées en six familles, une par question.

**Découvrir et sélectionner** : quelles données utiliser pour cette demande ?

- lecture du modèle BD TOPO, de ses classes et attributs selon la version documentée ;
- choix des services de la Géoplateforme selon le besoin : découverte de données, diffusion,
  téléchargement, extraction et calculs.

**Accéder et extraire** : comment récupérer le bon sous-ensemble ?

- téléchargement des archives IGN par territoire et millésime, avec contrôle des transferts ;
- téléchargement de couches vecteur (WFS), avec contrôle des effectifs et des identifiants,
  et raster (WMTS / WMS — orthophotos, Plan IGN, altitude) de la Géoplateforme (IGN) ;
- filtres attributaires et spatiaux GeoServer, avec prise en charge des géométries en CRS:84 ;
- interrogation de l'API Carto en un point, dans une zone ou par code : parcelles
  cadastrales, zonage des plans locaux d'urbanisme et servitudes, espaces naturels protégés
  et parcelles agricoles (RPG), avec récupération de toutes les pages ;
- géocodage d'adresses, de lieux et de parcelles, unitaire ou en masse à partir d'un CSV,
  puis examen des correspondances, des ambiguïtés et des lignes sans résultat.

**Préparer et contrôler** : les données sont-elles exploitables et compatibles ?

- inventaire des fichiers reçus, des couches et des métadonnées manquantes ;
- systèmes de coordonnées français (Lambert-93, coniques conformes, DOM) ;
- conversion, reprojection, filtrage, découpage et fusion de fichiers vecteur en ligne de
  commande, y compris l'encodage des anciens Shapefile et l'ajout de couches à un GeoPackage ;
- traitement de rasters (découpe, reprojection, mosaïque, COG, statistiques zonales), avec
  contrôle de la couverture, des grilles et de la structure des COG ;
- contrôle qualité vectoriel (géométries invalides ou vides, trous et chevauchements entre
  polygones, doublons, schéma et réparation).

**Analyser et dériver** : quelle information calculer ?

- agrégation des objets par territoire, avec contrôle des limites, doublons et totaux ;
- statistiques descriptives des attributs, catégories et valeurs manquantes d’une couche ;
- traitement vecteur en Python avec GeoPandas (jointures spatiales, croisements, tampons,
  statistiques zonales) ;
- altitudes ponctuelles et profils altimétriques, avec gestion des valeurs manquantes ;
- itinéraires et zones accessibles selon un temps ou une distance sur le réseau routier.

**Représenter et diffuser** : comment rendre le résultat utilisable ?

- illustrations cartographiques légères, statiques par défaut et interactives si besoin,
  avec ou sans QGIS, contrôle visuel et mesure du poids des fichiers ;
- projets QGIS portables, avec contrôle des chemins, couches, styles et fonds distants ;
- styles QGIS réutilisables, avec contrôle des symboles, catégories et classes numériques ;
- simplification de limites administratives avec Mapshaper, en conservant les frontières communes.

**Résoudre un besoin métier** : comment assembler les étapes pour répondre à un objectif ?

- présélection de zones selon l’altitude du terrain, la pente et la surface, avec contrôle
  des données manquantes ; le cas hélicoptère prépare une analyse géographique sans valider
  l’aptitude d’un site à l’atterrissage ;
- portrait du bâti d’une commune : nombre d’objets, surface bâtie sans doubles comptes,
  hauteurs et usages documentés, avec livraison QGIS facultative ;
- d’autres cas d’usage (accessibilité, exposition, suivi d’évolution) restent à explorer.

Installation de toutes les compétences : `npx skills add ignfab/geoskills`

Installation d'une seule famille, par exemple « Accéder et extraire » :
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`

Les prompts expérimentaux qui servent à tester et à valider les compétences sont tracés
dans `tests/prompts/` : un catalogue des prompts et un journal de leurs exécutions.
Les tests automatisés et les essais d’agents sont documentés ; la campagne comparative
complète reste à mener. L’installation des compétences n’installe pas les logiciels SIG.

Le contenu des compétences est rédigé en anglais — les outils couverts (GDAL, PROJ, WFS)
sont internationaux, même si les données le sont moins.

## License

[MIT](LICENSE)
