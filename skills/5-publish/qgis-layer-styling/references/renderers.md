# Rendering specifications

The helper's `--spec` is a local JSON file. All names below are examples: inspect the
layer first. Sizes mean marker diameter, line width or polygon stroke width. Units are
`mm` (default, physical size) or `map` (map units; do not assume metres). Opacity is 0–1.

## Single symbol

For a red polygon outline without fill:

```json
{"mode":"single","color":"#ff0000","outline":"#ff0000","no_fill":true,"size":0.4,"units":"mm","opacity":1}
```

For points/lines, use `color`, `size`, `units` and `opacity`. Polygon fill uses `color`
unless `no_fill` is true. No-fill differs from setting overall opacity to zero, which
also hides the outline.

## Categorized

```json
{"mode":"categorized","field":"category","colors":["#4575b4","#d73027","#66bd63"],"fallback":"#999999","units":"mm"}
```

Categories come from actual non-null distinct values in stable order. The final default
category covers **both null and previously unseen values**; its label is `Missing / other`.
Report that combined policy, especially when applying the style to another edition.
The palette cycles when there are more categories than colors; inspect legibility and
provide enough distinct colors where distinctions matter. More than 100 categories is
rejected; choose a user-approved grouping outside this helper rather than hide categories.

## Graduated

```json
{"mode":"graduated","field":"height","breaks":[0,10,20,30],"colors":["#fee8c8","#fdbb84","#e34a33"],"units":"mm"}
```

Use numeric metadata, not a field-name guess. Breaks include lower/upper endpoints and
must strictly increase and cover all observed finite values. QGIS assigns a shared break
to the first matching range (first range includes its lower endpoint; following intervals
behave as `(lower, upper]`). Test exact boundary values; never create gaps like 10–10.1.
Null values are **not rendered** by this graduated helper; report their count explicitly.
Infinite values are rejected. An all-null or constant field needs a different stated
choice, such as a single symbol, rather than degenerate class boundaries.

For equal intervals, compute `minimum + i * (maximum-minimum)/classes` from inspected
finite values. For quantiles, use a documented interpolation method, deduplicate tied
breaks, and report the reduced class count. The helper accepts the resulting explicit
breaks; its report must be accompanied by the chosen method and actual class frequencies.
Do not infer meaningful thresholds merely from a color ramp.
