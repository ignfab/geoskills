# Model, edition, format and service

Keep four independent statements in the answer:

| Evidence | What it establishes |
| --- | --- |
| Model number plus document revision | Which definitions were consulted |
| Dataset edition/date and territory | Which actual delivery is being discussed |
| Format metadata | Actual layer/column names, types and geometry encoding |
| Dated WFS metadata | What that service advertises now |

The subset records only explicitly checked PostgreSQL/Shapefile column mappings. For
GeoPackage, SQL dumps or WFS, inspect actual metadata; do not assume a lowercase name,
uppercase alias, namespace or type just because the product is called BD TOPO.

## Optional live WFS metadata

Use a public endpoint identified by the user or official service documentation. For the
Géoplateforme WFS entry point, inspect capabilities before choosing a typename:

```bash
curl --fail --show-error --get 'https://data.geopf.fr/wfs/ows' --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' --data-urlencode 'request=GetCapabilities' --output capabilities.xml
curl --fail --show-error --get 'https://data.geopf.fr/wfs/ows' --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' --data-urlencode 'request=DescribeFeatureType' --data-urlencode "typeNames=$DISCOVERED_TYPENAME" --output schema.xsd
```

Choose unused output paths before running these commands. Set `DISCOVERED_TYPENAME` from
the capabilities, not the bundled class names. Validate XML roots, namespaces and service
exceptions even after HTTP 200. Inspect actual element names, types and geometry properties.
Capabilities establish advertised CRS; DescribeFeatureType establishes fields. Neither
proves that all records are populated, nor that service update dates equal product editions.
No GetFeature request is needed here. If offline/unavailable, cite the static snapshot and
mark service-specific names unverified. Hand off actual extraction to `geopf-wfs-download`.
