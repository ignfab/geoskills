# geoskills

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compatible-blue)](https://agentskills.io/)

Some experimental [skills](https://cursor.com/fr/docs/context/skills) for working with
spatial data.

This project is in an exploratory phase. The stability of the skills is not yet guaranteed.

## Motivation

- Experiment VibeCoding with spatial data within Cursor
- [LangGraph also supports skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)
  (and skills could provide detailled documentation for MCP in
  [ignfab/demo-geocontext](https://github.com/ignfab/demo-geocontext))

## Skills

| Skill | Description |
| --- | --- |
| [geopf-wfs-download](skills/geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) from the Géoplateforme WFS with `ogr2ogr`. |
| [geoserver-cql-filter](skills/geoserver-cql-filter/README.md) | Write GeoServer WFS/WMS ECQL filters, including URL encoding and CRS:84 geometries with EWKT. |
| [geopf-wms-wmts](skills/geopf-wms-wmts/README.md) | Download raster layers (orthophotos, Plan IGN, elevation) from the Géoplateforme WMTS / WMS-R with GDAL. |
| [geopf-geocoding](skills/geopf-geocoding/README.md) | Geocode addresses, POIs and parcels (one by one or from a CSV file) with the Géoplateforme API. |
| [gdal-raster-basics](skills/gdal-raster-basics/README.md) | Clip, reproject, mosaic and convert rasters (DEM, orthophotos) with GDAL, build COGs and compute zonal statistics. |
| [crs-reprojection-france](skills/crs-reprojection-france/README.md) | French CRS (Lambert-93, CC zones, NTF, overseas territories): EPSG codes, reprojection and pitfalls. |
| [geopandas-basics](skills/geopandas-basics/README.md) | Process vector data in Python with GeoPandas: I/O, reprojection, spatial joins, overlay, buffers, zonal statistics. |
| [vector-data-quality](skills/vector-data-quality/README.md) | Audit and repair invalid, empty or duplicate vector features before analysis or publication. |
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
manual skill-selection scenarios.

## Résumé (FR)

Ce projet est en phase exploratoire. La stabilité des compétences n’est pas encore garantie.

`geoskills` est un ensemble expérimental de compétences pour agents de code, destinées à
travailler la donnée géographique :

- téléchargement de couches vecteur (WFS) et raster (WMTS / WMS — orthophotos, Plan IGN,
  altitude) de la Géoplateforme (IGN) ;
- géocodage d'adresses, de lieux et de parcelles, unitaire ou en masse à partir d'un CSV ;
- filtres attributaires et spatiaux GeoServer, avec prise en charge des géométries en CRS:84 ;
- traitement de rasters (découpe, reprojection, mosaïque, COG, statistiques zonales) ;
- systèmes de coordonnées français (Lambert-93, coniques conformes, DOM) ;
- traitement vecteur en Python avec GeoPandas (jointures spatiales, croisements, tampons,
  statistiques zonales) ;
- contrôle qualité vectoriel (géométries invalides ou vides, doublons, schéma et réparation) ;
- simplification de limites administratives avec Mapshaper, en conservant les frontières communes.

Installation : `npx skills add ignfab/geoskills`

Le contenu des compétences est rédigé en anglais — les outils couverts (GDAL, PROJ, WFS)
sont internationaux, même si les données le sont moins.

## License

[MIT](LICENSE)
