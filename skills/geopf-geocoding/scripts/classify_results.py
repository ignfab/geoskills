#!/usr/bin/env python3
"""Classify geocoded CSV rows without dropping input rows or changing their fields."""
import argparse
import csv
import json
import math
from pathlib import Path


def score(value):
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) and 0 <= number <= 1 else None


def classify(row, *, min_score, min_margin, city_column=None, accepted_types=()):
    status = row["result_status"]
    if status == "not-found":
        return "unmatched", "not_found"
    reasons = []
    if status != "ok":
        reasons.append("service_" + (status or "missing_status"))
    first, second = score(row["result_score"]), score(row["result_score_next"])
    if first is None:
        reasons.append("invalid_score")
    elif first < min_score:
        reasons.append("low_score")
    if row["result_score_next"].strip() and second is None:
        reasons.append("invalid_second_score")
    elif first is not None and second is not None:
        margin = first - second
        if margin < min_margin and not math.isclose(margin, min_margin, rel_tol=0, abs_tol=1e-12):
            reasons.append("ambiguous_candidates")
    if city_column:
        wanted = row[city_column].strip()
        if not wanted or not row["result_citycode"].strip():
            reasons.append("missing_city_code")
        elif wanted != row["result_citycode"].strip():
            reasons.append("city_mismatch")
    if accepted_types and row["result_type"] not in accepted_types:
        reasons.append("unexpected_match_type")
    for field, lower, upper in (("longitude", -180, 180), ("latitude", -90, 90)):
        try:
            value = float(row[field])
        except (ValueError, TypeError):
            value = math.nan
        if not math.isfinite(value) or not lower <= value <= upper:
            reasons.append("invalid_" + field)
    return ("review", ";".join(reasons)) if reasons else ("accepted", "policy_pass")


def classify_file(source, target, **policy):
    with Path(source).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        required = {"result_status", "result_score", "result_score_next", "longitude", "latitude"}
        if policy.get("city_column"):
            required.update({policy["city_column"], "result_citycode"})
        if policy.get("accepted_types"):
            required.add("result_type")
        if not required.issubset(fields) or len(fields) != len(set(fields)):
            raise ValueError("Missing required columns or duplicate CSV headers")
        if {"review_status", "review_reason"} & set(fields):
            raise ValueError("Review columns already exist; refusing to overwrite them")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("Malformed CSV row width")
    counts = dict.fromkeys(("accepted", "review", "unmatched"), 0)
    # Exclusive creation also protects the input and any previous output.
    with Path(target).open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields + ["review_status", "review_reason"])
        writer.writeheader()
        for row in rows:
            status, reason = classify(row, **policy)
            counts[status] += 1
            writer.writerow(dict(row, review_status=status, review_reason=reason))
    return {"rows": len(rows), "counts": counts, "policy": policy}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("--min-score", type=float, required=True)
    parser.add_argument("--min-margin", type=float, required=True)
    parser.add_argument("--city-column", help="Input column containing expected INSEE codes")
    parser.add_argument("--accepted-type", action="append", default=[])
    args = parser.parse_args()
    if any(not math.isfinite(x) or not 0 <= x <= 1 for x in (args.min_score, args.min_margin)):
        parser.error("Thresholds must be finite numbers between 0 and 1")
    try:
        result = classify_file(args.source, args.target, min_score=args.min_score,
                               min_margin=args.min_margin, city_column=args.city_column,
                               accepted_types=args.accepted_type)
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(2, f"Cannot classify CSV: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
