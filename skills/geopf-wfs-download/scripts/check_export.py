#!/usr/bin/env python3
"""Check a GeoPackage export against WFS hits collected with the same filter."""
import argparse
import json
from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET


def matched(path):
    root = ET.parse(path).getroot()
    if root.tag != "{http://www.opengis.net/wfs/2.0}FeatureCollection":
        raise ValueError("Expected a WFS 2.0 FeatureCollection, not an exception or HTML")
    value = root.get("numberMatched")
    if value == "unknown":
        return None
    if value is None or not value.isdecimal():
        raise ValueError("Missing or invalid numberMatched")
    return int(value)


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def check_export(path, layer, id_field, before, after):
    expected_before, expected_after = matched(before), matched(after)
    # Read-only URI prevents a typo from creating an empty database.
    with sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True) as db:
        layers = {r[0] for r in db.execute(
            "SELECT table_name FROM gpkg_contents WHERE data_type='features'")}
        if layer not in layers:
            raise ValueError("Layer is not a GeoPackage feature table")
        fields = {r[1] for r in db.execute(f"PRAGMA table_info({quote(layer)})")}
        if id_field not in fields:
            raise ValueError("The discovered source identifier is absent from the export")
        field = quote(id_field)
        count, distinct, missing = db.execute(
            f"SELECT count(*), count(DISTINCT {field}), "
            f"coalesce(sum({field} IS NULL OR trim(cast({field} AS TEXT))=''),0) "
            f"FROM {quote(layer)}").fetchone()
        duplicates = db.execute(
            f"SELECT count(*) - count(DISTINCT {field}) FROM {quote(layer)} "
            f"WHERE {field} IS NOT NULL AND trim(cast({field} AS TEXT))<>''").fetchone()[0]
    issues = []
    if missing:
        issues.append("missing_source_ids")
    if duplicates:
        issues.append("duplicate_source_ids")
    if expected_before is None or expected_after is None:
        issues.append("unknown_expected_count")
    elif expected_before != expected_after:
        issues.append("source_count_changed")
    elif count != expected_before:
        issues.append("count_mismatch")
    return {"layer": layer, "source_id_field": id_field, "count": count,
            "distinct_ids": distinct, "missing_ids": missing,
            "expected_before": expected_before, "expected_after": expected_after,
            "status": "consistent" if not issues else "unverified", "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export")
    parser.add_argument("--layer", required=True)
    parser.add_argument("--id-field", required=True)
    parser.add_argument("--hits-before", required=True)
    parser.add_argument("--hits-after", required=True)
    args = parser.parse_args()
    try:
        result = check_export(args.export, args.layer, args.id_field,
                              args.hits_before, args.hits_after)
    except (ValueError, OSError, sqlite3.Error, ET.ParseError) as exc:
        parser.exit(2, f"Cannot verify export: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "consistent" else 1


if __name__ == "__main__":
    raise SystemExit(main())
