# geopf-wfs-download

## WFS-01 — Complete bounded building extract

> Télécharge tous les bâtiments BD TOPO intersectant la boîte 1.443, 43.603, 1.446, 43.606
> (longitude/latitude WGS84), dans output/batiments.gpkg.

**Expected skill:** `geopf-wfs-download`.

- [ ] uses the advertised `BDTOPO_V3:batiment` layer and confirms its schema/CRS
- [ ] uses `-spat ... -spat_srs EPSG:4326` or an equivalent server-side spatial filter
- [ ] does not use `-limit` for this request for all buildings in the box
- [ ] checks feature count, geometry and CRS; reports a failed page as incomplete
- [ ] explains that intersecting features retain their whole geometry unless clipping was requested

## WFS-02 — Small sample in standard GeoJSON

> Donne-moi un échantillon de 5 bâtiments BD TOPO autour du Capitole de Toulouse,
> en GeoJSON dans output/echantillon.geojson.

**Expected result:** 1–5 polygon features in WGS84 longitude/latitude, near Toulouse.

- [ ] uses a small bounding box and `-limit 5`; labels the output as a sample
- [ ] produces RFC 7946 GeoJSON, including reprojection if needed
- [ ] does not download the national layer to sample it locally

The automated live test also disables paging and requests a page of five features to
bound transfer. A sample does not establish the count of the complete layer.

## WFS-03 — Add a distinct GeoPackage layer

> Ajoute la couche des régions ADMIN EXPRESS à output/batiments.gpkg, sous le nom regions.

Run after WFS-01. Verify that the existing buildings remain intact and a `regions` layer
is created. Use `-update -nln regions`; reserve `-append` for adding features to an
existing compatible layer. Resolve the actual ADMIN EXPRESS layer name from capabilities.

## WFS-04 — Missing Parquet driver

> Je veux exporter les communes et les départements ADMIN EXPRESS en GeoParquet.
> Supposons que le contrôle initial confirme que ogr2ogr fonctionne et lit le WFS, mais
> que son pilote Parquet est absent. Présente les solutions avant tout téléchargement
> ou conversion, et explique comment organiser les fichiers de sortie.

**Expected skill:** `geopf-wfs-download`.

- [ ] distinguishes a working GDAL/WFS reader from a missing output writer
- [ ] offers user-run Conda/Mamba, compatible distribution packages and official GDAL
  `ubuntu-full` container options; does not promise Parquet in `ubuntu-small`
- [ ] asks for the environment choice instead of silently using Python, `uv` or GeoPackage
- [ ] never installs packages or pulls a container image itself
- [ ] rechecks capabilities in the chosen environment and uses it for output validation
- [ ] explains one GeoParquet file per typename, with separate validation of both files

## WFS-05 — Missing ogr2ogr

> Comment préparer un téléchargement WFS de la Géoplateforme en GeoPackage si la
> commande ogr2ogr n'est pas disponible ? Propose la marche à suivre sans rien installer
> et sans lancer le téléchargement.

**Expected skill:** `geopf-wfs-download`.

- [ ] supplies GDAL installation/container choices for the user, with WFS and GPKG checks
- [ ] waits for the user's environment choice; does not launch an interactive setup
- [ ] does not use an already installed Python package as implicit permission to switch

## WFS-06 — Explicit last-resort proposal

> Je dois obtenir du GeoParquet depuis le WFS de la Géoplateforme, mais aucun GDAL avec
> le pilote Parquet n'est utilisable, je ne peux pas en installer et Docker est
> indisponible. Quelle solution de dernier recours proposes-tu ? N'installe rien et
> n'exécute pas encore la conversion.

**Expected skill:** `geopf-wfs-download`, with `geopandas-basics` only for an agreed
Python fallback.

- [ ] explains why the normal GDAL/container options are unavailable
- [ ] proposes Python conditionally and obtains agreement before executing a conversion
- [ ] checks existing dependencies; no automatic installation, including via `uv`
- [ ] retains the requested format, per-layer files and output-validation requirements

These are planning scenarios and need no service requests. To reproduce WFS-04 against
real CLI checks, use an isolated test environment with `OGR_SKIP=Parquet`; it disables
that driver without uninstalling software. Command tests and dry runs do not prove that
an agent follows the tooling rule.

## WFS-N1 — Negative: raster imagery

> Télécharge l'orthophoto du Capitole de Toulouse.

**Expected skill:** `geopf-wms-wmts`; do not use the WFS for imagery.

## WFS-07 — Count alone hides duplicates

> Un export WFS contient cinq objets dont les identifiants source sont 01, 02, 03, 04, 04.
> Le service annonçait cinq correspondances avant et après le téléchargement. Peut-on
> dire que l'export est complet ? Écris ton diagnostic dans `output/completude.md`, sans
> faire d'appel réseau ni installer d'outil.

Expected: duplicated source ID makes completeness unverified despite equal counts;
check paging/order, retain partial output/logs and avoid blind append.
