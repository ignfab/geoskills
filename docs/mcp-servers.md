# MCP servers

An [MCP server](https://modelcontextprotocol.io/docs/getting-started/intro) gives an agent
tools that reach a service, a database or an application directly. Three kinds of servers
are useful to these skills: Geocontext for Géoplateforme reference data, a PostGIS server
for data stored in a database, and a QGIS server for the QGIS session the user has open.

The skills use such a server **first when it is connected**, and their documented commands
otherwise. A server is never required: every skill works without one.

## The rule

| Situation | What the agent does |
| --- | --- |
| A server is connected and covers the step | Uses it first, within the limits the skill states |
| A server is connected but cannot do the step, such as a bulk export or a file in a chosen format, or its call fails | Uses the commands of the skill, and says so |
| No server is connected | Uses the commands of the skill, and may mention the server that would help |
| In every case | Never installs, configures or starts a server; reads the tool list of the connected server; validates the result and reports the route used |

Each skill concerned states this in a `## MCP servers` section of its `SKILL.md`, before
`## Prerequisites`, with the tools to use, their limits and the fallback.

## The servers

### Geocontext

[Geocontext](https://github.com/ignfab/geocontext) is published by IGNfab. It queries the
Géoplateforme on demand (geocoding, elevation, administrative units, cadastre, urban
planning, WFS layers) and returns structured answers. It hosts no data, downloads nothing
and all its tools are read-only. It is a prototype.

Its tool names change between versions. On 2026-11-13 the hosted endpoint ran 0.9.10 and
the package on npm was 0.9.8, while the repository documentation described 0.10.0:

| Need | 0.10 documentation | 0.9 (hosted endpoint, npm) |
| --- | --- | --- |
| Find, describe and read WFS types | `gpf_search_types`, `gpf_describe_type`, `gpf_get_features`, `gpf_get_feature_by_id` | `gpf_wfs_search_types`, `gpf_wfs_describe_type`, `gpf_wfs_get_features`, `gpf_wfs_get_feature_by_id` |
| Spatial filter of the feature tools | One object per filter, such as `intersects_feature_filter` with `typename` and `feature_id`; a travel-time filter | `spatial_operator` with flat parameters, such as `intersects_feature_typename` and `intersects_feature_id`; no travel-time filter |
| Count objects | `gpf_count_features` | `gpf_wfs_get_features` with `result_type: "hits"` |
| A map layer with geometries | `gpf_get_features_layer`, `gpf_get_feature_by_id_layer` (a GeoJSON URL) | `result_type: "request"` (the compiled WFS request) |
| Distance or travel time between two points | `distance` | not available |
| Geocoding, elevation, what lies at a point | `geocode`, `altitude`, `adminexpress`, `cadastre`, `urbanisme`, `assiette_sup` | the same names |

The skills therefore name both generations and tell the agent to read the tool list and
the input schemas of the connected server. The type search and description tools read a
schema catalogue bundled with the server, not the WFS itself, so the skills confirm a
field on the service before a download depends on it. The `geopf-service-selection` skill carries the
[full mapping](../skills/1-discover/geopf-service-selection/references/geocontext.md) of
tools, limits and the skill to use instead.

Observed on the hosted endpoint on 2026-11-13, as examples of why the limits matter:

- `geocode` can put a namesake in another department, or another object of the right
  municipality, first; adding the department name to the text made the town hall of
  Saint-Mandé disappear from the candidates, adding the postcode found it; an unknown
  house number returns the street;
- `cadastre` on a road returns the municipality and the cadastral sheet but no parcel,
  and `cadastre`, `urbanisme` and `assiette_sup` give the distance from the point to each
  object, which is not always 0;
- `altitude` returned a value without naming the elevation resource;
- a count of `BDTOPO_V3:batiment` intersecting the municipality of Saint-Mandé returned
  1,741 objects: exactly the buildings sharing an area with it, including those crossing
  the boundary, without the 3 that only touch it.

### A PostGIS server

No server is the reference here. Any MCP server that gives SQL access to the user's
PostgreSQL/PostGIS database works, whether it is dedicated to PostGIS (for example
[receptopalak/postgis-mcp](https://github.com/receptopalak/postgis-mcp)) or a general
PostgreSQL server, since PostGIS functions are plain SQL. The skills recognize it by its
name or tools (`postgis`, `postgres`, `sql`) and read its tool list.

When the data is already in the database, the skills run the inventory, the audit or the
analysis there instead of exporting tables. They run read-only queries (`SELECT` without
`INTO`, and no function that changes data, schema or SRID), and write a result table only
on request, under a name checked to be unused, never by dropping, replacing or altering an
existing table. Without such a server, or when a query fails, they ask you for an export
and work on that file. The user sets the connection and its credentials in the server
configuration: the skills never ask for them. A read-only database role is the safe
choice.

This route is guidance, not tested recipes: the repository has no PostGIS skill and no
database in its tests. Each note says how to apply the method and the checks of the skill
in SQL. For data in files, nothing changes.

### A QGIS server

A QGIS MCP server pairs a QGIS plugin with a server process and drives the session the
user has open. [jjsantos01/qgis_mcp](https://github.com/jjsantos01/qgis_mcp) is a common
one; its tools include `get_layers`, `add_vector_layer`, `add_raster_layer`,
`load_project`, `save_project`, `render_map` and `execute_code`. Names differ between
servers and forks, so the skills read the tool list.

The skills use it to read what is in the user's project, to export the map the user has
open and, only on request, to show a finished style or project in that session. The files themselves
(`.qml`, `.qgz`) are still produced by the tested helpers whenever standalone PyQGIS runs,
because those helpers validate the result by reloading it. Through the session alone, the
agent applies the same checks by hand and says so.

Three cautions. Creating or loading a project through the server replaces the project the
user has open and discards its unsaved changes without a prompt, so the skills do it only
when asked, after telling the user, and never save over it. The read tools of
`jjsantos01/qgis_mcp` return layer names, types, visibility and counts, but no source,
layer CRS or style, so the skills ask for the source files rather than guess them; its
`render_map` draws every layer of the project, hidden ones included, so the image is
compared with the layer list. A tool that executes arbitrary code in QGIS can do anything
QGIS can: the skills use it only with the user's agreement.

These third-party projects are examples observed on 2026-11-13, not endorsements. Check
their licence, their maintenance and what they can execute before connecting them.

## Skills and servers

| Skill | Server | Used first for | Still done with the skill's commands |
| --- | --- | --- | --- |
| [geopf-service-selection](../skills/1-discover/geopf-service-selection/README.md) | Geocontext | Answers that need no file: a place, an elevation, what lies at a point, a count or attributes of a WFS type | Choosing a service for file exports, bulk data, rasters, profiles and routes |
| [bdtopo-schema-guide](../skills/1-discover/bdtopo-schema-guide/README.md) | Geocontext | The properties of a WFS type (names, types, allowed values) from the schema catalogue bundled with the server | The versioned model, its revision and special values; the live service schema |
| [geopf-wfs-download](../skills/2-access/geopf-wfs-download/README.md) | Geocontext | Finding the layer and its fields; the expected count; answers without a file | Confirming the fields on the service; every download and conversion, with `ogr2ogr` |
| [apicarto-query](../skills/2-access/apicarto-query/README.md) | Geocontext | Parcel, planning zone, easements or administrative units at or near one point, with the distance | Areas, codes, complete listings, protected areas, RPG parcels, file outputs |
| [geopf-geocoding](../skills/2-access/geopf-geocoding/README.md) | Geocontext | Locating one place or address | CSV files, reverse geocoding, parcels, filters, scores, quality review |
| [geodata-intake](../skills/3-prepare/geodata-intake/README.md) | PostGIS | Inventory of a database: tables, geometry types, SRIDs | Inventory of files |
| [vector-data-quality](../skills/3-prepare/vector-data-quality/README.md) | PostGIS | Audit of a table: null, empty, invalid geometries, duplicate identifiers | Audit and repair of files; repairs in the database only on request |
| [geopandas-vector-analysis](../skills/4-analyze/geopandas-vector-analysis/README.md) | PostGIS | Joins and overlays between tables of the database | Files, WFS extracts, raster zonal statistics |
| [geopf-altimetry](../skills/4-analyze/geopf-altimetry/README.md) | Geocontext | The elevation of one point or a few points | A chosen resource, many points, CSV joins, profiles |
| [geopf-routing](../skills/4-analyze/geopf-routing/README.md) | Geocontext (0.10 or later for `distance` and the travel-time filter) | Locating named places; a distance or travel time between two points; objects reachable within a travel time | Route geometries, isochrones, resources, constraints |
| [geospatial-descriptive-statistics](../skills/4-analyze/geospatial-descriptive-statistics/README.md) | PostGIS | Summary of a table of the database | Summary of files, with the helper |
| [spatial-aggregation](../skills/4-analyze/spatial-aggregation/README.md) | PostGIS, Geocontext | Aggregation between tables of the database; a single count of reference objects in one administrative unit | Files; without PostGIS tables, several zones with a border policy, sums, means and ratios |
| [map-illustration](../skills/5-publish/map-illustration/README.md) | QGIS | An image of the map the user has open, compared with its layer list | Maps from data files, HTML maps |
| [qgis-layer-styling](../skills/5-publish/qgis-layer-styling/README.md) | QGIS | Finding the layer in the open project; on request and after agreement, showing the finished style | Creating and validating the `.qml` with the helper |
| [qgis-project-builder](../skills/5-publish/qgis-project-builder/README.md) | QGIS | Listing the layers already open; on request and after agreement, opening the finished project | Building and verifying the project file with the helper |
| [municipality-building-profile](../skills/6-workflows/municipality-building-profile/README.md) | Geocontext | Identifying the municipality and the building layer; a count to cross-check the helper's selected count | Downloading the buildings, their completeness evidence and the portrait |
| [terrain-elevation-screening](../skills/6-workflows/terrain-elevation-screening/README.md) | Geocontext | Identifying a named municipality; an indicative spot-check of a few elevations | The DEM, the screening and the candidate polygons |

The other skills (`geopf-file-download`, `geopf-raster-download`, `geoserver-cql-filter`,
`crs-reprojection-france`, `gdal-vector-processing`, `gdal-raster-processing` and
`mapshaper-simplify`) have no MCP route: none of these servers does their work.

## Connect a server

Connecting a server is your decision and your action: the agent never does it. For
Geocontext, add the hosted endpoint or the local package to the MCP settings of your
client. The exact syntax depends on the client:

```json
{
  "mcpServers": {
    "geocontext": { "type": "http", "url": "https://geollm.beta.ign.fr/geocontext/mcp" }
  }
}
```

```json
{
  "mcpServers": {
    "geocontext": { "command": "npx", "args": ["-y", "@ignfab/geocontext"] }
  }
}
```

With Claude Code, for example:

```bash
claude mcp add --transport http geocontext https://geollm.beta.ign.fr/geocontext/mcp
```

Start a new session, then check that the tools of the server appear in the tool list of
the agent. For a PostGIS or a QGIS server, follow the documentation of the server you
choose.

## What is checked, and what is not

- [test_mcp_sections.py](../tests/test_mcp_sections.py) checks on every push that each
  `## MCP servers` section says the server is optional, says what to do without it or
  when a call fails, ends by forbidding to install or configure a server and has no setup
  step, does not rely on the tool names of one Geocontext version, keeps a database
  read-only and the user's QGIS project unchanged unless asked; that no skill mentions an
  MCP server outside that section; and that this page and the skill READMEs list the same
  skills.
- The [review of 2026-11-13](../tests/review-mcp-servers-2026-11-13.md) records the checks
  made against the live Geocontext service, the paper simulations with a small model and
  the defects fixed.
- The agent scenarios and the A/B runner do not provide MCP tools: they exercise the
  command route. Whether an agent uses a connected server as written has not been
  measured yet; prompts XP-18 to XP-21 of the
  [experimental prompt catalog](../tests/prompts/catalog.md) are written for that.
- Geocontext reads live services and is a prototype: its answers, tools and availability
  can change. A report names the server, the tool, the filter and the access date.

Return to the [documentation guide](README.md).
