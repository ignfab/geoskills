# Interactive HTML

## Lean vector map

Folium writes an HTML/Leaflet map without a web build pipeline. Prefer it for small local
vector results needing zoom, pan, layer visibility and selected attributes. Use the helper
with `--formats html`, or `--formats png html` to keep a static companion. GeoPandas and
Folium are enough for a uniform-colour HTML; numeric colour scales also need Matplotlib.

```bash
python3 scripts/render_vector.py areas.geojson output/web-map \
  --title 'Study areas' --source-note 'Source: supplied data; edition unknown' \
  --formats html --tooltip id label
```

Use inspected attribute names. The helper transforms geometry to longitude/latitude
EPSG:4326, keeps string IDs, HTML-escapes selected tooltip strings and embeds only those
fields plus an internal display colour. It uses `tiles=None`, canvas rendering and circle
markers; no popup, Bootstrap, jQuery or icon-library assets are needed for this route.
Only Leaflet JS/CSS are retained from the installed Folium version's declared assets.
The helper rejects polar/antimeridian extents that this simple Web Mercator view cannot
represent reliably. Simplify/clip a checked display copy before embedding a large layer.

The [Folium reference](https://python-visualization.github.io/folium/latest/reference.html)
documents `tiles=None`, `prefer_canvas` and `fit_bounds`; note that map bounds use
latitude/longitude pairs while GeoJSON coordinates use longitude/latitude.

## Dependencies and offline claims

An HTML with embedded GeoJSON can still require internet access for Leaflet JS/CSS.
`report.json` lists the actual URLs; it marks the helper output as **not offline**.
No tiles are used by default. Add a basemap only if it aids the message and was requested:
discover the provider, keep its attribution and document remote access. Do not embed
tokens or silently replace unavailable background data with a different source.

If a fully offline map is required, use already available local Leaflet assets with their
licence/attribution, copy them into a delivery bundle and change its resource paths. Test
the moved bundle with networking disabled, including CSS image dependencies when used.
Do not claim `tiles=None` alone makes a map offline. If the required assets/browser are
unavailable, explain that limitation and deliver a verified static companion where useful.
The helper does not install or download these assets automatically.

## Browser checks

Open the delivered HTML, allow its declared assets only as appropriate, and inspect
resource/console errors. Confirm the intended extent and feature count, then zoom, pan,
toggle the feature layer and inspect a tooltip including a leading-zero ID and missing
value if present. Check that unselected attributes were not embedded. Inspect at the
intended viewport size for title/caption overlap. Use a network-disabled reload before
claiming an offline bundle. File existence or matching the word `Leaflet` is not a browser
test. Publishing/hosting is a separate user request, not part of creating this file.
