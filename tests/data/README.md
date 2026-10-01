# Fixture metadata

These small files are test inputs, not authoritative production data. Keep originals
unchanged; write generated files and sidecars outside this directory.

- `adresses.csv`: eight test cases mixing public-place addresses, an invented unmatched
  address and an empty query. UTF-8 without BOM, deliberately exercising encoding detection.
  Postal codes and identifiers are strings, including leading zeros.
- `points.csv`: longitude/latitude points near public landmarks, EPSG:4326.
- `points_gps.csv`: named points in EPSG:4326, with **latitude before longitude** in the CSV.
- `points_lambert2e.csv`: test coordinates in EPSG:27572 (NTF Paris / Lambert zone II).
- `monuments_sans_prj/monuments.shp`: three Paris landmarks in **EPSG:2154**. The `.prj` was
  intentionally omitted. Control point: Notre-Dame is near 2.3499° E, 48.8530° N.
- `mnt_dalles/*.asc`: IGN RGE ALTI extracts of Saint-Mandé in **EPSG:2154**, metre units,
  10 m pixels, vertical reference NGF-IGN69, nodata `-99999`. The `.prj` files were
  intentionally omitted. The two adjacent tiles form a 145 × 195 pixel mosaic.
- `saint_mande.geojson`: IGN ADMIN EXPRESS boundary of Saint-Mandé (INSEE `94067`),
  EPSG:4326 longitude/latitude; approximately 90.6 ha in Lambert-93.

The IGN boundary and DEM extracts are distributed under the
[Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
The historical fixture acquisition version/date is not recorded separately; regression
values were supplied with the scenarios and rechecked against the stored fixtures on
2026-09-30. Live service responses can differ from these snapshots.
