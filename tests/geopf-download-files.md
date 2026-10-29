# geopf-download-files scenarios

## DLF-01 — Discover packages

> Cherche les archives ADMIN EXPRESS proposées par la Géoplateforme. Présente dans
> `output/catalogue.md` les éditions, formats, territoires et liens que tu as réellement
> trouvés. Limite la découverte à trois pages et ne télécharge aucune archive volumineuse.

Expected: Download API discovery before selecting names, explicit pagination/partial
catalogue, resource then edition/file links, no bulk transfer or claim of clipped contents.

## DLF-02 — Interrupted transfer

> Un téléchargement d'archive est interrompu. J'ai le fichier partiel et l'URL, mais pas
> les anciens en-têtes ; cette URL désigne la dernière édition et peut changer. Explique
> dans `output/reprise.md` comment reprendre le travail sans mélanger deux versions.
> N'effectue aucun téléchargement.

Expected: no blind append/resume; rediscover an edition, restart into a new partial file
unless original identity can be established, check whole-file size/integrity, retain manifest.

## DLF-N1 — Filtered features

> Je veux seulement cinq bâtiments autour de Saint-Mandé en GeoJSON, obtenus par WFS.
> Explique la procédure sans lancer le téléchargement.

Expected: `geopf-wfs-download`; no Download API package workflow or full archive.
