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
[Licence Ouverte 2.0](https://www.data.gouv.fr/pages/legal/licences/etalab-2-0).
The historical fixture acquisition version/date is not recorded separately; regression
values were supplied with the scenarios and rechecked against the stored fixtures on
2026-09-30. Live service responses can differ from these snapshots.

## Additional synthetic fixtures

- `terrain_screening.asc` and `terrain_screening_aoi.geojson`: invented 7 × 7 terrain grid
  and its 70 × 70 m AOI (repository MIT license). Confirmed EPSG:2154, 10 m cells, metre
  elevations in an arbitrary synthetic vertical reference, not real ground/aviation data.
  No `.prj` is supplied; this metadata authorizes CRS assignment on a copy. The left four
  columns are 100 m except a valid zero at the northwest corner and nodata at the southwest
  corner; the right three columns are 200 m. The interval [0, 100] retains 27 of 48 valid
  cells (2,700 m²); Horn slope ≤ 5 degrees additionally retains 8 cells (800 m²). Without
  a halo, 25 cells have unknown slope, including edges and the nodata neighbourhood.
- `geocoded_synthetic.csv`: seven invented API rows; policy 0.7 score / 0.1 margin,
  expected INSEE code and housenumber yields 1 accepted, 5 review and 1 unmatched.
- `elevation_points.csv` and `elevations_synthetic.json`: two invented points/results,
  string IDs, one missing elevation sentinel; vertical datum intentionally unknown.
- `classes_synthetic.asc`: invented 2×2 categorical grid in confirmed EPSG:2154, 10 m
  cells, classes 0/1/5 and nodata 255; nearest refinement to 5 m yields 75% valid coverage.

- `communes_sans_cpg/communes.shp`: three municipality points (Saint-Mandé `94067`,
  L'Haÿ-les-Roses `94038`, Cœuvres-et-Valsery `02201`) in **EPSG:2154**, with a `.prj`.
  Text is encoded in **CP1252 without a `.cpg`** and with no code page in the `.dbf`, as in
  legacy Windows deliveries; `œ`, `–` and `«` distinguish CP1252 from ISO-8859-1. Read with
  `-oo ENCODING=CP1252`. Coordinates are the municipality points returned by the IGN
  geocoder on 2026-10-29, not town-hall positions.
- `communes_points.geojson`: the same three points in EPSG:4326, UTF-8, with the fields
  `code_insee`, `nom_officiel`, `nom_officiel_en_majuscules` and `remarque`. Two names
  exceed the 10 characters of a Shapefile field.

These fixtures contain no private user records and may be copied into isolated agent runs.

## Vector aggregation fixtures

`aggregation_objects.geojson` and `aggregation_zones.geojson` are invented planar fixtures
with declared EPSG:2154 metre coordinates (not real locations). Points a/b lie inside zone
001, c inside 002, edge on their common border and outside in no zone. Zone NA is empty.
Heights are 0, 10, null, 30 and 100; denominators are 2, 0 and null. The literal ID NA
and leading zeroes test string preservation. No external source or network is required.

## Municipal building profile fixtures

`building_profile_municipalities.geojson`, `building_profile_buildings.geojson` and
`building_profile_input.json` are invented planar data and a manifest (repository MIT
license). They are not IGN data or real administrative boundaries. EPSG:2154 coordinates
are near 650000 E, 6860000 N; each of the two municipalities is a 100 × 100 m square.
Codes `00001`/`00002` deliberately test string preservation.

For `00001`, buildings `001` and `002` each occupy 400 m² and overlap over 100 m²;
`003` crosses the eastern border (100 m² original, 50 m² inside), `004` occupies 100 m²,
`touch` touches only the border and `outside` is disjoint. Four objects are selected;
the union covers 850 m² (8.5%), while clipped individual areas sum to 950 m².
Heights for the six source records are 10, 20, 0, 500, 1000 and null; zero is an explicit
**synthetic fixture** sentinel. Selected heights have mean/median 15 m and linear quartiles
12.5/17.5 m. Selected usage counts are housing 2, literal NA 1 and missing 1. Do not apply
that synthetic height policy to production data without verifying its own specification.
