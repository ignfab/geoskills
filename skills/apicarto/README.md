# apicarto

Query IGN's [API Carto](https://apicarto.ign.fr/api/doc/) for French reference data at a
point, in an area or by code: cadastral parcels and municipalities, urban-planning
documents, zones and easements from the Géoportail de l'Urbanisme, protected natural
areas, RPG agricultural parcels and administrative units. A bundled script fetches every
page of a query and rejects incomplete or erroneous responses.

For bulk national layers, see [geopf-wfs-download](../geopf-wfs-download/README.md) or
[geopf-download-files](../geopf-download-files/README.md); for addresses,
[geopf-geocoding](../geopf-geocoding/README.md).

## Requirements

curl and Python 3 (standard library only); GDAL to inspect and convert the GeoJSON
results. For Debian/Ubuntu, a user-run installation command is:

```bash
sudo apt install curl python3 gdal-bin
```

The user installs missing software; the agent does not. No API key is needed, except for
the wine appellation module.

## Installation

```bash
npx skills add ignfab/geoskills --skill apicarto
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
