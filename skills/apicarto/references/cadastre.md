# Cadastre module

Endpoints: `cadastre/commune`, `cadastre/feuille`, `cadastre/division`, `cadastre/parcelle`
and `cadastre/localisant`, described in
<https://apicarto.ign.fr/api/doc/cadastre.yml>. Observations below were made on
2026-10-29 in Saint-Mandé (`94067`), Paris and Ajaccio; parcel counts change with each
cadastral edition.

## Sources

`source_ign=PCI` (the default) queries Parcellaire Express, updated twice a year. `BDP`
queries BD Parcellaire, a historical product that is no longer updated: use it only when
the user asks for it. The `edition` field of `cadastre/feuille` gives the date of the
cadastral edition (`2026-06-01` for Saint-Mandé on that day); report it.

## Identifiers

| Field | Form | Example |
| --- | --- | --- |
| `code_insee` | 5 characters, a string | `94067`, `02201`, `2A004` |
| `code_dep`, `code_com` | Department and municipality parts of the code | `94`, `067` |
| `code_arr` | Arrondissement of Paris, Lyon or Marseille, else `000` | `101` for Paris 1st |
| `com_abs` | Former municipality absorbed by a merger, else `000` | `000` |
| `section` | 2 characters, padded with `0` | `0J`, `AZ` |
| `numero` | 4 digits, padded with `0` | `0182` |
| `idu` | 14 characters: department, municipality or arrondissement, `com_abs`, section, number | `940670000J0182`, `75101000AZ0051` |

- Unpadded values are rejected with HTTP 400 and a JSON message per field, for example
  `Le numéro de section est sur 2 caractères`.
- Corsican codes (`2A004`) work although the OpenAPI pattern is `\d{5}`.
- Paris, Lyon and Marseille: query the municipality code with `code_arr`, the last three
  digits of the arrondissement code. `code_insee=75056&code_arr=101` returned 1482
  parcels; `code_insee=75101` returned none. In `idu`, the arrondissement replaces the
  municipality part.
- A user's reference such as "section J, parcel 182" becomes `section=0J&numero=0182`.
  The `geopf-geocoding` skill can also locate a parcel from its reference; use API Carto
  for the attributes, listings and spatial queries.

## Find parcels

One parcel from its reference:

```bash
curl --show-error --get --max-time 60 https://apicarto.ign.fr/api/cadastre/parcelle \
  --data-urlencode code_insee=94067 --data-urlencode section=0J --data-urlencode numero=0182 \
  --output parcelle.json
```

Every parcel of a municipality: Saint-Mandé had `numberMatched` 1100, more than one page
of 1000. Use the script; with `--page-size 500` it made three requests:

```bash
python3 scripts/fetch_features.py cadastre/parcelle parcelles_94067.geojson \
  --param code_insee=94067 --page-size 500
```

Large municipalities are slow without a section: a whole-municipality query for Paris
(`75056`) or Ajaccio (`2A004`) did not answer within 120 seconds. List the sheets first,
then query section by section:

```bash
curl --show-error --get --max-time 60 https://apicarto.ign.fr/api/cadastre/feuille \
  --data-urlencode code_insee=94067 --output feuilles.json
```

Saint-Mandé had 11 sheets, sections `0A` to `0K`. Parcels around a point or in an area are
selected by intersection with `geom`; a point on a boundary can return both neighbors.

## Fields

`cadastre/parcelle` returns `idu`, `numero`, `feuille`, `section`, `code_dep`, `code_com`,
`com_abs`, `code_arr`, `code_insee`, `nom_com`, `contenance` and `gid`, with a
`MultiPolygon` geometry.

- `contenance` is the area recorded by the cadastre, in m², as an integer. It differs from
  the area computed from the geometry; report which one is used.
- `cadastre/commune` returns at most 500 municipalities per request.
- `cadastre/localisant` returns points for parcels that have no drawn geometry.
- `cadastre/division` returns the divisions of BD Parcellaire.

The cadastre is a tax document: it does not prove ownership or a legal boundary.
