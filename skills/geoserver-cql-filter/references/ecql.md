# ECQL syntax

Use names and types from the target layer's schema. The following invented fields are
examples, not names to assume on a service.

| Intent | Example |
| --- | --- |
| Text, including an apostrophe | `name = 'King''s Park'` |
| Identifier containing spaces | `"land use" = 'park'` |
| Preserve a string code's leading zeros | `code IN ('01', '02')` |
| Numeric range, inclusive | `height BETWEEN 10 AND 25` |
| Missing value | `height IS NULL` |
| Exclude missing values | `height IS NOT NULL` |
| Case-insensitive prefix | `name ILIKE 'park%'` |
| Group alternatives | `(kind = 'park' OR kind = 'garden') AND area > 1000` |
| Feature IDs (not an attribute named `id`) | `IN ('sites.12', 'sites.13')` |
| All / none | `INCLUDE` / `EXCLUDE` |
| UTC half-open interval | `observed_at >= 2026-01-01T00:00:00Z AND observed_at < 2026-02-01T00:00:00Z` |

`LIKE` is case-sensitive; `%` matches any sequence and `_` one character. These are ECQL
wildcards, not URL escapes. For literal wildcard characters, consult the deployed
parser's supported escaping instead of assuming SQL behavior. Use `IS NULL`, not `= NULL`.
Match the schema's date type; do not compare arbitrary text timestamps as though they
were dates. Parentheses make Boolean intent explicit.

For an external string value, double each embedded apostrophe before enclosing it in
single quotes; URL encoding is a separate step. Use only discovered/allowed identifiers
and operators when constructing expressions from inputs. Do not execute filter text as
shell code or add a SQL `WHERE`/`SELECT` wrapper.

## Spatial predicates

```text
INTERSECTS(geom, SRID=4326;POINT(2.35 48.85))
WITHIN(geom, SRID=4326;POLYGON((2.34 48.84,2.36 48.84,2.36 48.86,2.34 48.86,2.34 48.84)))
```

`WITHIN(feature, region)` tests containment; `INTERSECTS` includes partial overlaps and
boundary contact. Neither clips the returned geometry. `CONTAINS` reverses the containment
relationship. `BBOX` selects by an envelope; it cannot represent an irregular boundary.
For exact administrative selection, obtain the actual boundary instead of inventing a box.

Read [spatial filters](spatial-filters.md) for CRS and distance handling. Functions beyond
these predicates depend on the deployed server; check its capabilities/documentation.
Do not copy `ST_Intersects`, `ST_Transform` or other PostGIS SQL directly into ECQL.

## Sources

- [GeoServer CQL/ECQL tutorial](https://docs.geoserver.org/stable/en/user/tutorials/cql/cql_tutorial/).
- [GeoServer ECQL reference](https://docs.geoserver.org/stable/en/user/filter/ecql_reference/).
