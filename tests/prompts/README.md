# Experimental prompts

Scenario files (`tests/<skill>.md`) hold stable prompts with expected results, scored in A/B
campaigns. This folder traces the exploratory prompts used while a skill is written or
validated: a new skill, a description change, a chain of several skills, or a family that
has no skill yet. Each run is recorded so that the evidence behind a change is kept and good
prompts can become scenarios.

| File | Content |
| --- | --- |
| [catalog.md](catalog.md) | Every experimental prompt, with its family, expected skills and status |
| [runs.md](runs.md) | One row per run: date, harness, model, commit, skills loaded and outcome |

## Workflow

1. **Write the prompt first.** Add it to `catalog.md` with the next free `XP-<NN>` number
   before running it, so that its wording is fixed. Numbers are never reused.
2. **Install the skills under test** in a fresh directory outside the repository, so that
   the root `CLAUDE.md` does not leak into the run:

   ```bash
   npx skills add /path/to/geoskills -a claude-code -y
   ```

   Copy the fixtures from `tests/data/` into `data/`, create `output/`, then start a new
   session. The A/B runner does all of this for one prompt (`ab_run XP-05 with x1`); see
   [Experimental prompts in the A/B protocol](../ab-testing.md#experimental-prompts).
3. **Send the prompt as is.** Note the skills loaded, in order, and check the result against
   the `Watch` line of the catalog entry.
4. **Record the run** as a new row of `runs.md`.
5. **Follow up.** When the expected behavior is clear, promote the prompt to a scenario of
   `tests/<skill>.md` and set its status to `promoted to <ID>`. Otherwise change the skill or
   open an issue, and say so in the Notes.

## Columns of runs.md

- **Date**: the day of the run, `YYYY-MM-DD`.
- **Prompt**: the catalog identifier, such as `XP-05`.
- **Harness**: the agent tool and its version, such as `Claude Code 2.1.287 (claude -p)`.
- **Model**: the model identifier reported by the harness.
- **Commit**: `git rev-parse --short HEAD` of the installed skills, followed by `+dirty` when
  uncommitted changes were installed.
- **Skills loaded**: the skills of this repository loaded during the run, in order and in
  backticks, or `none`.
- **Outcome**: `pass`, `partial` or `fail`, as defined below.
- **Notes**: what worked and what failed, the cost and turns when known, and any follow-up.

| Outcome | Meaning |
| --- | --- |
| `pass` | The expected skills were loaded, the result is correct and no conduct rule was broken. |
| `partial` | The result is usable, but a skill was missing or unexpected, a step was incomplete or a check was skipped. |
| `fail` | The result or the skill is wrong, or a conduct rule was broken: an installation attempt, a download piped through `head` or `tail`, an invented layer or field name. |

## Rules

- The prompt is written entirely in French, exactly as sent; everything else is in English
  (see [Language](../../CLAUDE.md#language)).
- No credentials, personal data or private paths. Raw transcripts stay outside the
  repository; summarize them in the Notes.
- Add rows; never rewrite past runs. A rerun after a skill change is a new row with its own
  commit.
- Run rows retain the skill names used at that commit. Current catalog expectations use
  current names; [the naming guide](../../docs/skill-naming.md) maps renamed skills.
- [test_prompt_log.py](../test_prompt_log.py) checks identifiers, families, skill names,
  statuses and rows.

## Catalog entry template

```markdown
## XP-<NN> — <English title>

> <French prompt, exactly as sent>

- **Family:** `<family folder, such as 6-workflows>`
- **Expected skills:** `<skill-name>`, then `<skill-name>` (or `none`)
- **Watch:** <what a run must show>
- **Status:** open
```
