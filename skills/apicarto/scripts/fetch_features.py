#!/usr/bin/env python3
"""Fetch every page of an API Carto query into one GeoJSON file (standard library only)."""
import argparse
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://apicarto.ign.fr/api"
GEOMETRY_TYPES = {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}
LONLAT_CRS = {"urn:ogc:def:crs:OGC:1.3:CRS84", "urn:ogc:def:crs:EPSG::4326", "EPSG:4326", "OGC:CRS84"}


def load_geometry(path):
    """Return one GeoJSON geometry in longitude/latitude from a geometry, Feature or collection."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("The geometry file is not a GeoJSON object")
    crs = (data.get("crs") or {}).get("properties", {}).get("name")
    if crs and crs not in LONLAT_CRS:
        raise ValueError(f"Geometry CRS {crs} is not longitude/latitude; reproject to EPSG:4326")
    if data.get("type") == "FeatureCollection":
        if len(data.get("features", [])) != 1:
            raise ValueError("The geometry file must contain exactly one feature")
        data = data["features"][0]
    if data.get("type") == "Feature":
        data = data.get("geometry") or {}
    if data.get("type") not in GEOMETRY_TYPES:
        raise ValueError("Expected a GeoJSON Point, LineString or Polygon geometry")
    positions = list(_positions(data["coordinates"]))
    if not positions or any(not (-180 <= x <= 180 and -90 <= y <= 90) for x, y, *_ in positions):
        raise ValueError("Coordinates are not longitude/latitude in degrees")
    return data, len(positions)


def _positions(coordinates):
    if coordinates and isinstance(coordinates[0], (int, float)):
        yield coordinates
    else:
        for item in coordinates:
            yield from _positions(item)


def fetch_page(url, params, geometry, timeout):
    if geometry is None:
        request = Request(url + "?" + urlencode(params))
    else:
        body = json.dumps(dict(params, geom=geometry)).encode("utf-8")
        request = Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as error:
        raise ValueError(f"HTTP {error.code}: {_message(error.read())}") from None
    except URLError as error:
        raise ValueError(f"Service unreachable: {error.reason}") from None
    try:
        page = json.loads(raw)
    except ValueError:
        raise ValueError(f"Response is not JSON: {_message(raw)}") from None
    if not isinstance(page, dict) or page.get("type") != "FeatureCollection":
        raise ValueError(f"Response is not a FeatureCollection: {_message(raw)}")
    if not isinstance(page.get("features"), list):
        raise ValueError("FeatureCollection without a features list")
    return page


def _message(raw):
    text = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
        text = json.dumps(data.get("message", data), ensure_ascii=False)
    except (ValueError, AttributeError):
        pass
    return " ".join(text.split())[:300]


def fetch_all(endpoint, output, params=(), geometry_path=None, *, page_size=1000,
              max_features=50_000, base_url=BASE_URL, timeout=120):
    if not re.fullmatch(r"[a-z0-9-]+(/[a-z0-9-]+)+", endpoint):
        raise ValueError("Endpoint must look like cadastre/parcelle or nature/natura-habitat")
    if not 1 <= page_size <= 1000 or max_features < 1:
        raise ValueError("Page size must be between 1 and 1000, and the feature cap positive")
    query = {}
    for item in params:
        key, sep, value = item.partition("=")
        if not sep or not key or key in query:
            raise ValueError(f"Invalid or repeated parameter: {item!r}")
        if key in {"geom", "_limit", "_start"}:
            raise ValueError(f"{key} is set by this script")
        query[key] = value
    geometry, vertices = load_geometry(geometry_path) if geometry_path else (None, 0)
    url = base_url.rstrip("/") + "/" + endpoint
    features, ids, matched, pages = [], set(), None, 0
    # The service's own next links point to http://localhost; pages are requested by _start.
    while True:
        page = fetch_page(url, dict(query, _limit=page_size, _start=len(features)), geometry, timeout)
        pages += 1
        batch = page["features"]
        returned = page.get("numberReturned")
        if returned is not None and returned != len(batch):
            raise ValueError("numberReturned differs from the features of the page")
        if pages == 1:
            matched = page.get("numberMatched")
            if isinstance(matched, int) and matched > max_features:
                raise ValueError(f"{matched} features match; narrow the query or raise the cap")
        elif page.get("numberMatched") != matched:
            raise ValueError("numberMatched changed between pages; the source changed during paging")
        for feature in batch:
            identifier = feature.get("id")
            if identifier is None or identifier in ids:
                raise ValueError(f"Missing or repeated feature id {identifier!r} across pages")
            ids.add(identifier)
        features.extend(batch)
        if len(batch) < page_size or (isinstance(matched, int) and len(features) >= matched):
            break
        if len(features) >= max_features:
            raise ValueError("Feature cap reached before the last page")
    if isinstance(matched, int) and len(features) != matched:
        raise ValueError(f"Fetched {len(features)} features but numberMatched is {matched}")
    # Exclusive creation keeps an earlier result instead of overwriting it.
    with Path(output).open("x", encoding="utf-8") as handle:
        json.dump({"type": "FeatureCollection", "features": features}, handle, ensure_ascii=False)
    result = {"endpoint": endpoint, "params": query, "geometry_vertices": vertices,
              "page_size": page_size, "pages": pages, "number_matched": matched,
              "features": len(features), "output": str(output),
              "status": "complete" if isinstance(matched, int) else "count_not_reported"}
    if not features:
        # Swapped coordinates or an area outside France also return an empty collection.
        result["warning"] = ("No feature matched: check that the query lies inside the module's "
                             "coverage and that coordinates are in longitude, latitude order")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("endpoint", help="Module path, such as cadastre/parcelle")
    parser.add_argument("output", help="New GeoJSON file; an existing file is never replaced")
    parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE",
                        help="Query parameter, such as code_insee=94067 (repeatable)")
    parser.add_argument("--geometry", help="GeoJSON file with one longitude/latitude geometry")
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--max-features", type=int, default=50_000)
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()
    try:
        result = fetch_all(args.endpoint, args.output, args.param, args.geometry,
                           page_size=args.page_size, max_features=args.max_features,
                           base_url=args.base_url)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Cannot fetch {args.endpoint}: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
