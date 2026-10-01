# Bulk geocoding from CSV

Service limits and parameters checked on 2026-09-30.

`POST https://data.geopf.fr/geocodage/search/csv` (and `/reverse/csv`) takes a
`multipart/form-data` body and returns a CSV file.

## Limits

- UTF-8 file; stay below **50 MB and 200,000 records** per request.
- For a larger file, split it into several files (see below) and send them one after the other.

## Form fields

| Field | Description |
|-------|-------------|
| `data` | The CSV file (`-F data=@file.csv`). Required |
| `columns` | Column(s) joined to build the query text. Repeat it once per column. If you leave it out, **every** column is joined, which is rarely what you want |
| `indexes` | `address`, `poi` or `parcel`. Repeat it to use several indexes. Note the plural: `indexes`, not `index` |
| `postcode`, `citycode` | Name of the column holding a postcode or INSEE code, used as a filter |
| `type` | Name of the column holding the accepted result type |
| `lon`, `lat` | Names of the columns holding a point that favours close candidates. For `/reverse/csv`, the columns to reverse-geocode |
| `category` | Name of the column holding a POI category |
| `departmentcode`, `municipalitycode`, `section`, `sheet`, `number`, ... | Names of the columns used for parcel filters |
| `result_columns` | Output columns to keep (repeat it). By default, all of them are kept |

Filters take a **column name**, not a value. `-F postcode=code_postal` means "filter each row
by the value in its `code_postal` column".

## Output columns

The input columns are generally kept, followed by result columns. In forward geocoding,
existing input columns named `longitude` or `latitude` are overwritten: rename them first
if their original values must be preserved. Common result columns include:

`longitude`, `latitude`, `result_score`, `result_score_next`, `result_label`, `result_type`,
`result_id`, `result_banId`, `result_housenumber`, `result_name`, `result_street`,
`result_postcode`, `result_city`, `result_context`, `result_citycode`, `result_oldcitycode`,
`result_oldcity`, `result_district`, `result_status`.

- `result_status` is `ok` when a candidate was found, `not-found` when none was, and
  `skipped` for missing or invalid query parameters, and `error` for a server-side error.
  An HTTP 200 response can still contain individual rows with `error` status.
- `result_score_next` is the score of the second candidate. When it is close to
  `result_score`, the match is ambiguous.

## Examples

Address split across several columns, filtered by postcode, keeping only a few output columns:

```bash
curl -fsS --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv \
  -F columns=adresse -F columns=ville \
  -F postcode=cp \
  -F result_columns=longitude -F result_columns=latitude \
  -F result_columns=result_label \
  -F result_columns=result_score -F result_columns=result_status \
  -F result_columns=result_type -F result_columns=result_score_next \
  -F result_columns=result_citycode \
  -o adresses_geocodees.csv
```

When you use `result_columns`, list `longitude` and `latitude` in it too. Otherwise the
output has no coordinates. Keep `result_status` and the quality fields needed below too.

Reverse geocoding of a CSV file with `lon` and `lat` columns:

```bash
curl -fsS --max-time 300 -X POST https://data.geopf.fr/geocodage/reverse/csv \
  -F data=@points.csv \
  -o points_adresses.csv
```

## Checking quality

Count the rows that are poorly matched or not found:

```bash
python3 - <<'PY'
import csv
with open("adresses_geocodees.csv", encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    required = {"result_status", "result_score"}
    if not required.issubset(reader.fieldnames or []):
        raise SystemExit("Missing quality columns; keep result_status and result_score")
    rows = list(reader)
bad = [r for r in rows if r["result_status"] != "ok" or float(r["result_score"] or 0) < 0.5]
print(f"{len(bad)} / {len(rows)} rows need review")
PY
```

This score check is a first pass. Also compare municipality and result type against each
query, and review close first/second scores. A high score is not proof of a correct match.

## Converting to a spatial file

```bash
ogr2ogr -f GPKG adresses.gpkg adresses_geocodees.csv \
  -oo X_POSSIBLE_NAMES=longitude -oo Y_POSSIBLE_NAMES=latitude \
  -a_srs EPSG:4326 -nln adresses
```

## Encoding and splitting uploads

If accented input is echoed as mojibake (for example `Saint-MandÃ©`), the service may have
misdetected the encoding. Retry a small UTF-8 copy with a BOM and compare the echoed
fields. Do not modify the original file or interpret encoding failures as absent addresses.

Use [../scripts/split_csv.py](../scripts/split_csv.py) to prepare UTF-8 CSV uploads. It
preserves quoted commas, embedded newlines, leading zeros and headers, and adds a UTF-8
BOM. It defaults to 100,000 records and 49 MB **including the header and BOM** per chunk.
It requires Python 3 and refuses an existing output directory. Run from the skill directory
(or resolve the script relative to this reference):

```bash
python3 scripts/split_csv.py /path/to/big.csv /path/to/uploads
# For semicolon-separated input, add: --delimiter ';'
```

Only upload after the splitter exits successfully. On failure, its directory may contain
partial chunks. Use a separate results directory so output files cannot become new inputs:

```bash
mkdir -p /path/to/results
for f in /path/to/uploads/chunk_*.csv; do
  [ -f "$f" ] || continue
  curl -fsS --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
    -F data=@"$f" -F columns=adresse -F postcode=cp \
    -o "/path/to/results/$(basename "$f")" || break
done
```

Check every response and the total record count before merging with a CSV reader/writer.
Require matching headers and retain input IDs; a failed or missing chunk is an incomplete
job. For recurrent larger jobs, the API also provides asynchronous batch processing;
see the [official guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/).
