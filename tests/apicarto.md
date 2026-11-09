# apicarto

Values observed on 2026-10-29. Compare a run with the live `numberMatched` and current
documents of the same day, not with these numbers alone.

## APC-01 — Every parcel of a municipality

> Récupère toutes les parcelles cadastrales de Saint-Mandé (code INSEE 94067) avec leur
> identifiant et leur contenance, et écris-les dans `output/parcelles_saint_mande.geojson`.

**Expected skill:** `apicarto`

**Expected result:** every parcel from `cadastre/parcelle` (1100 on 2026-10-29), with unique
`idu` values and `contenance` kept as the cadastral area in m², in EPSG:4326.

- [ ] reads the module description or uses the bundled script
- [ ] pages with `_start` until `numberMatched`; stopping at 1000 features fails
- [ ] does not follow the `http://localhost` links of the responses
- [ ] distinguishes `contenance` from an area computed from the geometry
- [ ] reports `numberMatched`, the features written and the access date

## APC-02 — Natura 2000 at a point

> Le point de longitude 2,6458 et de latitude 48,4038 est-il dans un site Natura 2000 ?
> Donne les codes et les noms des sites, et enregistre les réponses dans `output/`.

**Expected skill:** `apicarto`

**Expected result:** yes, in two sites named "Massif de Fontainebleau": `FR1100795`
(Habitats Directive, `natura-habitat`) and `FR1110795` (Birds Directive, `natura-oiseaux`).

- [ ] queries both Natura 2000 networks
- [ ] sends a GeoJSON geometry in longitude, latitude order
- [ ] saves the raw responses and cites the site codes from them

## APC-03 — Urban-planning zone at a point

> Quelle est la zone du plan local d'urbanisme au point de longitude 2,419441 et de
> latitude 48,841526, à Saint-Mandé ? Donne le document concerné et enregistre la réponse
> dans `output/`.

**Expected skill:** `apicarto`

**Expected result:** on 2026-10-29, zone `UFb` (type `U`) of the PLUi of partition
`DU_200057941`, with its `idurba` and `datvalid`. If the GPU module answers HTTP 500, the
run reports the outage instead of naming a zone.

- [ ] uses `gpu/zone-urba` (and possibly `gpu/document` or `gpu/municipality`)
- [ ] reports the document identifier and approval date with the zone
- [ ] says that the approved plan remains the reference
- [ ] does not invent a zone from memory or from a map image

## APC-N1 — Negative: address geocoding

> Donne les coordonnées de l'adresse 73 avenue de Paris, 94160 Saint-Mandé.

**Expected skill:** `geopf-geocoding`, not `apicarto`.

## APC-N2 — Negative: bulk cadastral download

> Télécharge toutes les parcelles cadastrales du département du Val-de-Marne pour un
> usage hors ligne.

**Expected skill:** `geopf-download-files` (a Parcellaire Express package), or
`geopf-wfs-download` for a filtered extract; not thousands of `apicarto` pages.
