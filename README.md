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
skill collections and its implementation follow-up. The table below lists the current skills.

## Skills

| Skill | Description |
| --- | --- |
| [geodata-intake](skills/geodata-intake/README.md) | Read-only inventory of formats, layers, metadata and missing CRS evidence. |
| [geopf-download-files](skills/geopf-download-files/README.md) | Paginated Atom discovery, edition selection, foreground transfers, safe resume and integrity checks. |
| [geopf-altimetry](skills/geopf-altimetry/README.md) | Discover terrain/surface resources, preserve missing elevations, join CSV rows and sample profiles. |
| [geopf-routing](skills/geopf-routing/README.md) | Discover navigation resources, choose units/direction and export route or isochrone geometry. |
| [geopf-services](skills/geopf-services/README.md) | Choose a Géoplateforme API for dataset discovery, maps, vector features, downloads, geocoding and geographic calculations. |
| [geopf-wfs-download](skills/geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) with `ogr2ogr` and check export counts and source IDs. |
| [geoserver-cql-filter](skills/geoserver-cql-filter/README.md) | Write GeoServer WFS/WMS ECQL filters, including URL encoding and CRS:84 geometries with EWKT. |
| [geopf-wms-wmts](skills/geopf-wms-wmts/README.md) | Download raster layers (orthophotos, Plan IGN, elevation) from the Géoplateforme WMTS / WMS-R with GDAL. |
| [geopf-geocoding](skills/geopf-geocoding/README.md) | Geocode addresses, POIs and parcels, and review CSV matches, ambiguity and unmatched rows. |
| [gdal-raster-basics](skills/gdal-raster-basics/README.md) | Clip, reproject, mosaic and convert rasters with GDAL; check coverage, grids and COG structure, and compute zonal statistics. |
| [crs-reprojection-france](skills/crs-reprojection-france/README.md) | French CRS (Lambert-93, CC zones, NTF, overseas territories): EPSG codes, reprojection and pitfalls. |
| [geopandas-basics](skills/geopandas-basics/README.md) | Process vector data in Python with GeoPandas: I/O, reprojection, spatial joins, overlay, buffers, zonal statistics. |
| [vector-data-quality](skills/vector-data-quality/README.md) | Audit and repair invalid, empty or duplicate vector features, and gaps or overlaps between polygons, before analysis or publication. |
| [mapshaper-simplify](skills/mapshaper-simplify/README.md) | Simplify polygon boundaries with Mapshaper, preserve shared borders and export lighter GeoJSON or TopoJSON. |

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

Target a specific agent (`claude-code`, `cursor`, `opencode`, ...):

```bash
npx skills add ignfab/geoskills -a claude-code
```

Skills are installed in the current project by default; add `-g` to install them for the
whole user account.

## Contributing

New skills go in `skills/<skill-name>/`. See [CLAUDE.md](CLAUDE.md) (also exposed as
`AGENTS.md` for cross-agent tooling) for the conventions.

## Validation

See [tests/README.md](tests/README.md) for automated checks, optional live IGN tests and
manual skill-selection scenarios. Report conventions are described in
[docs/output-reports.md](docs/output-reports.md).

## Résumé (FR)

Ce projet est en phase exploratoire. La stabilité des compétences n’est pas encore garantie.

`geoskills` est un ensemble expérimental de compétences pour agents de code, destinées à
travailler la donnée géographique :

- inventaire des fichiers reçus, des couches et des métadonnées manquantes ;
- téléchargement des archives IGN par territoire et millésime, avec contrôle des transferts ;
- altitudes ponctuelles et profils altimétriques, avec gestion des valeurs manquantes ;
- itinéraires et zones accessibles selon un temps ou une distance sur le réseau routier ;
- choix des services de la Géoplateforme selon le besoin : découverte de données, diffusion,
  téléchargement, extraction et calculs ;
- téléchargement de couches vecteur (WFS), avec contrôle des effectifs et des identifiants,
  et raster (WMTS / WMS — orthophotos, Plan IGN, altitude) de la Géoplateforme (IGN) ;
- géocodage d'adresses, de lieux et de parcelles, unitaire ou en masse à partir d'un CSV,
  puis examen des correspondances, des ambiguïtés et des lignes sans résultat ;
- filtres attributaires et spatiaux GeoServer, avec prise en charge des géométries en CRS:84 ;
- traitement de rasters (découpe, reprojection, mosaïque, COG, statistiques zonales), avec
  contrôle de la couverture, des grilles et de la structure des COG ;
- systèmes de coordonnées français (Lambert-93, coniques conformes, DOM) ;
- traitement vecteur en Python avec GeoPandas (jointures spatiales, croisements, tampons,
  statistiques zonales) ;
- contrôle qualité vectoriel (géométries invalides ou vides, trous et chevauchements entre
  polygones, doublons, schéma et réparation) ;
- simplification de limites administratives avec Mapshaper, en conservant les frontières communes.

Installation : `npx skills add ignfab/geoskills`

Le contenu des compétences est rédigé en anglais — les outils couverts (GDAL, PROJ, WFS)
sont internationaux, même si les données le sont moins.

## License

[MIT](LICENSE)
