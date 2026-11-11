"""Deterministic single-table summaries. No geometry edits or implicit imputation."""
import argparse
import csv
import json
import math
from pathlib import Path

import pandas as pd


def number(value):
    return float(value) if pd.notna(value) and math.isfinite(float(value)) else None


def summarize(frame, numeric=(), categorical=(), *, source, units=None, ddof=1):
    if ddof not in (0, 1):
        raise ValueError('ddof must be 0 (population) or 1 (sample)')
    selected = list(numeric) + list(categorical)
    if not selected or len(set(selected)) != len(selected):
        raise ValueError('Select distinct numeric and categorical fields')
    if not frame.columns.is_unique:
        raise ValueError('Duplicate column names')
    missing = set(selected) - set(frame.columns)
    if missing:
        raise ValueError(f'Unknown fields: {sorted(missing)}')
    report = {'source': source, 'rows': len(frame), 'pandas': pd.__version__,
              'crs': str(frame.crs) if getattr(frame, 'crs', None) else None,
              'method': {'ddof': ddof, 'quantiles': [0.25, 0.5, 0.75],
                         'interpolation': 'linear', 'frequency_denominator': 'all rows',
                         'missing': 'null/NaN', 'invalid': 'exclude and count text/infinity'},
              'fields': {}, 'warnings': []}
    for field in selected:
        raw = frame[field]
        absent = int(raw.isna().sum())
        item = {'dtype': str(raw.dtype), 'unit': (units or {}).get(field, 'unspecified'),
                'total': len(raw), 'missing': absent,
                'missing_fraction': absent / len(raw) if len(raw) else None}
        if field in numeric:
            if pd.api.types.is_bool_dtype(raw):
                raise ValueError(f'{field}: boolean is not a numeric measure')
            values = pd.to_numeric(raw, errors='coerce').astype(float)
            text = int((raw.notna() & values.isna()).sum())
            infinite = int(values.isin([float('inf'), -float('inf')]).sum())
            valid = values[values.notna() & ~values.isin([float('inf'), -float('inf')])]
            item.update(kind='numeric', valid=len(valid), invalid_text=text, infinite=infinite)
            item.update({key: number(getattr(valid, key)()) for key in ['min', 'max', 'mean', 'median']})
            item['sum'] = number(valid.sum(min_count=1))
            item['std'] = number(valid.std(ddof=ddof)) if len(valid) > ddof else None
            item['quantiles'] = {str(q): number(valid.quantile(q, interpolation='linear'))
                                 for q in report['method']['quantiles']}
            if text or infinite:
                report['warnings'].append(f'{field}: excluded {text} nonnumeric and {infinite} infinite values')
            if not len(valid):
                report['warnings'].append(f'{field}: no finite numeric observations')
        else:
            # Explicit string categories retain leading zeroes; null has its own JSON value.
            values = raw.astype('string')
            counts = values.dropna().value_counts(sort=False).sort_index()
            categories = [{'value': str(value), 'count': int(count),
                           'frequency': int(count) / len(raw)} for value, count in counts.items()]
            if absent:
                categories.append({'value': None, 'count': absent, 'frequency': absent / len(raw)})
            item.update(kind='categorical', valid=len(raw)-absent, categories=categories)
        report['fields'][field] = item
    return report


def write_report(report, output):
    """Create an unused directory; JSON is canonical, CSV is a lossless metric table."""
    encoded = json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)+'\n'
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output/'summary.json').write_text(encoded, encoding='utf-8')
    with (output/'summary.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['field', 'metric', 'value_json'])
        for field, item in report['fields'].items():
            for metric, value in item.items():
                writer.writerow([field, metric, json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)])
        for key in ['source', 'rows', 'pandas', 'crs', 'method', 'warnings']:
            writer.writerow(['', key, json.dumps(report[key], ensure_ascii=False, allow_nan=False, sort_keys=True)])
    lines = ['# Attribute summary', '', f"Source: {report['source']}",
             f"Rows: {report['rows']}; CRS: {report['crs'] or 'not declared'}", '',
             f"Method: {json.dumps(report['method'], sort_keys=True)}", '']
    for field, item in report['fields'].items():
        lines += [f'## {field}', '', '```json', json.dumps(item, ensure_ascii=False, allow_nan=False, indent=2), '```', '']
    lines += ['Warnings: '+ ('; '.join(report['warnings']) or 'none'), '']
    (output/'summary.md').write_text('\n'.join(lines), encoding='utf-8')
    if json.loads((output/'summary.json').read_text()) != report:
        raise ValueError('JSON round-trip failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('output', help='new report directory')
    parser.add_argument('--layer', help='discovered layer name, required for non-CSV input')
    parser.add_argument('--numeric', nargs='*', default=[])
    parser.add_argument('--categorical', nargs='*', default=[])
    parser.add_argument('--ddof', type=int, choices=[0, 1], default=1)
    parser.add_argument('--units', default='{}', help='JSON mapping of field to documented unit')
    args = parser.parse_args()
    if Path(args.source).suffix.lower() == '.csv':
        # Only blank CSV cells are missing; literal NA is a valid identifier/category.
        frame = pd.read_csv(args.source, dtype='string', keep_default_na=False, na_values=[''])
    else:
        import geopandas as gpd
        if not args.layer:
            parser.error('Inspect layers first and supply --layer')
        frame = gpd.read_file(args.source, layer=args.layer)
    result = summarize(frame, args.numeric, args.categorical, source=args.source,
                       units=json.loads(args.units), ddof=args.ddof)
    write_report(result, args.output)
    print(json.dumps({'output': args.output, 'rows': result['rows'], 'warnings': result['warnings']}))


if __name__ == '__main__':
    main()
