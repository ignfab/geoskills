# bdtopo-schema-guide

**Family:** [1. Discover and select](../README.md).

Version-aware BD TOPO semantics for buildings and roads, with traceable IGN sources.

## Requirements

No GIS tools or network for bundled reference lookup. Optional helper uses Python 3's
standard library. Never install software from the agent; Markdown remains usable without
Python. Online metadata checks can use existing curl (user-run Debian/Ubuntu installation:
`sudo apt install curl`).

## Install

```bash
npx skills add ignfab/geoskills --skill bdtopo-schema-guide
```

## Contents

- [SKILL.md](SKILL.md): version selection, lookup and answer validation.
- [Sources](references/sources-and-versions.md), [classes](references/themes-and-classes.md),
  [attributes](references/attributes-and-enums.md), [formats/services](references/formats-and-services.md).
- [Versioned JSON subset](references/schema-3.5-2026-07.json) and [offline lookup](scripts/lookup.py).
- [French scenarios](../../../tests/bdtopo-schema-guide.md).

This is a small documented subset, not a full schema validator or migration tool. Unknown
versions/fields return `unverified`, never guessed mappings. Source PDFs are referenced,
not redistributed. Model 3.5 and document revision July 2026 are separate from delivery dates.
