# Overseas territories (DROM-COM)

Each overseas territory has its own geodetic system. Lambert-93 must not be used outside
mainland France and Corsica.

| Territory | Geographic CRS | Projected CRS (legal) | Vertical system |
|-----------|----------------|-----------------------|-----------------|
| Guadeloupe | RGAF09 (EPSG:5489) | RGAF09 / UTM 20N (EPSG:5490) | Guadeloupe 1988 (EPSG:5757). Les Saintes: IGN 1988 LS (EPSG:5616), Marie-Galante: IGN 1988 MG (EPSG:5617) |
| Saint-Martin | RGAF09 (EPSG:5489) | RGAF09 / UTM 20N (EPSG:5490) | IGN 1988 SM (EPSG:5620) |
| Saint-Barthélemy | RGAF09 (EPSG:5489) | RGAF09 / UTM 20N (EPSG:5490) | IGN 1988 SB (EPSG:5619) |
| Martinique | RGAF09 (EPSG:5489) | RGAF09 / UTM 20N (EPSG:5490) | Martinique 1987 (EPSG:5756) |
| French Guiana | RGFG95 (EPSG:4624) | RGFG95 / UTM 22N (EPSG:2972) | NGG1977 (EPSG:5755) |
| Réunion | RGR92 (EPSG:4627) | RGR92 / UTM 40S (EPSG:2975) | Reunion 1989 (EPSG:5758) |
| Mayotte | RGM04 (EPSG:4470) | RGM04 / UTM 38S (EPSG:4471) | Mayotte 1950 (EPSG:5793) |
| Saint-Pierre-et-Miquelon | RGSPM06 (EPSG:4463) | RGSPM06 / UTM 21N (EPSG:4467) | Danger 1950 (EPSG:5792) |

## Legacy systems

Older datasets may use earlier local systems:

| Territory | Legacy system | Example EPSG |
|-----------|---------------|--------------|
| Guadeloupe, Martinique | RRAF 1991 / UTM 20N (replaced by RGAF09) | 2989 |
| Réunion | Reunion 1947 / TM Reunion (Piton des Neiges / Gauss-Laborde) | 3727 |
| Saint-Pierre-et-Miquelon | Saint-Pierre-et-Miquelon 1950 / UTM 21N | 2987 |

Check the name and extent of any code with `projinfo EPSG:<code>`, and list the available
transformations with `projinfo -s EPSG:<old> -t EPSG:<new> --summary`.

## Multi-territory datasets

A single dataset covering mainland France and the overseas territories (for example the ADMIN
EXPRESS layers of the Géoplateforme WFS) is usually published in EPSG:4326. Keep it in
EPSG:4326 for storage and display. To compute areas or distances, reproject each territory
to its own projected CRS from the table above. For example, the communes of Réunion (region
code `04`):

```bash
ogr2ogr -f GPKG -where "code_insee_de_la_region = '04'" -t_srs EPSG:2975 \
  communes_reunion.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "ADMINEXPRESS-COG.LATEST:commune"
```

Most Géoplateforme WFS layers are served in EPSG:4326, but some layers that cover only one
overseas territory use its local UTM CRS (EPSG:5490, 2975, 4471, ...). Check the CRS with
`ogrinfo -so` before filtering (see the `geopf-wfs-download` skill).
