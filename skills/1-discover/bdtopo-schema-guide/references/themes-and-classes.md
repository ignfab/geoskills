# Themes and initial classes

Scope: IGN BD TOPO model 3.5, July 2026 specification; provenance and retrieval details are
in [sources](sources-and-versions.md). The [JSON subset](schema-3.5-2026-07.json) is the
single maintained source for field facts.

| Need | Documented PostgreSQL class | Geometry | Source pages |
| --- | --- | --- | --- |
| Building characteristics | `batiment` | MultiPolygon Z | 65–66 |
| Road-segment characteristics | `troncon_de_route` | LineString Z | 354 |

These geometry types describe the model, not the actual CRS, completeness, dimensions or
quality of a user's export. Inspect those separately. A building feature count need not
be a count of dwellings or distinct real-world properties. A road-segment count is not a
count of named roads. Do not infer building-to-municipality or road-network joins from
class names alone; inspect actual identifiers and documented relationships first.

Administrative classes and other themes are intentionally outside this initial subset.
For such requests, find the applicable official chapter or state that the answer is not
verified offline. Do not manufacture a class using a translated concept name.
