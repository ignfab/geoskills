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
covered (GDAL, PROJ, WFS) are international even when the data is French.

French discoverability is handled in two places, and nowhere else:

- the `description` frontmatter, which seeds the French terms a user is likely to type
  (`télécharger`, `couche`, `carte`, `Géoplateforme`);
- the `Résumé (FR)` section of the root `README.md`.

## Agent conduct

A skill instructs an agent that runs commands on the user's machine. Every skill follows
these rules, and states them where they apply:

- **Never install software.** When a tool is missing, `## Prerequisites` gives the install
  command for the user to run; the agent does not run `sudo apt`, `conda` or `pip` itself.
- **No interactive commands.** Do not run a command that waits for input (a login, a setup
  wizard); ask the user to run it.
- **Discover before querying.** Take layer names, field names and CRSs from the service or
  file metadata, not from memory.
- **Validate before reporting.** Each `SKILL.md` has a `## Validate the output` section
  saying how to check that a result is non-empty, in the expected CRS and of a plausible
  magnitude.
- **Keep long commands visible.** Run downloads in the foreground (with `-progress` where
  available); do not pipe them through `head` or `tail`.

## Checklist for a new skill

- [ ] `skills/<skill-name>/SKILL.md` with `name` + `description` in the frontmatter
- [ ] `description` mentions when to use the skill, with French trigger terms
- [ ] long-form content moved to `references/` and linked from `SKILL.md`
- [ ] `skills/<skill-name>/README.md` with requirements, install command and contents
- [ ] entry added to the `Skills` table of the root `README.md`
- [ ] `npx skills add <path-to-this-repo>` lists the skill without a warning
- [ ] `SKILL.md` has a `## Validate the output` section, and its prerequisites follow the
  agent conduct rules above

CI runs [.github/validate-skills.py](.github/validate-skills.py) to parse YAML, validate
names and descriptions, require skill READMEs, and check local links and discoverable
references. It also runs the automated helper and local GDAL tests in `tests/`.
Install the Python validation dependency with `python3 -m pip install -r tests/requirements.txt`.

Discovery by the Skills CLI and agent skill selection remain separate checks; see
[tests/README.md](tests/README.md). Live IGN service tests are opt-in and do not run on
ordinary pushes or pull requests.
