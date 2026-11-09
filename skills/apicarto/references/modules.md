# Other modules

Each module's OpenAPI file at `https://apicarto.ign.fr/api/doc/<module>.yml` lists its
endpoints and parameters. Observations below were made on 2026-10-29.

## Urban planning (`gpu`)

Data come from the Géoportail de l'Urbanisme. Every endpoint takes `geom` or `partition`;
`partition` identifies a document as `DU_<INSEE or SIREN>` or `PSMV_<…>`.

1. `gpu/municipality` tells whether the municipality has its own plan. `is_rnu: true`
   means that the national rules (RNU) apply: no zone is expected.
2. `gpu/document` returns the document covering the geometry: `partition`, `du_type`
   (`PLU`, `PLUi`, `CC`, `POS`, `PSMV`), `grid_title` and `name`.
3. `gpu/zone-urba` returns the zones (`gpu/secteur-cc` for a CC map):
   - `libelle` is the zone code of the document and `libelong` its full name;
   - `typezone` is the national type: `U` (urban), `AUc` or `AUs` (to be urbanized), `A`
     (agricultural) or `N` (natural);
   - `idurba` identifies the document version, `datvalid` its approval date (YYYYMMDD) and
     `nomfic` the regulation file.
4. `gpu/prescription-*` and `gpu/info-*` return the prescriptions and information of the
   plan (surface, line and point variants).
5. `gpu/assiette-sup-*`, `gpu/generateur-sup-*` and `gpu/acte-sup` return public-utility
   easements (SUP): `suptype` (for example `i4` for electricity lines), `typeass` and the
   act file.

Observed in Saint-Mandé (2.419441, 48.841526): document `PLUi` of partition `DU_200057941`
(an intercommunal plan, keyed by its SIREN), zone `UFb` of type `U`, one surface
prescription and three easement areas.

Earlier the same day, `gpu/zone-urba` and `gpu/document` answered HTTP 500 for at least
20 minutes, with a GeoServer `ExceptionReport` wrapped in `{"type": "error", "message": …}`.
Report such an outage; do not answer from another source without saying so.

## Protected areas (`nature`)

| Endpoint | Areas |
| --- | --- |
| `natura-habitat` | Natura 2000, Habitats Directive (SIC/ZSC) |
| `natura-oiseaux` | Natura 2000, Birds Directive (ZPS) |
| `znieff1`, `znieff2` | ZNIEFF of type 1 and type 2 |
| `rnn`, `rnc` | National reserves and reserves of Corsica |
| `pn`, `pnr` | National parks and regional nature parks |
| `rncf` | National hunting and wildlife reserves |

The responses carry `sitecode` and `sitename` (Natura 2000) or `id_mnhn` and `nom`
(ZNIEFF), and a link to the INPN record in `url`. A point in the Fontainebleau forest
(2.6458, 48.4038) returned `FR1100795` from `natura-habitat` and `FR1110795` from
`natura-oiseaux`: one network alone gives an incomplete answer. The `crs` member is
`urn:ogc:def:crs:CRS::84`.

## Agricultural parcels (`rpg`)

`rpg/v2` covers 2015 onward and `rpg/v1` 2010 to 2014; `annee` and `geom` are required.
On 2026-10-29, `annee=2025` was rejected with HTTP 400:
`Année Invalide : Valeur uniquement entre 2015 et 2024`. Fields include `code_cultu` (crop
code), `code_group` (crop group) and `surf_parc` in hectares. The RPG describes declared
agricultural parcels, not cadastral parcels.

## Administrative units, postcodes and generic search

- `limites-administratives/commune`, `departement` and `region` take `lon` and `lat`, or a
  `geom`. For a full layer of municipalities, use ADMIN EXPRESS through the
  `geopf-wfs-download` skill.
- `codes-postaux/communes/<postcode>` returns a JSON list of `codePostal`, `codeCommune`,
  `nomCommune` and `libelleAcheminement`. A postcode can serve several municipalities and a
  municipality several postcodes; `75001` returns the arrondissement code `75101`.
- `wfs-geoportail/search` intersects any layer of the Géoplateforme WFS with `geom`. Take
  `source` from the WFS `GetCapabilities` (for example `BDTOPO_V3:batiment`) and paginate as
  for the other modules.

## Wine appellations (`aoc`)

`aoc/appellation-viticole` accepts only POST and requires an `apikey` and a `source`
parameter. A GET answers HTTP 404. Without a key provided by the user, say that this module
is not available rather than using another source.
