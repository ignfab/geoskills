#!/usr/bin/env python3
"""Inspect one saved Download API Atom page; no network calls or file downloads."""
import argparse
import json
import xml.etree.ElementTree as ET

ATOM = "{http://www.w3.org/2005/Atom}"
GPF = "{https://data.geopf.fr/annexes/ressources/xsd/gpf_dl.xsd}"


def inspect_feed(path):
    root = ET.parse(path).getroot()
    if root.tag != ATOM + "feed":
        raise ValueError("Expected an Atom feed, not HTML or an exception")
    page, size, total = (int(root.attrib[GPF + key])
                         for key in ("page", "pagesize", "totalentries"))
    if page < 1 or not 1 <= size <= 50 or total < 0:
        raise ValueError("Invalid pagination metadata")
    entries = []
    for entry in root.findall(ATOM + "entry"):
        identifier = entry.findtext(ATOM + "id")
        if not identifier:
            raise ValueError("Entry has no identifier")
        entries.append({"id": identifier, "title": entry.findtext(ATOM + "title"),
                        "links": [dict(link.attrib) for link in entry.findall(ATOM + "link")]})
    if len(entries) > size or len({e['id'] for e in entries}) != len(entries):
        raise ValueError("Duplicate entries or page larger than advertised")
    expected = min(size, max(0, total - (page - 1) * size))
    if len(entries) != expected:
        raise ValueError("Truncated or inconsistent catalogue page")
    return {"page": page, "page_size": size, "total": total,
            "next_page": page + 1 if page * size < total else None,
            "entries": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feed")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_feed(args.feed), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        parser.exit(2, f"Cannot inspect feed: {exc}\n")


if __name__ == "__main__":
    main()
