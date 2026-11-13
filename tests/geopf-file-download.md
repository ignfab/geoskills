# geopf-file-download

## DLF-01 — Discover packages

> Cherche les archives ADMIN EXPRESS proposées par la Géoplateforme. Présente dans
> `output/catalogue.md` les éditions, formats, territoires et liens que tu as réellement
> trouvés. Limite la découverte à trois pages et ne télécharge aucune archive volumineuse.

**Expected skill:** `geopf-file-download`.

**Expected result:** a catalogue built from the Download API responses (resource, then
editions and file links), labelled as partial when more pages exist. Live editions change:
compare with the responses saved during the run.

- [ ] queries the Download API capabilities before naming a resource or an edition
- [ ] reads `page`, `pagesize` and `totalentries` and stops after three pages
- [ ] says the catalogue is partial when `totalentries` exceeds what was read
- [ ] lists only editions, formats, territories and links found in the responses
- [ ] downloads no archive and does not describe archive contents it has not opened

## DLF-02 — Interrupted transfer

> Un téléchargement d'archive est interrompu. J'ai le fichier partiel et l'URL, mais pas
> les anciens en-têtes ; cette URL désigne la dernière édition et peut changer. Explique
> dans `output/reprise.md` comment reprendre le travail sans mélanger deux versions.
> N'effectue aucun téléchargement.

**Expected skill:** `geopf-file-download`.

**Expected result:** a written procedure. Without the original strong `ETag`, the partial
file cannot be tied to an edition, so a blind resume could join two editions.

- [ ] refuses a resume without `If-Range` (a bare `curl --continue-at -`) or any append
  onto the partial file
- [ ] rediscovers the edition and its stable file link before downloading again
- [ ] restarts into a new partial file unless the original identity can be established
- [ ] checks the size and integrity of the whole file before using it
- [ ] keeps a manifest of the edition, URL, size and date for the next attempt

## DLF-N1 — Negative: filtered features

> Je veux seulement cinq bâtiments autour de Saint-Mandé en GeoJSON, obtenus par WFS.
> Explique la procédure sans lancer le téléchargement.

**Expected skill:** `geopf-wfs-download`, not `geopf-file-download`.

- [ ] describes a bounded WFS request limited to five features
- [ ] does not propose a full Download API archive
