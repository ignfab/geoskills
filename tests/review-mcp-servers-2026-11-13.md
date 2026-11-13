# MCP server routes — 2026-11-13

This review covers the `## MCP servers` sections added to 17 skills: use a connected
Geocontext, PostGIS or QGIS MCP server first, and the documented commands otherwise. It
records what was checked against the real Geocontext service, how a small model handled
the sections on paper, the defects found and fixed, and what remains unmeasured.
[docs/mcp-servers.md](../docs/mcp-servers.md) describes the routes themselves.

## Geocontext, checked against the service

The statements about Geocontext were checked against its README, its generated tool
reference (version 0.10.0) and read-only calls to the hosted endpoint
`https://geollm.beta.ign.fr/geocontext/mcp`.

- **Three versions were in use.** The hosted endpoint answered as version 0.9.10 with ten
  tools, the package on npm was 0.9.8, and the repository documented 0.10.0 with fourteen
  tools. The WFS tools are named `gpf_wfs_*` in 0.9 and `gpf_*` in 0.10; 0.9 counts with
  `result_type: "hits"` and takes flat spatial parameters with `spatial_operator`; 0.10
  adds `gpf_count_features`, `distance`, a travel-time filter and two layer tools.
- **An unknown tool name is an error that lists the available tools**, so an agent that
  uses a 0.10 name on a 0.9 server can recover.
- `geocode` for the town hall of Saint-Mandé returned Saint-Mandé-sur-Brédoire
  (Charente-Maritime) before Saint-Mandé (Val-de-Marne): the first candidate is not always
  the right one, and there is no score.
- `altitude` returned an altitude and an accuracy text, without the elevation resource or
  the vertical reference.
- `adminexpress` returned the units covering a point with their INSEE codes and a
  `feature_ref`; a count of `BDTOPO_V3:batiment` intersecting the municipality of
  Saint-Mandé returned 1,741 objects; feature results carry no geometry and give
  `numberMatched` and `numberReturned`.
- `cadastre`, `urbanisme` and `assiette_sup` return the nearest objects with their
  distance to the point.
- The type search and description tools read a schema catalogue bundled with the server,
  not the WFS itself.

## Paper simulations with a small model

Agent scenarios and the A/B runner provide no MCP tool, so a paper exercise was used to
test the wording. For each of the 17 skills, a small model (`haiku`) received the
`SKILL.md`, a French request and a session description, and wrote the tool calls it
would make, its command steps, its message to the user and what it found unclear.
`spatial-aggregation` was simulated twice, once per server. The sessions were: Geocontext
0.9 with the real tool list of the hosted endpoint, Geocontext 0.10 with the documented
tool list, a generic PostGIS server, a QGIS server with the tool list of
`jjsantos01/qgis_mcp`, and no server at all.

| Session | Simulations | Result |
| --- | --- | --- |
| Geocontext 0.9 | 10 | Every tool name exists in 0.9.10; counts use `gpf_wfs_get_features` with `result_type: "hits"` and the flat spatial parameters; no `distance` call, the routing request falls back to the Navigation API |
| Geocontext 0.10 | 10 | Every tool name exists in 0.10.0; counts use `gpf_count_features` with `intersects_feature_filter`; `distance` is called with the `pedestrian` profile |
| PostGIS connected | 5 | 18 SQL statements, all read-only: `geometry_columns`, SRIDs, validity reasons, a left join that keeps empty zones, reconciliation counts |
| QGIS connected | 3 | The open project is read; the open map is exported with `render_map`; no project is created, loaded or saved; one read-only code execution on a layer kept out of the project |
| No server | 18 | No MCP call; the documented commands are used; no attempt to install, configure or connect a server |

All 101 proposed MCP calls named a tool of the connected server, and their arguments
satisfied the input schemas where the server publishes one. The models' lists of unclear
points led to these additions: how to check an answer that has no file, how to get the
`feature_ref` of a named municipality, what an empty `cadastre` result means, what to do
when no `geocode` candidate matches, bounded and aggregated queries in a database, and
when a tool that executes code in QGIS may be used.

This is a paper exercise: the model did not call the tools, and one model was used. It
shows that the text can be followed with the tool list of each version, not how often an
agent follows it.

## Defects found and fixed

Two reviews of the change found defects in the first version of the sections. The
factual ones were measured again on the hosted endpoint or read in the sources before
the fix.

1. **A count by intersection does not include objects that only touch the boundary.**
   The sections said the opposite. Measured on Saint-Mandé: the 1,741 identifiers
   returned by the server are exactly the buildings sharing an area with the
   municipality; none of the 3 buildings that only touch it is among them. The
   `municipality-building-profile` cross-check now compares the count with the helper's
   selected count.
2. **`cadastre` on a road is not empty.** It returns the municipality and the cadastral
   sheet at distance 0, without a parcel; only a point at sea gave an empty result. The
   rule now looks for a missing `parcelle` object.
3. **Checking `city` and `zipcode` is not enough after `geocode`.** Adding the department
   name to the text made the town hall of Saint-Mandé disappear, adding the postcode
   found it, and an unknown house number returned the street, in the right municipality.
   The sections now check `fulltext` and `kind` too, and add the postcode, not the
   department name.
4. **Some Geocontext statements were imprecise:** the type search and description tools
   read a bundled catalogue, so fields are confirmed on the service; the 0.9 request mode
   returns the compiled WFS request, not a GeoJSON layer; `feature_ref` is optional for
   planning objects and easements; the travel-time filter starts from a departure point
   and stops at 120 minutes; parameter names differ between 0.9 and 0.10, not only tool
   names.
5. **The common QGIS server cannot do what the sections assumed.** Its read tools give no
   source, layer CRS or style, so the agent now asks for the source file. Its
   `render_map` draws hidden layers in registry order, so the image is compared with the
   layer list and written to an unused path. Loading a project discards unsaved changes
   without a prompt, and loading a style replaces the whole style of the layer: both now
   need the user's agreement first, as does code execution in QGIS. Connection strings
   are never copied into a report or a project.
6. **"`SELECT` only" did not make a query read-only**, since `SELECT … INTO` and some
   functions write. The PostGIS notes now forbid both, check that a requested table name
   is unused, never drop, replace or alter an existing table, ask the user for exports
   instead of reading credentials from a configuration file, read SRIDs from the rows
   when `geometry_columns` declares none, and treat a `reltuples` of `-1` or `0` as
   unknown.
7. **Fallbacks and caveats were incomplete.** Every section now covers a failed call, not
   only a missing server; `spatial-aggregation` falls back to `geopf-wfs-download` for
   public layers; a layer missing from the catalogue search is looked for in the WFS
   capabilities; a count is compared with an export as an order of magnitude (2,636
   counted, 2,634 written for the Saint-Mandé box); an empty `urbanisme` result leads to
   `is_rnu`; `altitude` does not say whether a height is terrain or surface; `distance`
   optimizes time by default.
8. **The test let regressions through.** Mutation testing on a copy showed that a section
   could lose one of its two QGIS guards, its read-only clause, or its fallback sentence
   in some files, or add an install step, and still pass. The test now has eight checks;
   ten such mutations were applied one at a time on a copy and each made it fail.
9. **The documents disagreed in places.** The family pages, the READMEs, the reference
   page, the contributor guide and the English and French paragraphs of the root README
   now describe the same behavior.

## Verification

- `python3 .github/validate-skills.py`: 24 skills validated.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 212 tests, 26 skipped (live
  tests, PyQGIS, Mapshaper, IGN grids), no failure.
- Two reviews by independent agents: the first returned 11 findings; the second, with
  five lenses, returned 49 distinct findings. All but one were fixed; the remaining one,
  deriving the servers of a skill from the table of the reference page in the test, was
  left out to keep the test simple. The automatic verification of the second review was
  interrupted by a usage limit, so its factual findings were checked by hand: live calls
  to the hosted endpoint, the source of `jjsantos01/qgis_mcp` and the Geocontext schemas.
- No `description` field changed, and no skill outside the 17 gained an MCP mention.

## Remaining limits

- **No agent run with a connected server.** Prompts XP-18 to XP-21 of the
  [experimental catalog](prompts/catalog.md) are written for that and have not been run.
- **Geocontext is a prototype.** Tool names and parameters changed between 0.9 and 0.10
  and can change again; the hosted endpoint is a beta service.
- **PostGIS and QGIS were not exercised for real.** No database or QGIS session was
  connected; the PostGIS notes are guidance without tested SQL recipes, and the tool
  lists of other servers differ.
- **Selection is unchanged.** The `description` of each skill was not modified, so these
  sections act only once a skill is loaded.
