# apicarto-query

**Family:** [2. Access and extract](../README.md).

Query IGN's [API Carto](https://apicarto.ign.fr/api/doc/) for French reference data at a
point, in an area or by code: cadastral parcels and municipalities, urban-planning
documents, zones and easements from the Géoportail de l'Urbanisme, protected natural
areas, RPG agricultural parcels and administrative units. A bundled script fetches every
page of a query and rejects incomplete or erroneous responses.

For bulk national layers, see [geopf-wfs-download](../geopf-wfs-download/README.md) or
[geopf-file-download](../geopf-file-download/README.md); for addresses,
[geopf-geocoding](../geopf-geocoding/README.md).

## Requirements

Python 3's standard library is sufficient for the pagination helper; curl runs the
manual HTTP examples. Reuse existing GDAL for the documented spatial checks and GeoJSON
conversion. Metadata queries do not require a GIS stack, and missing GDAL does not block
the helper's download/count checks; it leaves the spatial validation outstanding.

If missing, the user can install only the tool needed for the selected stage:
`sudo apt install python3`, `sudo apt install curl` or `sudo apt install gdal-bin`
(Debian/Ubuntu).

The user installs missing software; the agent does not. No API key is needed, except for
the wine appellation module.

## Installation

```bash
npx skills add ignfab/geoskills --skill apicarto-query
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Module choice, queries, pagination, validation and report. |
| [references/cadastre.md](references/cadastre.md) | Parcel identifiers, sections, arrondissements, sheets and fields. |
| [references/modules.md](references/modules.md) | Urban planning, protected areas, RPG, administrative units, postcodes, generic WFS search. |
| [scripts/fetch_features.py](scripts/fetch_features.py) | Fetches every page of a query into one GeoJSON file and checks the count. |

## Example

```bash
python3 scripts/fetch_features.py cadastre/parcelle parcelles.geojson --param code_insee=94067
ogrinfo -so -al parcelles.geojson
```
