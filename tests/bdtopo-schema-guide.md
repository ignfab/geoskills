# bdtopo-schema-guide scenarios

## BTS-01 — Building semantics offline

> Sans accès réseau ni téléchargement, explique pour le modèle BD TOPO 3.5 documenté en juillet 2026 quelle classe et quel champ décrivent la hauteur des bâtiments, ce que signifie zéro, et cite la source.

Expected: `bdtopo-schema-guide`; batiment/hauteur (HAUTEUR in Shapefile), metres to eaves, zero unknown/not significant, IGN revision and pp. 76–77.

## BTS-02 — Road hierarchy and unsupported version

> Pour le modèle BD TOPO 3.5 documenté en juillet 2026, indique la classe des tronçons routiers et les champs documentés pour leur importance et leur nombre de voies. Peut-on affirmer sans autre preuve que ces champs sont identiques dans un ancien export 3.3 ? Cite tes sources.

Expected: `bdtopo-schema-guide`; troncon_de_route, importance/IMPORTANCE and nombre_de_voies/NB_VOIES; no unsupported equivalence to 3.3.

## BTS-N1 — Known WFS extraction

> Télécharge en GeoPackage une couche BD TOPO déjà identifiée depuis le WFS IGN.

Expected: `geopf-wfs-download`; no semantic guide for an already identified extraction.

## BTS-N2 — Territorial count

> Donne-moi le nombre de bâtiments par commune avec mes deux couches locales.

Expected: `spatial-aggregation`; no BD TOPO schema-guide load.
