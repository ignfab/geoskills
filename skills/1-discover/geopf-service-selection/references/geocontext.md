# Geocontext MCP server

[Geocontext](https://github.com/ignfab/geocontext) is an MCP server published by IGNfab.
It queries the Géoplateforme on demand and returns structured answers: it hosts no data
and downloads nothing to the user's machine. Every tool is read-only. The project is a
prototype: tools and names change between versions.

Geocontext is optional. Use it first when it is connected and covers the request;
otherwise use the services and skills of this skill's table. Never install, configure or
start an MCP server yourself.

## Is it connected?

Look at your tool list. The Geocontext tools are named as below, often with a prefix
that depends on the client, such as `mcp__geocontext__geocode`. If none is present, the
server is not connected: continue without it. You may tell the user that it exists and
that they can connect it themselves, either to the hosted endpoint
`https://geollm.beta.ign.fr/geocontext/mcp` or locally with `npx -y @ignfab/geocontext`
(Node.js required), in the MCP settings of their client.

## Tools by need

Names in the `Tool (0.10)` column are those of the Geocontext 0.10 documentation. The
`In 0.9` column gives the 0.9 equivalent when it differs. On 2026-11-13 the hosted
endpoint ran 0.9.10 and the package published on npm was 0.9.8: both showed the 0.9 names.
Version 0.10 was documented in the repository but not yet published. Always read the tool
list and the tool descriptions of the connected server.

| Need | Tool (0.10) | In 0.9 | Limits | Use instead |
| --- | --- | --- | --- | --- |
| Coordinates of a place or address | `geocode` | same | Up to 10 candidates, no score; the first one can be a namesake or another object of the municipality | `geopf-geocoding` for CSV files, reverse geocoding, parcels, filters and scores |
| Elevation of a point | `altitude` | same | One point per call; the resource, the vertical reference and terrain or surface are not stated; `-99999` is missing data, returned without an error | `geopf-altimetry` for a chosen resource, many points or a profile |
| Distance or travel time between two points | `distance` | not available | No route geometry; the default `profile` is `spherical`, a straight line like `ellipsoidal`: pass `car` or `pedestrian` for a road distance and a travel time | `geopf-routing` for a route geometry or a reachable area |
| Administrative units at a point | `adminexpress` | same | A point only; returns INSEE codes and a `feature_ref` | `geopf-wfs-download` for boundaries as files |
| Cadastral objects near a point | `cadastre` | same | Objects within 10 m, at most one per type, each with its `distance` | `apicarto-query` for areas, codes and complete listings |
| Urban-planning objects at or near a point | `urbanisme` | same | A point only; each object has its `distance` | `apicarto-query` for areas and complete listings |
| Public-utility easements at or near a point | `assiette_sup` | same | A point only; each area has its `distance` | `apicarto-query` |
| Find a WFS type from keywords | `gpf_search_types` | `gpf_wfs_search_types` | French keywords work best; searches the bundled catalogue | WFS GetCapabilities |
| Property names, types and allowed values of a type | `gpf_describe_type` | `gpf_wfs_describe_type` | A schema catalogue bundled with the server, not the WFS itself | WFS DescribeFeatureType, to confirm a field on the live service |
| Count the objects matching a filter | `gpf_count_features` | `gpf_wfs_get_features` with `result_type: "hits"` | One number; state the filter used | `geopf-wfs-download` for a counted export |
| Read attributes of objects | `gpf_get_features` | `gpf_wfs_get_features` | No geometry; 100 objects by default, 5,000 at most | `geopf-wfs-download` for a file or a complete extract |
| One object from its `feature_ref` | `gpf_get_feature_by_id` | `gpf_wfs_get_feature_by_id` | Exactly one object, or an error | — |
| A map layer with geometries | `gpf_get_features_layer`, `gpf_get_feature_by_id_layer` (a GeoJSON URL, 5,000 objects by default) | `result_type: "request"` (the compiled WFS request; 100 objects unless `limit` is raised) | Meant for a map display tool; 5,000 objects at most | `geopf-wfs-download` for a file in a chosen format and CRS |

The spatial filter also changes shape. Version 0.10 takes one object per filter, such as
`intersects_feature_filter` with `typename` and `feature_id`, or `bbox_filter`. Version 0.9
takes `spatial_operator` (`bbox`, `intersects_point`, `dwithin_point` or
`intersects_feature`) with flat parameters such as `intersects_feature_typename` and
`intersects_feature_id`, and has no travel-time filter. Read the input schema of the tool
before filling it.

Geocontext has no tool for raster images, ready-made archives, elevation profiles, route
geometries, protected natural areas or RPG parcels: use `geopf-raster-download`,
`geopf-file-download`, `geopf-altimetry`, `geopf-routing` and `apicarto-query`.

## Rules when using it

- Coordinates are longitude and latitude in WGS84, in that order.
- Find the type before querying it, and describe it before filtering: property names
  cannot be guessed, and a wrong name is an error.
- An administrative unit or a parcel comes with a `feature_ref` (`typename` and
  `feature_id`); a planning object or an easement has one when its layer can be queried.
  Reuse it as the spatial filter of the feature tools
  rather than typing a bounding box. For a named municipality, `geocode` then
  `adminexpress` at that point give its INSEE code and its `feature_ref`.
- A filter by intersection counts the objects sharing an area with the reference object,
  including those that cross its boundary; objects that only touch it were left out on
  2026-11-13. Say so when you report a count.
- Compare `numberReturned` with `numberMatched`. When they differ, the answer is a
  sample: raise `limit`, narrow the filter, or switch to `geopf-wfs-download`.
- `cadastre`, `urbanisme` and `assiette_sup` return the `distance` in metres between the
  point and each object. Above 0, the object is near the point, not at it: report it. A
  `cadastre` result without a `parcelle` object means that no parcel lies within 10 m, as
  on a road or a public space; the municipality and the cadastral sheet are still
  returned. An empty `urbanisme` result does not mean that no rule applies: check
  `gpu/municipality` with `apicarto-query`.
- The first `geocode` candidate can be a namesake elsewhere or another object of the
  right municipality: check `fulltext` and `kind` as well as `city` and `zipcode`. A
  `street` candidate for a requested house number is the street, not the address. When
  nothing matches, add the postcode to the text, not the department name, or take another
  candidate.
- Check an answer before reporting it: no error returned, the right place or object and a
  plausible value. The layer tools of version 0.10 return geometries, but for map display
  and at most 5,000 objects: they do not replace a checked file export.
- A failed call returns an error message, not an empty result. Report it, then use the
  service or skill of the last column; do not answer from memory.
- In the report, name the server and its version when known, the tool, the type, the
  filter and the access date. Geocontext reads live services: a value can change.
