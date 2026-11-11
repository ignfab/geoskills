# Attribute interpretation

Use [schema-3.5-2026-07.json](schema-3.5-2026-07.json) for the exact format names, types,
meanings, source keys and pages. Class lookup returns a **subset**, never all fields.

Building entries include `hauteur`/`HAUTEUR`, `nature`/`NATURE` and `usage_1`/`USAGE1`.
Road entries include `nature`/`NATURE`, `importance`/`IMPORTANCE` and
`nombre_de_voies`/`NB_VOIES`. Uppercase Shapefile aliases shown here are documented mappings,
not a rule to apply to unknown attributes. The road importance enum is complete (1–6);
other enums are not fully bundled and must not be reconstructed from memory.

## Before downstream statistics

Building height zero is documented as unknown or not significant (pp. 76–77). Road lane
count zero has conditional special meanings (p. 371); the source also contains potentially
conflicting ferry rules. State that ambiguity instead of treating all zeroes as measured
absence or inventing a universal conversion.

`geospatial-descriptive-statistics` and `spatial-aggregation` preserve **valid** zeroes.
For a source-specific sentinel, explicitly declare the conversion in an in-memory derived
column, keep the original, and report its excluded count separately from originally null
values. Confirm the source model/revision first. Do not globally replace zeroes in every
numeric field. Style generation similarly needs a declared policy for these special values.

No field's absence from this subset means it is absent from BD TOPO. For an invented field,
return unverified; for a proposed renamed/deprecated field, cite version-change evidence
or leave the claim unresolved.
