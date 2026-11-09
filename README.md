# geoskills

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](https://agentskills.io/)

Some experimental [skills](https://cursor.com/fr/docs/context/skills) for working with
spatial data.

This project is in an exploratory phase. The stability of the skills is not yet guaranteed.

## Motivation

- Experiment VibeCoding with spatial data within Cursor
- [LangGraph also supports skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)
  (and skills could provide detailed documentation for MCP in
  [ignfab/demo-geocontext](https://github.com/ignfab/demo-geocontext))

See [docs/landscape.md](docs/landscape.md) for the dated comparison with other geospatial
skill collections and its implementation follow-up. The section below lists the current skills.

## Skills

Skills are grouped into six families, one folder each under [skills/](skills/). Each family
answers one question. A task usually goes through the first five in order; the sixth chains
them to meet a business need.

| Family | Question | Skills |
| --- | --- | --- |
| [1. Discover and select](skills/1-discover/README.md) | Which data should be used for this request? | `geopf-services` |
| [2. Access and extract](skills/2-access/README.md) | How do I retrieve the right subset? | `geopf-download-files`, `geopf-wfs-download`, `geopf-wms-wmts`, `geoserver-cql-filter`, `apicarto`, `geopf-geocoding` |
| [3. Prepare and check](skills/3-prepare/README.md) | Is the data usable and compatible? | `geodata-intake`, `crs-reprojection-france`, `gdal-vector-basics`, `gdal-raster-basics`, `vector-data-quality` |
| [4. Analyze and derive](skills/4-analyze/README.md) | What information should be computed? | `geopandas-basics`, `geopf-altimetry`, `geopf-routing` |
| [5. Represent and publish](skills/5-publish/README.md) | How do I make the result usable? | `mapshaper-simplify` |
| [6. Solve a business need](skills/6-workflows/README.md) | How do I chain the steps to reach an objective? | None yet |

### 1. Discover and select

| Skill | Description |
| --- | --- |
| [geopf-services](skills/1-discover/geopf-services/README.md) | Choose a Géoplateforme API for dataset discovery, maps, vector features, downloads, geocoding and geographic calculations. |

### 2. Access and extract

| Skill | Description |
| --- | --- |
| [geopf-download-files](skills/2-access/geopf-download-files/README.md) | Paginated Atom discovery, edition selection, foreground transfers, safe resume and integrity checks. |
| [geopf-wfs-download](skills/2-access/geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) with `ogr2ogr` and check export counts and source IDs. |
| [geopf-wms-wmts](skills/2-access/geopf-wms-wmts/README.md) | Download raster layers (orthophotos, Plan IGN, elevation) from the Géoplateforme WMTS / WMS-R with GDAL. |
| [geoserver-cql-filter](skills/2-access/geoserver-cql-filter/README.md) | Write GeoServer WFS/WMS ECQL filters, including URL encoding and CRS:84 geometries with EWKT. |
| [apicarto](skills/2-access/apicarto/README.md) | Query API Carto for parcels, urban-planning zones and easements, protected areas and RPG parcels at a point, in an area or by code, with complete pagination. |
| [geopf-geocoding](skills/2-access/geopf-geocoding/README.md) | Geocode addresses, POIs and parcels, and review CSV matches, ambiguity and unmatched rows. |

### 3. Prepare and check

| Skill | Description |
| --- | --- |
| [geodata-intake](skills/3-prepare/geodata-intake/README.md) | Read-only inventory of formats, layers, metadata and missing CRS evidence. |
| [crs-reprojection-france](skills/3-prepare/crs-reprojection-france/README.md) | French CRS (Lambert-93, CC zones, NTF, overseas territories): EPSG codes, reprojection and pitfalls. |
| [gdal-vector-basics](skills/3-prepare/gdal-vector-basics/README.md) | Convert, reproject, filter, clip and merge vector files with `ogr2ogr` and `gdal vector`, including legacy Shapefile encodings and GeoPackage layers. |
| [gdal-raster-basics](skills/3-prepare/gdal-raster-basics/README.md) | Clip, reproject, mosaic and convert rasters with GDAL; check coverage, grids and COG structure, and compute zonal statistics. |
| [vector-data-quality](skills/3-prepare/vector-data-quality/README.md) | Audit and repair invalid, empty or duplicate vector features, and gaps or overlaps between polygons, before analysis or publication. |

### 4. Analyze and derive

| Skill | Description |
| --- | --- |
| [geopandas-basics](skills/4-analyze/geopandas-basics/README.md) | Process vector data in Python with GeoPandas: I/O, reprojection, spatial joins, overlay, buffers, zonal statistics. |
| [geopf-altimetry](skills/4-analyze/geopf-altimetry/README.md) | Discover terrain/surface resources, preserve missing elevations, join CSV rows and sample profiles. |
| [geopf-routing](skills/4-analyze/geopf-routing/README.md) | Discover navigation resources, choose units/direction and export route or isochrone geometry. |

### 5. Represent and publish

| Skill | Description |
| --- | --- |
| [mapshaper-simplify](skills/5-publish/mapshaper-simplify/README.md) | Simplify polygon boundaries with Mapshaper, preserve shared borders and export lighter GeoJSON or TopoJSON. |

### 6. Solve a business need

No skill yet. The [family page](skills/6-workflows/README.md) lists the use cases and the
building blocks available today.

## Installation

Skills are installed with the [Vercel Skills CLI](https://github.com/vercel-labs/skills),
which reads them directly from this repository.

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

## Contributing

New skills go in `skills/<family>/<skill-name>/`, in the family whose question their main
output answers. See [CLAUDE.md](CLAUDE.md) (also exposed as `AGENTS.md` for cross-agent
tooling) for the conventions.

## Validation

See [tests/README.md](tests/README.md) for automated checks, optional live IGN tests and
manual skill-selection scenarios. Report conventions are described in
[docs/output-reports.md](docs/output-reports.md).

## Résumé (FR)

Ce projet est en phase exploratoire. La stabilité des compétences n’est pas encore garantie.

`geoskills` est un ensemble expérimental de compétences pour agents de code, destinées à
travailler la donnée géographique. Elles sont regroupées en six familles, une par question.

**Découvrir et sélectionner** : quelles données utiliser pour cette demande ?

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

- traitement vecteur en Python avec GeoPandas (jointures spatiales, croisements, tampons,
  statistiques zonales) ;
- altitudes ponctuelles et profils altimétriques, avec gestion des valeurs manquantes ;
- itinéraires et zones accessibles selon un temps ou une distance sur le réseau routier.

**Représenter et diffuser** : comment rendre le résultat utilisable ?

- simplification de limites administratives avec Mapshaper, en conservant les frontières communes.

**Résoudre un besoin métier** : comment assembler les étapes pour répondre à un objectif ?

- pas encore de compétence : la page de la famille liste les cas d'usage (diagnostic
  territorial, accessibilité, exposition, suivi d'évolution) et les briques disponibles.

Installation de toutes les compétences : `npx skills add ignfab/geoskills`

Installation d'une seule famille, par exemple « Accéder et extraire » :
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`

Le contenu des compétences est rédigé en anglais — les outils couverts (GDAL, PROJ, WFS)
sont internationaux, même si les données le sont moins.

## License

[MIT](LICENSE)
