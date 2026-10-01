# Skill tests

Automated tests check commands, data and helpers. Manual scenarios check agent selection
and decisions; their French prompts exercise skills described in English.

## Automated checks

From the repository root, with Python >= 3.9 and PyYAML installed:

```bash
python3 -m pip install -r tests/requirements.txt
python3 .github/validate-skills.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Agents must not install missing software; give the installation command to the user.

- `test_split_csv.py`
- `test_validation.py`

## Manual scenarios

Check CLI discovery with `npx skills add . --list` from the repository root. Install the
skills for your agent, start a fresh session in `tests/`, then run the following prompts.
Use `output/` for generated files and keep source fixtures unchanged.

- [geopf-geocoding.md](geopf-geocoding.md)
- [geopf-wfs-download.md](geopf-wfs-download.md)
