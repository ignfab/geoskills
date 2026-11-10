# Data delivery services

Official starting points: [service overview](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/)
and [delivery guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/).
This summary was checked on 2026-10-27. Follow the individual guides and live metadata
before constructing a request; service availability does not guarantee dataset access.

## Map images: WMS-R and WMS-V

Both services implement WMS 1.3.0. `GetCapabilities` advertises layers, styles, formats,
CRSs and extents; `GetMap` renders an image. Where supported, `GetFeatureInfo` queries
information at a map pixel; it is not a bulk feature export.

| Source | Endpoint | Official guide |
|--------|----------|----------------|
| Raster data | `https://data.geopf.fr/wms-r` | [WMS-R](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wms-raster/) |
| Vector data rendered as images | `https://data.geopf.fr/wms-v/ows` | [WMS-V](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wms-vecteur/) |

For discovery, append `?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities`.
Choose WMS when the client needs a custom map extent, image size or supported CRS.
WMS-V is not WFS: receiving a PNG of buildings does not provide their geometries.
Respect WMS 1.3.0 axis order: EPSG:4326 uses latitude/longitude in `BBOX`; use CRS:84
for longitude/latitude only if advertised. Use `geopf-wms-wmts` for WMS-R downloads.

## Image tiles: WMTS

[Official WMTS guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wmts/).

Discovery URL:
`https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities`.

Choose WMTS for fast tiled display. `GetTile` addresses an advertised layer, style,
format, tile matrix set, matrix, row and column. Do not assume a Web Mercator grid or
invent zoom identifiers. A client that needs an arbitrary image extent may prefer WMS;
a client that mosaics tiles must respect their grid. Use `geopf-wms-wmts` for GDAL
downloads. Inspect the data type and metadata before using a tile as numeric elevation.

## Vector tiles: TMS

[Official TMS guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/tms/).

- Service metadata: `https://data.geopf.fr/tms/1.0.0`.
- Layer metadata: `https://data.geopf.fr/tms/1.0.0/{Layer}/metadata.json`.
- Tile template: `https://data.geopf.fr/tms/1.0.0/{Layer}/{z}/{x}/{y}.pbf`.

Choose TMS when a map client needs vector tiles and client-side styling. Resolve the
layer identifier from metadata and the style from the dataset's catalogue entry.
Consult the advertised tile scheme, zoom range and bounds; do not blindly flip Y or
assume an XYZ convention from the path alone. Tiles can contain clipped or generalized
geometries and zoom-dependent attributes. They are not a complete source for counts,
areas or editable feature extraction; use WFS or dataset downloads for those needs.

## Vector features: WFS

[Official WFS guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wfs/).

Discovery URL:
`https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`.

Choose WFS for bounded queries that return vector geometry and attributes.
Read `DescribeFeatureType` before filtering fields, then use `GetFeature` with a
spatial or attribute filter. A `resultType=hits` request can provide a count to compare
with downloaded features. Page complete extracts; use a limit only for an explicit
sample. A small response is not proof of completeness. Hand off to `geopf-wfs-download`;
use `geoserver-cql-filter` for GeoServer ECQL filters where supported.

## Ready-made files: download API

[Official download guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/telechargement/).

Choose this API for existing product editions, archives and large offline datasets.
Use `geopf-download-files` when installed for paginated discovery, edition selection,
foreground transfers, safe resume and integrity checks. The API returns Atom feeds,
not WFS features or map images:

1. Discover resources at `https://data.geopf.fr/telechargement/capabilities`.
2. Follow the advertised resource to `/telechargement/resource/{resourceName}`.
3. Follow a subresource to
   `/telechargement/resource/{resourceName}/{subResourceName}` and its file links.
4. Download the selected file using its advertised URL, not a filename reconstructed
   from an old edition or example.

Listings are paginated: `page` starts at 1; the documented `limit` maximum is 50.
Use the total (`gpf_dl:totalentries`) and pagination metadata to establish completeness.
Check the edition, geographic coverage, format, CRS, licence and expected size before
downloading. A spatial filter selects available packages; do not assume it clips their
contents. Prefer appropriate prepackaged files over thousands of WFS requests.

## Custom vector exports: extraction API

[Official extraction guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/extraction/).

Choose extraction when ready-made packages do not fit the requested area or when a
custom selection of tables, fields, CRS and format is needed. Compare the expected
volume and processing time with downloading existing packages; extraction is not
automatically faster for a large regional dataset.

- Landing page: `https://data.geopf.fr/extraction` (OGC API Processes).
- Process schemas: `https://data.geopf.fr/extraction/processes`.
- [Extraction API schema](https://data.geopf.fr/extraction/swagger-ui/index.html).
- [Warehouse API schema](https://data.geopf.fr/api/swagger-ui/index.html) for accessible
  stored data, including `GET /users/me/stored_data` under `https://data.geopf.fr/api`.

This workflow requires authentication. Accessible datasets depend on the account and
the producer's permissions; do not infer them from the public WFS catalogue. Discover
the data schema and process inputs before starting a job. The documented export formats
include GeoPackage, GeoJSON, GeoParquet, Shapefile, GML and PGDUMP; confirm the current
process contract before selecting one.

Check current quotas, submit only the requested job, and follow its advertised status
and result links. Queuing is not success. Confirm completion and inspect the resulting
files for the selected tables, non-empty geometries, CRS, extent and plausible counts.
Do not repeat a job submission as if it were a harmless metadata retry.
