"""Offline, fail-closed lookup in the bundled versioned BD TOPO subset."""
import argparse
import json
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1]/'references/schema-3.5-2026-07.json'


def lookup(version, revision, class_name, field=None, format_name='postgresql'):
    data = json.loads(FIXTURE.read_text())
    source = next(iter(data['sources'].values()))
    unknown = {'status': 'unverified', 'reason': 'Not covered by this curated snapshot; not evidence of absence',
               'requested_version': version, 'requested_revision': revision, 'source': source}
    if version != source['model_version'] or revision != source['document_revision']:
        return dict(unknown, reason='Model version or document revision is unsupported; inspect applicable documentation')
    if format_name not in ('postgresql', 'shapefile') or class_name not in data['classes']:
        return unknown
    cls = data['classes'][class_name]
    if field:
        item = next((value for key, value in cls['fields'].items()
                     if field == value['names'].get(format_name)), None)
        if item is None:
            return unknown
        return {'status': 'documented', 'source': source, 'class': class_name,
                'format': format_name, 'field': item}
    return {'status': 'documented', 'source': source, 'class': cls, 'format': format_name,
            'coverage': data['coverage']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--class', dest='class_name', required=True)
    parser.add_argument('--field')
    parser.add_argument('--format', default='postgresql')
    args = parser.parse_args()
    print(json.dumps(lookup(args.version, args.revision, args.class_name, args.field, args.format), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
