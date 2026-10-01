# geoskills

Some experimental [skills](https://cursor.com/fr/docs/context/skills) for working with
spatial data.

## Motivation

- Experiment VibeCoding with spatial data within Cursor
- [LangGraph also supports skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)
  (and skills could provide detailled documentation for MCP in
  [ignfab/demo-geocontext](https://github.com/ignfab/demo-geocontext))

## Skills

| Skill | Description |
| --- | --- |
| [geopf-wfs-download](skills/geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) from the Géoplateforme WFS with `ogr2ogr`. |
| [geopf-geocoding](skills/geopf-geocoding/README.md) | Geocode addresses, POIs and parcels (one by one or from a CSV file) with the Géoplateforme API. |
| [gdal-raster-basics](skills/gdal-raster-basics/README.md) | Clip, reproject, mosaic and convert rasters (DEM, orthophotos) with GDAL, build COGs and compute zonal statistics. |
| [crs-reprojection-france](skills/crs-reprojection-france/README.md) | French CRS (Lambert-93, CC zones, NTF, overseas territories): EPSG codes, reprojection and pitfalls. |

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

`geoskills` est un ensemble expérimental de compétences pour agents de code, destinées à
travailler la donnée géographique :

- téléchargement de couches vecteur (WFS) de la Géoplateforme (IGN) ;
- géocodage d'adresses, de lieux et de parcelles, unitaire ou en masse à partir d'un CSV ;
- traitement de rasters (découpe, reprojection, mosaïque, COG, statistiques zonales) ;
- systèmes de coordonnées français (Lambert-93, coniques conformes, DOM) ;

Installation : `npx skills add ignfab/geoskills`

Le contenu des compétences est rédigé en anglais — les outils couverts (GDAL, PROJ, WFS)
sont internationaux, même si les données le sont moins.

## License

[MIT](LICENSE)
