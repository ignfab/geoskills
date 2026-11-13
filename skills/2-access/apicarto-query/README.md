# apicarto-query

**Family:** [2. Access and extract](../README.md).

Query IGN's [API Carto](https://apicarto.ign.fr/api/doc/) for French reference data at a
point, in an area or by code: cadastral parcels and municipalities, urban-planning
documents, zones and easements from the Géoportail de l'Urbanisme, protected natural
areas, RPG agricultural parcels and administrative units. Results are GeoJSON in WGS84
longitude/latitude. A bundled script fetches every page of a query and rejects incomplete
or erroneous responses.

## When to use it

- Retrieve every cadastral parcel of a municipality or section, with its identifier and
  official area (`contenance`), to a GeoJSON file.
- Check whether a point lies in a Natura 2000 site, querying both networks, and report
  the site codes and names.
- Find the urban-planning zone at a point, with its document and approval date.
- List the easements (SUP), protected areas (ZNIEFF, nature reserves, national and
  regional parks) or RPG crops within an area.
- Find the municipality, department or region at a point.

## When to use another skill

- Geocode an address: [`geopf-geocoding`](../geopf-geocoding/README.md)
- Download bulk national layers, or the parcels of a whole department or region:
  [`geopf-file-download`](../geopf-file-download/README.md) (a ready-made package) or
  [`geopf-wfs-download`](../geopf-wfs-download/README.md) (a filtered extract)
- Get map images: [`geopf-raster-download`](../geopf-raster-download/README.md)

## What you get

- One GeoJSON `FeatureCollection` per query, in EPSG:4326, with every page requested by
  `_start` (the service's `next` links point to `http://localhost`). An existing file is
  never overwritten.
- A JSON summary from the script: endpoint, parameters, pages, `numberMatched`, features
  written, output path and `status` (`complete` or `count_not_reported`), with a warning
  when nothing matched.
- Raw responses saved by curl for a point query; a 400 or 500 response is kept so that its
  JSON message can be read.

The script exits with status 2 on an error response, a missing or repeated identifier, a
`numberMatched` that changes between pages, an incomplete count or a geometry that is not
in longitude/latitude. By default it refuses a query matching more than 50,000 features
(`--max-features`).

Before reporting, the agent checks that the response is a `FeatureCollection`, not an
error object; that the feature count equals `numberMatched` with unique identifiers and
the expected geometry type; and that `ogrinfo -so -al` shows EPSG:4326 with an extent in
France (overseas data have their own ranges). For zoning it reports the document
(`partition`, `idurba`, `du_type`) and approval date (`datvalid`) with each zone.

The report says that API Carto returns data for information: the approved plan's
regulation and graphic documents remain the reference for urban planning, and the
cadastre does not prove ownership or boundaries. Service errors are reported as such,
never replaced by an answer from memory.

## Requirements

Python 3's standard library is sufficient for the pagination helper; curl runs the
manual HTTP examples. Reuse existing GDAL for the documented spatial checks and GeoJSON
conversion. Metadata queries do not require a GIS stack, and missing GDAL does not block
the helper's download/count checks; it leaves the spatial validation outstanding.

Check only the stage's tools with `python3 --version`, `curl --version` or `ogrinfo --version`.

If missing, the user can install only the tool needed for the selected stage:
`sudo apt install python3`, `sudo apt install curl` or `sudo apt install gdal-bin`
(Debian/Ubuntu).

The user installs missing software; the agent does not. The service is
`https://apicarto.ign.fr/api`. No API key is needed, except for the wine appellation module
(`aoc`): the user provides the key outside the chat, and it is never printed in commands
or logs.

## Installation

```bash
npx skills add ignfab/geoskills --skill apicarto-query
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`.

## Example

> Retrieve every cadastral parcel of Saint-Mandé (INSEE code 94067) with its identifier and
> its official area, and write them to `output/parcelles_saint_mande.geojson`.

```bash
python3 scripts/fetch_features.py cadastre/parcelle parcelles.geojson --param code_insee=94067
ogrinfo -so -al parcelles.geojson
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Module choice, queries, pagination, validation and report. |
| [references/cadastre.md](references/cadastre.md) | Parcel identifiers, sections, arrondissements, sheets and fields. |
| [references/modules.md](references/modules.md) | Urban planning, protected areas, RPG, administrative units, postcodes, generic WFS search. |
| [scripts/fetch_features.py](scripts/fetch_features.py) | Fetches every page of a query into one GeoJSON file and checks the count. |

## Tests

French agent scenarios: [tests/apicarto-query.md](../../../tests/apicarto-query.md) (3 positive + 1
negative). Offline: [test_apicarto.py](../../../tests/test_apicarto.py) (paging script and
documented requests against a loopback server). Live: [test_live_apicarto.py](../../../tests/test_live_apicarto.py).

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) chooses the access route
  and lists API Carto among the services.
- [`geopf-geocoding`](../geopf-geocoding/README.md) locates a parcel from its reference,
  without its official area; this skill adds `contenance` and every parcel of an area.
- [`gdal-vector-processing`](../../3-prepare/gdal-vector-processing/README.md) converts, filters
  or clips the GeoJSON results locally.
