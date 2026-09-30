# Contributing to geoskills

Conventions for adding or editing a skill in this repository.

## Layout

One directory per skill, under `skills/`:

```
skills/<skill-name>/
├── SKILL.md      # agent-facing instructions (required)
├── README.md     # human-facing documentation
└── references/   # long-form documentation, loaded on demand
    └── *.md
```

`<skill-name>` is lowercase with hyphens, and matches the `name` in the frontmatter.

Keeping skills under `skills/` matters for discovery: the
[Vercel Skills CLI](https://github.com/vercel-labs/skills) scans the repository root only
one level deep, whereas `skills/` is a known container walked up to three levels. It also
keeps the root free for `docs/`, `templates/` or `examples/`.

## SKILL.md

Required YAML frontmatter:

```yaml
---
name: geopf-wfs-download
description: Downloads WFS data from the French Géoplateforme ... Use when the user wants to ...
---
```

- `name` and `description` are both **required** — a `SKILL.md` missing either is silently
  skipped by the CLI.
- `description` states *what the skill does* and *when to use it*. It is the only thing the
  agent reads before deciding to load the skill, so it carries the trigger words.
- Keep `SKILL.md` short: the endpoint or entry command, the minimal syntax, and the two or
  three commands covering most needs. Everything longer goes to `references/` and is linked
  from a `## References` section.

## Language

Skills are written **in English**, including `name`, `description` and the body. The tools
covered (GDAL, OpenLayers, WFS) are international even when the data is French.

French discoverability is handled in two places, and nowhere else:

- the `description` frontmatter, which seeds the French terms a user is likely to type
  (`télécharger`, `couche`, `carte`, `Géoplateforme`);
- the `Résumé (FR)` section of the root `README.md`.

## Checklist for a new skill

- [ ] `skills/<skill-name>/SKILL.md` with `name` + `description` in the frontmatter
- [ ] `description` mentions when to use the skill, with French trigger terms
- [ ] long-form content moved to `references/` and linked from `SKILL.md`
- [ ] `skills/<skill-name>/README.md` with requirements, install command and contents
- [ ] entry added to the `Skills` table of the root `README.md`
- [ ] `npx skills add <path-to-this-repo>` lists the skill without a warning

The first, third and last of these are enforced in CI: the *Validate skills* workflow runs
[.github/validate-skills.py](.github/validate-skills.py), which checks that every
`skills/**/SKILL.md` has a non-empty `name` and `description` and that `name` matches its
directory.
