# geopf-routing

## RTE-01 — Pedestrian route

> Calcule avec la Géoplateforme un itinéraire piéton entre les coordonnées longitude
> 2,337306, latitude 48,849319 et longitude 2,367776, latitude 48,852891. Enregistre un
> GeoJSON dans `output/` et indique la distance en mètres, la durée en secondes et les
> éventuels décalages des extrémités par rapport aux points demandés.

**Expected skill:** `geopf-routing`.

**Expected result:** a GeoJSON FeatureCollection holding one LineString route in central
Paris, with a positive distance of a few kilometres and a positive duration.
`test_live_enrichment.py` runs a comparable route request.

- [ ] discovers the resource and the pedestrian profile from the service capabilities
- [ ] states the distance and time units returned by the service, and converts them if needed
- [ ] wraps the route geometry in a valid FeatureCollection
- [ ] measures the gap between each requested point and the route end, in metres
- [ ] keeps the resource and its version in the output or the report

## RTE-02 — Arrival area

> Produis un GeoJSON des lieux permettant de rejoindre à pied le point de longitude
> 2,337306 et latitude 48,849319 en cinq minutes, avec la Géoplateforme. Enregistre le
> résultat dans `output/` et précise les paramètres de calcul.

**Expected skill:** `geopf-routing`.

**Expected result:** a valid Polygon or MultiPolygon isochrone around the point, computed
in the arrival direction for 300 seconds.

- [ ] uses an isochrone with `direction=arrival`, not the default departure
- [ ] uses `costType=time` with 300 seconds, or explicit equivalent units
- [ ] writes a valid, non-empty Polygon or MultiPolygon
- [ ] does not substitute a circular buffer for the network calculation
- [ ] reports the resource, profile, direction, cost and units

## RTE-N1 — Negative: geometric buffer

> Explique comment créer un tampon géométrique de 500 mètres autour de points locaux
> déjà en EPSG:2154, sans utiliser un réseau routier ou un service distant.

**Expected skill:** `geopandas-vector-analysis` or local vector tools, not `geopf-routing`.

- [ ] uses a metric buffer in EPSG:2154
- [ ] makes no Navigation API request
