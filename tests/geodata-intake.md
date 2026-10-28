# geodata-intake scenarios

## INT-01 — Inventory an unfamiliar delivery

> Examine les fichiers `data/monuments_sans_prj/` et `data/mnt_dalles/` sans les modifier.
> Fais un inventaire dans `output/inventaire.md` : formats, couches, champs, dimensions,
> systèmes de coordonnées déclarés et métadonnées manquantes. Ne déduis pas une projection
> à partir des seules coordonnées. Propose la prochaine étape sans transformer les données.

Expected: `geodata-intake`; one logical Shapefile and two ASCII raster tiles. The files
have no declared CRS; that absence remains explicit. No `.prj` or statistics sidecar is
created, no coordinate assignment/repair. The report distinguishes observations from
external producer metadata if consulted.

## INT-02 — Inspect a spatial CSV

> Examine `data/points_gps.csv` et explique dans `output/diagnostic.md` comment préparer
> ces données pour une analyse géographique. Vérifie les noms des colonnes et les ordres
> de grandeur, sans reprojeter ni réécrire le fichier.

Expected: latitude comes before longitude; three points including Réunion. Do not label
all points as mainland Lambert-93 or infer spatial column order by position.

## INT-N1 — Explicit conversion

> Convertis `data/saint_mande.geojson` en `output/commune.gpkg`, en conservant son système
> de coordonnées et ses attributs.

Expected: direct vector I/O workflow; no broad delivery inventory or `geodata-intake` load.
