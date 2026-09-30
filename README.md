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
|-------|-------------|
| [geopf-wfs-download](skills/geopf-wfs-download/README.md) | Download vector layers (BD TOPO, ADMIN EXPRESS, cadastre) from the Géoplateforme WFS with `ogr2ogr`. |

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

## Résumé (FR)

`geoskills` est un ensemble de *skills* expérimentales pour travailler la donnée
géographique avec un agent de code, à commencer par le téléchargement de couches WFS de la
Géoplateforme (IGN) avec `ogr2ogr`.

Installation : `npx skills add ignfab/geoskills`

Le contenu des skills est rédigé en anglais — les outils couverts (GDAL, PROJ, WFS)
sont internationaux, même si les données le sont moins.

## License

[MIT](LICENSE)
