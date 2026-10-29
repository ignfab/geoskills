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
- `admin_units_synthetic.geojson`: three invented polygons near 2° E, 48° N, created for
  Mapshaper tests (repository MIT license, no external data). EPSG:4326 longitude/latitude.
  Features `001` and `002` partition a 0.02° × 0.02° rectangle with an exactly shared,
  zigzag border; feature `003` is a separate 0.0002° square. The tiny polygon tests
  `keep-shapes`; all identifiers deliberately retain leading zeros. These are not real
  administrative boundaries.
- `coverage_synthetic.geojson`: nine invented parcels `P01`–`P09` in **EPSG:2154**, near
  653000 E, 6859000 N (repository MIT license, no external data). Every polygon is valid on
  its own, but the set is not a valid coverage: `P02` and `P03` overlap by 1 m²
  (0.05 m × 20 m), `P03` and `P04` leave a 5 cm gap open to the outside, `P07` and `P08`
  leave an enclosed 4 m × 4 m gap, `P09` is an 8 m² sliver (0.1 m × 80 m) along the top of
  the second row, and `P01` has one repeated vertex. Shared edges otherwise have matching
  vertices. Used by the vector-data-quality tests and scenario VDQ-03.

The IGN boundary and DEM extracts are distributed under the
[Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
The historical fixture acquisition version/date is not recorded separately; regression
values were supplied with the scenarios and rechecked against the stored fixtures on
2026-09-30. Live service responses can differ from these snapshots.

## Additional synthetic fixtures

- `geocoded_synthetic.csv`: seven invented API rows; policy 0.7 score / 0.1 margin,
  expected INSEE code and housenumber yields 1 accepted, 5 review and 1 unmatched.
- `elevation_points.csv` and `elevations_synthetic.json`: two invented points/results,
  string IDs, one missing elevation sentinel; vertical datum intentionally unknown.
- `classes_synthetic.asc`: invented 2×2 categorical grid in confirmed EPSG:2154, 10 m
  cells, classes 0/1/5 and nodata 255; nearest refinement to 5 m yields 75% valid coverage.

These fixtures contain no private user records and may be copied into isolated agent runs.
