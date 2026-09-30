# Bulk geocoding from CSV

`POST https://data.geopf.fr/geocodage/search/csv` (and `/reverse/csv`) takes a
`multipart/form-data` body and returns a CSV file.

## Limits

- UTF-8 file, at most **50 MB or 200,000 rows** per request.
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

The input columns are kept, followed by:

`longitude`, `latitude`, `result_score`, `result_score_next`, `result_label`, `result_type`,
`result_id`, `result_banId`, `result_housenumber`, `result_name`, `result_street`,
`result_postcode`, `result_city`, `result_context`, `result_citycode`, `result_oldcitycode`,
`result_oldcity`, `result_district`, `result_status`.

- `result_status` is `ok` when a candidate was found, `not-found` when none was, and
  `skipped` when the query text is empty.
- `result_score_next` is the score of the second candidate. When it is close to
  `result_score`, the match is ambiguous.

## Examples

Address split across several columns, filtered by postcode, keeping only a few output columns:

```bash
curl -s -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv \
  -F columns=adresse -F columns=ville \
  -F postcode=cp \
  -F result_columns=longitude -F result_columns=latitude \
  -F result_columns=result_label \
  -F result_columns=result_score \
  -F result_columns=result_citycode \
  -o adresses_geocodees.csv
```

When you use `result_columns`, list `longitude` and `latitude` in it too. Otherwise the
output has no coordinates.

Reverse geocoding of a CSV file with `lon` and `lat` columns:

```bash
curl -s -X POST https://data.geopf.fr/geocodage/reverse/csv \
  -F data=@points.csv \
  -o points_adresses.csv
```

## Checking quality

Count the rows that are poorly matched or not found:

```bash
python3 - <<'PY'
import csv
rows = list(csv.DictReader(open("adresses_geocodees.csv", encoding="utf-8")))
bad = [r for r in rows if r["result_status"] != "ok" or float(r["result_score"] or 0) < 0.5]
print(f"{len(bad)} / {len(rows)} rows need review")
PY
```

## Converting to a spatial file

```bash
ogr2ogr -f GPKG adresses.gpkg adresses_geocodees.csv \
  -oo X_POSSIBLE_NAMES=longitude -oo Y_POSSIBLE_NAMES=latitude \
  -a_srs EPSG:4326 -nln adresses
```

## Splitting a large file

Split the file into 100,000-row chunks and repeat the header in each one:

```bash
tail -n +2 big.csv | split -l 100000 - chunk_
for f in chunk_*; do
  { head -1 big.csv; cat "$f"; } > "$f.csv" && rm "$f"
  curl -s -X POST https://data.geopf.fr/geocodage/search/csv \
    -F data=@"$f.csv" -F columns=adresse -F postcode=cp -o "$f.out.csv"
done
```

To merge the results, keep the header of the first file only.
