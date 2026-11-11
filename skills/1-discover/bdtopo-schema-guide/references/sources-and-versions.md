# Sources and version scope

The bundled source is IGN's **BD TOPO 3.5 content specification**, file
[DC_BDTOPO_3-5.pdf](https://data.geopf.fr/annexes/ressources/documentation/DC_BDTOPO_3-5.pdf),
revision **July 2026**, checked on **2026-11-11**. The title above is translated into English.
The PDF's model number is 3.5; its revision date is not the user's dataset edition.
SHA-256 of the inspected PDF:
`0542356dcf921bff5263043fe2af288a018d61d8e0f4d750005142f09cdb7331`.

The old geoservices URL redirected to an HTML map page during verification. Use the PDF
URL above and check content type and title; a successful HTTP status does not prove PDF
content. The URL is mutable: pin facts by revision and hash, not only filename.

Every entry in [the subset](schema-3.5-2026-07.json) has a source key and printed page
numbers; that key resolves to publisher, URL, title, version, revision and checked date.
Only the listed classes/fields and explicitly complete enumerations are covered. Other
3.5 revisions, 3.3/3.4 and future models are not asserted compatible or incompatible.

## Refresh procedure

1. Retrieve the official specification in the foreground to a **new** local path, without
   installing download/PDF tools. Verify PDF magic, cover version/revision and publisher.
2. Record retrieval date and hash. Read the relevant complete pages, including continued
   constraints on the following page; inspect tables visually where extraction is ambiguous.
3. Compare each curated identifier, type, unit, sentinel and format mapping. Add a new
   versioned snapshot when semantics/revision changes; preserve old provenance.
4. For removals/renames consult IGN's
   [model change history](https://data.geopf.fr/annexes/ressources/documentation/SE_BDTOPO_depuis_v3-0.pdf)
   and the relevant before/after specifications. A missing entry in this subset proves nothing.
5. Update references, lookup selection and offline regression tests together. Run a building,
   road, unknown-field and unsupported-version prompt. Live WFS checks remain optional and
   dated; they must not replace the model documentation or become ordinary CI dependencies.
