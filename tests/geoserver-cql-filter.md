# geoserver-cql-filter

These scenarios are offline filter-writing tasks. Their supplied metadata is synthetic;
do not contact `example.org` or install a server. Automated request tests check transport,
not ECQL parsing, spatial results or agent selection. On a real deployment, additionally
test known inside/outside features and compare with a query in the layer's CRS.

## CQL-01 — Strings, identifiers and URL encoding

> Prépare sans l'envoyer une requête WFS 2.0 GeoServer pour la couche test:sites à
> https://example.org/geoserver/wfs. Son schéma contient « nom » et « code » de type
> texte, « population » de type entier. Le format JSON est disponible. Je veux les noms
> commençant par L'Haÿ & Parc, un code égal à 01 ou 02 et une population d'au moins
> 1000. Limite la réponse à dix entités. Écris le filtre et la commande dans output/filtre.md.

**Expected skill:** `geoserver-cql-filter`

- [ ] preserves string codes as `'01'`, `'02'` and escapes the apostrophe as `''`
- [ ] combines `LIKE 'L''Haÿ & Parc%'`, `IN` and the numeric comparison with `AND`
- [ ] uses WFS 2.0 `typeNames`, `count=10` and raw ECQL through a URL parameter encoder
- [ ] does not pre-encode `%`, let `&` create another parameter or execute shell text
- [ ] states that the request is unexecuted and would return a sample

## CQL-02 — CRS:84 geometry against a projected layer

> Sans appeler de serveur, écris un filtre GeoServer pour les entités qui croisent ce
> polygone CRS:84 : POLYGON((2.34 48.84,2.36 48.84,2.36 48.86,2.34 48.86,2.34 48.84)).
> Le schéma de test:sites indique une géométrie shape en EPSG:2154. La configuration
> GeoServer est forceXY=true et accepte l'EWKT. Je veux une réponse WFS en EPSG:3857.
> Explique les trois systèmes de coordonnées et écris le résultat dans output/spatial.md.

**Expected skill:** `geoserver-cql-filter`

- [ ] uses `INTERSECTS(shape, SRID=4326;POLYGON((...)))` with unchanged lon/lat pairs
- [ ] distinguishes the input CRS, EPSG:2154 layer and EPSG:3857 response `srsName`
- [ ] does not replace the input SRID with 2154 or 3857 without transforming coordinates
- [ ] does not quote EWKT as text or use `SRID=84`, `SRID=CRS:84` or PostGIS SQL
- [ ] explains that returned features are selected, not clipped; proposes inside/outside checks

## CQL-03 — WMS filter list and axes

> Prépare sans l'envoyer une requête GeoServer WMS 1.3.0 pour test:sites puis test:routes,
> toutes deux annoncées en EPSG:4326. Garde les sites dont la géométrie shape croise le
> point CRS:84 POINT(2.35 48.85), et toutes les routes. Le serveur accepte l'EWKT avec
> forceXY=true. Pour l'image de 256 par 256 pixels en PNG, utilise EPSG:4326 et l'emprise
> longitude 2.34 à 2.36, latitude 48.84 à 48.86. Écris dans output/carte.md.

**Expected skill:** `geoserver-cql-filter`

- [ ] keeps layer order and uses `INTERSECTS(shape, SRID=4326;POINT(2.35 48.85));INCLUDE`
- [ ] passes the whole filter list as one encoded parameter, preserving both semicolons
- [ ] uses the WMS 1.3.0 map BBOX `48.84,2.34,48.86,2.36` for EPSG:4326
- [ ] keeps the EWKT point in lon/lat despite the map BBOX being lat/lon
- [ ] explains that the response is an image and must be checked for OGC errors/blank output

## CQL-04 — Unsupported EWKT and misleading HTTP success

> Mon ancien GeoServer renvoie un statut HTTP 200 mais un document ExceptionReport
> signalant une erreur sur SRID dans mon filtre EWKT. La couche est en EPSG:2154 et
> mon polygone en CRS:84. Puis-je simplement supprimer SRID=4326 ou ajouter
> srsName=EPSG:4326 ? Sans faire de requête ni installer de logiciel, écris la démarche
> de correction dans output/diagnostic.md.

**Expected skill:** `geoserver-cql-filter`

- [ ] treats the OGC exception as failure despite HTTP 200
- [ ] rejects stripping the SRID without coordinate transformation and the output-CRS fix
- [ ] proposes plain WKT transformed into the discovered layer CRS or XML Filter Encoding
- [ ] verifies the chosen encoding's axes and recommends a bounded known-feature check
- [ ] does not change server settings, install software or claim a successful live result

## CQL-N1 — Negative: local SQL

> Écris une requête SQL PostGIS qui sélectionne les parcelles à moins de 100 mètres
> des écoles. Les deux tables sont déjà dans ma base locale, en EPSG:2154.

**Expected result:** no `geoserver-cql-filter`; use PostGIS SQL, not `cql_filter` or ECQL.

## CQL-N2 — Negative: OGC API CQL2

> Mon service OGC API Features annonce CQL2-JSON. Prépare un filtre JSON sur la propriété
> population pour garder les valeurs supérieures à 1000, sans utiliser WFS ni WMS.

**Expected result:** no GeoServer ECQL substitution; follow the service's CQL2 conformance
and request format instead of inventing a `cql_filter` parameter.
