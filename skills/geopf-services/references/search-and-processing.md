# Search, calculations and validation

These service summaries were checked against the linked official guides on 2026-10-27.
Use the current metadata and API schemas for parameters, resources and limits.

## Dataset discovery and metadata

Use the [CSW metadata service](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/csw/)
to find dataset/service descriptions, provenance, coverage, licence and distribution links.
Start with
`https://data.geopf.fr/csw?SERVICE=CSW&REQUEST=GetCapabilities&VERSION=2.0.2`.
Discover supported metadata types before `GetRecords`; page using `MAXRECORDS` and
`STARTPOSITION` (starting at 1). Retrieve a selected record with `GetRecordById` and
follow its distribution links to the appropriate data service. A catalogue record is
metadata, not the dataset itself or proof that its download link is currently working.

The [Géoplateforme search service](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/recherche/)
describes searching published offerings in a general index and custom searches on
imported data. It can help locate an offering by text; it is not the address geocoder.
The linked overview does not specify a complete request contract. Follow current
official API documentation or the [catalogue interface](https://cartes.gouv.fr/rechercher-une-donnee/search)
instead of guessing a `/search` route or its parameters. Then check that offering's
service capabilities before selecting its layers and formats.

## Geocoding and autocomplete

| Need | Discovery | Operations and documentation |
|------|-----------|------------------------------|
| Address, place or parcel to coordinates; reverse lookup; batch geocoding | `https://data.geopf.fr/geocodage/getcapabilities` | [Geocoding guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/) and [API schema](https://data.geopf.fr/geocodage/openapi) |
| Suggestions while typing an address or place | `https://data.geopf.fr/geocodage/completion/getcapabilities` | [Autocomplete guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/autocompletion/) and [API schema](https://data.geopf.fr/geocodage/completion/openapi) |

Use `geopf-geocoding` for search, reverse search and CSV workflows. Autocomplete uses
`https://data.geopf.fr/geocodage/completion/` with text and supported filters; it is a
search-interface service, not a bulk address-validation substitute. Discover resource
types and geographic filters rather than copying identifiers from old examples.

Review candidate labels, geographic plausibility, ambiguity and coverage; a returned
coordinate does not guarantee the address matched. Preserve unmatched batch records
and identifiers. An overview request does not authorize sending user address lists.

## Elevations and profiles

[Official elevation guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-altimetrique/)
and [API schema](https://data.geopf.fr/altimetrie/api/index.html).

Use `geopf-altimetry` when installed for point/CSV requests, missing-elevation handling
and sampled profiles.

Discover resources at `https://data.geopf.fr/altimetrie/resources`, then inspect the
chosen resource's coverage, source and precision. The service can return elevations at
points or a sampled profile along a line. Point elevation uses
`https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json`; consult the schema
for the profile operation and supported input sizes.

Use longitude/latitude as specified by the API, not projected metre coordinates.
Different source DEMs can produce different answers. Confirm the vertical reference
from resource documentation; do not equate an altitude with GNSS ellipsoidal height.
The documented uncovered-point marker is `-99999`, not a real elevation. Check that
valid results cover the requested points and have plausible units and magnitudes.
For a full DEM or local raster processing, prefer the appropriate download service
and `gdal-raster-basics`, not millions of point-elevation requests.

## Routes and reachable areas

Both use `https://data.geopf.fr/navigation/getcapabilities` and the
[navigation API schema](https://data.geopf.fr/navigation/openapi/).

Use `geopf-routing` when installed for route and isochrone requests, unit/direction
checks and geometry exports.

| Need | Endpoint | Official guide |
|------|----------|----------------|
| A route between a start and an end, optionally with intermediate stops | `https://data.geopf.fr/navigation/itineraire` | [Routing](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-itineraire/) |
| An area reachable within a time or distance, from or towards a point | `https://data.geopf.fr/navigation/isochrone` | [Isochrones and isodistances](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-isochrone-isodistance/) |

Discover the resources and options for the specific operation. Do not assume a routing
engine supports isochrones, every travel profile or every exclusion constraint.
Confirm the travel profile, optimization, direction, cost and distance/time units.
Geocode addresses first if necessary; an address string is not a coordinate pair.

Validate output geometry, CRS, endpoints or reachable area, and plausible distance
and duration. An isochrone follows the network; it is not a Euclidean buffer. A successful
route request does not imply live-traffic information or guaranteed travel time.

## Standards validation

[Official validation guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/validation/)
and [API schema](https://data.geopf.fr/validation/swagger-ui/index.html).

The authenticated API accepts an archive and checks it against a supported standard,
such as a PLU or PCRS data model. It produces a CSV report and can optionally return
standardized data. This is different from a local geometry-validity check:
use `vector-data-quality` for local empty/invalid/duplicate feature inspection.

Before submitting to `https://data.geopf.fr/validation/api/validations`, confirm the
standard and its version, supported archive format, retention period, account access
and permission to upload the data. Ask the user to perform interactive login themselves.
Do not guess a validation model URL or treat geometry repair as proof of conformance.
Inspect the completed report and its errors/warnings; job completion only means the
checks ran, not that the input passed. Explain any unavailable or expired results.

## Usage statistics

The authenticated [usage-statistics API](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/statistiques/)
reports requests and transferred bytes over a period. Producers and users have different
scopes, such as offerings, datastores, permissions and keys. Consult the
[API schema](https://data.geopf.fr/api/stats/swagger-ui/index.html)
and account rights before choosing a scope or aggregation period. This is service-usage
reporting, not zonal statistics or analysis of geographic attributes.

## Access and operational precautions

- Public discovery is not permission to access all resources. Check restrictions and
  licence/attribution requirements for the chosen dataset.
- Extraction, standards validation and usage statistics require authentication. Other operations can
  have different public/authenticated quotas; read the current guide. Do not imply that
  every API requires an account or that every API is anonymously accessible.
- Do not request credentials in chat, put tokens in URLs or save them in tracked files.
  Use the user's existing approved credential mechanism; otherwise stop authenticated
  operations and explain how the user can prepare access.
- Before an upload or job submission, ensure that the user's request covers sending
  those data to that service; a request for an overview does not. Use existing
  authorization when it already covers the operation.
- Keep requests bounded, respect current [rate limits](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/limites-d-usage/)
  and service-specific concurrency limits, and handle
  HTTP 429 with the advertised retry delay. Never bypass quotas by adding parallelism.
  Report HTTP, API and parsing failures rather than substituting empty successful data.
- For operations that create jobs, confirm their status before retrying a submission.
  Respect retention limits and verify results before reporting completion.
