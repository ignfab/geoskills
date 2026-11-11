# bdtopo-schema-guide

## BTS-01 — Building semantics offline

> Sans accès réseau ni téléchargement, explique pour le modèle BD TOPO 3.5 documenté en juillet 2026 quelle classe et quel champ décrivent la hauteur des bâtiments, ce que signifie zéro, et cite la source.

**Expected skill:** `bdtopo-schema-guide`.

**Expected result:** class `batiment`, field `hauteur` (`HAUTEUR` in Shapefile), in
metres from the lowest adjacent ground to the highest eaves edge (not the roof ridge);
zero means unknown or not significant. Source: IGN specification, model 3.5,
July 2026 revision, pp. 76–77, read from the bundled snapshot without any network call.

- [ ] names `batiment` and `hauteur`, with `HAUTEUR` as the documented Shapefile name
- [ ] says the height runs to the eaves in metres, and that 0 means unknown or not
  significant
- [ ] cites model version, document revision and pages 76–77
- [ ] makes no network call and downloads nothing

## BTS-02 — Road hierarchy and unsupported version

> Pour le modèle BD TOPO 3.5 documenté en juillet 2026, indique la classe des tronçons routiers et les champs documentés pour leur importance et leur nombre de voies. Peut-on affirmer sans autre preuve que ces champs sont identiques dans un ancien export 3.3 ? Cite tes sources.

**Expected skill:** `bdtopo-schema-guide`.

**Expected result:** class `troncon_de_route`, fields `importance`/`IMPORTANCE` (enum 1–6)
and `nombre_de_voies`/`NB_VOIES`. Equivalence with model 3.3 is unverified: the answer
says so and points to the 3.3 specification instead of asserting it.

- [ ] names `troncon_de_route`, `importance` and `nombre_de_voies` with their Shapefile names
- [ ] cites the model version and revision of the source
- [ ] refuses to claim the 3.3 fields are identical without a 3.3 source

## BTS-N1 — Known WFS extraction

> Télécharge en GeoPackage une couche BD TOPO déjà identifiée depuis le WFS IGN.

**Expected skill:** `geopf-wfs-download`, not `bdtopo-schema-guide`: the layer is already
identified, so no semantic guide is needed.

- [ ] goes to the WFS download path
- [ ] does not load `bdtopo-schema-guide`

## BTS-N2 — Territorial count

> Donne-moi le nombre de bâtiments par commune avec mes deux couches locales.

**Expected skill:** `spatial-aggregation`, not `bdtopo-schema-guide`.

- [ ] treats the request as an object-to-zone count
- [ ] does not load `bdtopo-schema-guide`
