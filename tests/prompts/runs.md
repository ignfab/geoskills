# Experimental prompt runs

One row per run, oldest first. The prompts are in [catalog.md](catalog.md), and the
[README](README.md) defines each column and outcome.

| Date | Prompt | Harness | Model | Commit | Skills loaded | Outcome | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-09 | XP-05 | Claude Code 2.1.287 (`claude -p`, A/B runner) | claude-opus-5-5 | b7e4bc3 | `geopf-routing` | partial | 51.1 of 90.6 ha (56.4 %) within 10 minutes, confirmed from the raw isochrone. Isochrone parameters taken from the capabilities; raw responses kept. The town hall was geocoded with curl on the POI index and checked against its address (7 m apart), but without `geopf-geocoding`; the overlay used GeoPandas without `geopandas-basics`. $0.58, 15 turns. |
| 2026-11-09 | XP-01 | Claude Code 2.1.287 (`claude -p`, A/B runner) | claude-opus-5-5 | b7e4bc3 | `geopf-wms-wmts` | partial | Sound advice: RGE ALTI at 1 m through the WMS-R in Lambert-93, terrain rather than surface model, no WMTS image tiles. No discovery request, so layers and coverage were not checked online. `geopf-services` was not loaded, here or in an earlier run without network access: its description sends elevation tasks to the specialized skills. Follow-up: decide which skill owns product choice. $0.25, 4 turns. |
