# geopf-geocoding

## GEO-01 — Geocode one address

> Donne-moi les coordonnées GPS du 73 avenue de Paris à Saint-Mandé.

**Expected skill:** `geopf-geocoding`

**Reference result (live data may change):** lon `2.424573`, lat `48.845726`, label
`73 Avenue de Paris 94160 Saint-Mandé`, score ≈ 0.97, type `housenumber`.

- [ ] calls `https://data.geopf.fr/geocodage/search`, without an API key or another geocoder
- [ ] gives the coordinates in lon/lat order, or says which order it uses
- [ ] reports the score or the result type
- [ ] coordinates are within 0.002° of the reference and citycode is `94067`; an exact
  score or spelling match is not required

## GEO-02 — Geocode a CSV file in bulk

> Géocode le fichier data/adresses.csv (colonnes numero, voie, code_postal, commune) et
> écris le résultat dans output/adresses_geocodees.csv. Signale-moi les lignes douteuses.

**Expected skill:** `geopf-geocoding`

**Expected result:**

| id | Address | Expected |
|----|---------|----------|
| 1 | 73 avenue de Paris, Saint-Mandé | `ok`, 2.424573 / 48.845726, score 0.97 (see known issue) |
| 2 | 8 boulevard du Port, Cergy | `ok`, 2.062821 / 49.031624, score 0.97 |
| 3 | 20 rue de la Paix, Paris (no postcode) | `ok`, `75002`, score 0.96 |
| 4 | 1 place du Capitole, Toulouse | `ok`, 1.444053 / 43.603872, score 0.98 |
| 5 | 36 quai des Orfèvres, Paris | `ok`, score ≈ 0.96 with correctly decoded UTF-8 |
| 6 | 1 rue de Paris, Saint-Denis (97400) | `ok` but type **`street`**: the house number was not found |
| 7 | 12 rue imaginaire des Tests, Nulle-Part | `not-found` |
| 8 | empty row | `skipped` |

- [ ] uses `POST /search/csv` once, not one `/search` call per row
- [ ] passes `columns` once per column, and `postcode=code_postal` (a column name, not a value)
- [ ] if it uses `result_columns`, keeps coordinates, status and the fields used for quality checks
- [ ] preserves all 8 input IDs and the original accented text in the echoed fields
- [ ] flags rows 7 and 8; flags row 6 if its result is still `street`, and explains why
- [ ] treats scores and nearest-address labels as observations, not exact golden values
- [ ] checks for the encoding trap below; if present, retries with a UTF-8 BOM copy,
  preserving the source and not reporting row 1 as an unknown address

**Encoding trap reproduced on 2026-09-30** (documented in the skill's batch reference):
the service guesses the
encoding of the uploaded file and reads this UTF-8 file as Latin-1. "Saint-Mandé" becomes
"Saint-MandÃ©" in the echoed input columns, and row 1 comes back `not-found`. A copy
prefixed with a UTF-8 BOM gives the expected results:

```bash
{ printf '\xef\xbb\xbf'; cat data/adresses.csv; } > output/adresses_bom.csv
```

The skill also provides `scripts/split_csv.py`, which adds a BOM to upload copies.
Do not require the API to keep misdetecting BOM-less files: if encoding detection improves,
the scenario still passes. Row 5 also shows why echoed accents matter even for `ok` results.

## GEO-03 — Reverse-geocode points

> Quelle est l'adresse la plus proche de chacun des points de data/points.csv ?

**Expected skill:** `geopf-geocoding`

**Expected result:**

| id | Point | Nearest address | Distance |
|----|-------|-----------------|----------|
| 1 | 2.4245, 48.8451 | 2b Avenue Pasteur 94160 Saint-Mandé | 57 m |
| 2 | 1.4442, 43.6045 | Rue Ernest Roschach 31000 Toulouse | 36 m |
| 3 | 55.4497, -20.8822 | Rue de Paris 97400 Saint-Denis | 3 m |

- [ ] uses `/reverse` or `POST /reverse/csv`
- [ ] each result is within 1 km of the input; exact labels and distances may change
- [ ] does not swap lon and lat (point 3 is in Réunion; swapped, it would fall in the North
  Atlantic, south of Iceland)

## GEO-04 — Get a cadastral parcel

> Récupère le contour de la parcelle cadastrale D 50 de Saint-Mandé (94067) et
> enregistre-le en GeoJSON dans output/parcelle.geojson.

**Expected skill:** `geopf-geocoding`

**Expected result:** one feature, id `940670000D0050`, geometry of type **Polygon or MultiPolygon**, near
2.4248 / 48.8450.

- [ ] uses `index=parcel` with `departmentcode=94`, `municipalitycode=067`, `section` and
  `number`
- [ ] uses `returntruegeometry=true` **and** moves `truegeometry` into the feature geometry.
  A `Point` geometry in the output is a failure.

## GEO-05 — Find an INSEE code

> Quel est le code INSEE de la commune de Saint-Mandé ?

**Expected skill:** `geopf-geocoding` (optional: answering from memory is acceptable if
correct)

**Expected result:** `94067` (postcode 94160).

- [ ] if the API is used: `type=municipality`

## GEO-N1 — Negative: no geocoding needed

> Convertis data/adresses.csv en fichier Excel dans output/adresses.xlsx.

**Expected skill:** not `geopf-geocoding`.

- [ ] no call to `data.geopf.fr`
