#!/usr/bin/env python3
"""Split UTF-8 CSV records into bounded, BOM-prefixed uploads (standard library only)."""

import argparse
import csv
import io
from pathlib import Path

BOM = b"\xef\xbb\xbf"


def encode_record(row):
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow(row)
    return buffer.getvalue().encode("utf-8")


def split_csv(source, output_dir, *, max_rows=100_000, max_bytes=49_000_000, delimiter=","):
    """Return chunk paths; refuse existing output directories to prevent stale uploads.

    Limits include the repeated header and BOM. Output uses comma-separated CSV even
    when a different input delimiter is supplied. A failed run may leave partial chunks;
    the caller must not upload them unless this function completes successfully.
    """
    if max_rows < 1 or max_bytes < 1:
        raise ValueError("max_rows and max_bytes must be positive")
    output_dir = Path(output_dir)
    with Path(source).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter, strict=True)
        header = next(reader, None)
        if not header or not any(header):
            raise ValueError("CSV needs a non-empty header")
        prefix = BOM + encode_record(header)
        if len(prefix) >= max_bytes:
            raise ValueError("CSV header exceeds the byte limit")
        output_dir.mkdir(parents=True, exist_ok=False)
        paths = []
        chunk = None
        row_count = byte_count = 0
        try:
            for record_number, row in enumerate(reader, start=1):
                if not row:  # Ignore blank physical lines, not records of empty fields.
                    continue
                if len(row) != len(header):
                    raise ValueError(f"Record {record_number}: wrong number of columns")
                payload = encode_record(row)
                if len(prefix) + len(payload) > max_bytes:
                    raise ValueError(f"Record {record_number} exceeds the byte limit")
                if chunk is None or row_count >= max_rows or byte_count + len(payload) > max_bytes:
                    if chunk is not None:
                        chunk.close()
                    path = output_dir / f"chunk_{len(paths) + 1:06d}.csv"
                    chunk = path.open("xb")
                    paths.append(path)
                    chunk.write(prefix)
                    row_count, byte_count = 0, len(prefix)
                chunk.write(payload)
                row_count += 1
                byte_count += len(payload)
        finally:
            if chunk is not None:
                chunk.close()
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path, help="New directory for upload chunks")
    parser.add_argument("--max-rows", type=int, default=100_000)
    parser.add_argument("--max-bytes", type=int, default=49_000_000)
    parser.add_argument("--delimiter", default=",")
    args = parser.parse_args()
    try:
        paths = split_csv(args.source, args.output_dir, max_rows=args.max_rows,
                          max_bytes=args.max_bytes, delimiter=args.delimiter)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        parser.exit(1, f"Error: {exc}. Do not upload partial chunks from this run.\n")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
