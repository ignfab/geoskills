# geopf-routing scenarios

## RTE-01 — Pedestrian route

> Calcule avec la Géoplateforme un itinéraire piéton entre les coordonnées longitude
> 2,337306, latitude 48,849319 et longitude 2,367776, latitude 48,852891. Enregistre un
> GeoJSON dans `output/` et indique la distance en mètres, la durée en secondes et les
> éventuels décalages des extrémités par rapport aux points demandés.

Expected: resource/profile discovery, explicit units, route geometry wrapped as a
FeatureCollection, positive plausible metrics, network snapping checked in metres.

## RTE-02 — Arrival area

> Produis un GeoJSON des lieux permettant de rejoindre à pied le point de longitude
> 2,337306 et latitude 48,849319 en cinq minutes, avec la Géoplateforme. Enregistre le
> résultat dans `output/` et précise les paramètres de calcul.

Expected: isochrone, `arrival`, `costType=time`, 300 seconds or equivalent explicit units;
valid polygon/multipolygon, no circular buffer substituted, resource version retained.

## RTE-N1 — Geometric buffer

> Explique comment créer un tampon géométrique de 500 mètres autour de points locaux
> déjà en EPSG:2154, sans utiliser un réseau routier ou un service distant.

Expected: `geopandas-basics` or local vector tools; no navigation API or `geopf-routing` load.
