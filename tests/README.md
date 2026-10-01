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

- `test_geopandas.py`
- `test_live.py`
- `test_split_csv.py`
- `test_validation.py`
- `test_workflows.py`

GDAL >= 3.1 and PROJ CLI tools are required for local workflow tests. Tests use temporary
outputs and disable PROJ networking. CI sets `GEOSKILLS_REQUIRE_GDAL=1`; missing tools
then fail. An installed but broken tool is always an error. NTF and vertical tests skip
when their IGN grids are unavailable.

Live IGN tests are disabled by default. Run them deliberately with
`GEOSKILLS_LIVE=1 python3 -m unittest discover -s tests -p 'test_live.py' -v`.
This sends public test addresses and coordinates to IGN and downloads bounded extracts;
do not substitute private data.

Optional Python checks require `python3 -m pip install -r tests/requirements-geospatial.txt`.
Missing optional dependencies produce explicit skips.

## Manual scenarios

Check CLI discovery with `npx skills add . --list` from the repository root. Install the
skills for your agent, start a fresh session in `tests/`, then run the following prompts.
Use `output/` for generated files and keep source fixtures unchanged.

- [crs-reprojection-france.md](crs-reprojection-france.md)
- [gdal-raster-basics.md](gdal-raster-basics.md)
- [geopandas-basics.md](geopandas-basics.md)
- [geopf-geocoding.md](geopf-geocoding.md)
- [geopf-wfs-download.md](geopf-wfs-download.md)
- [geopf-wms-wmts.md](geopf-wms-wmts.md)

See [fixture metadata](data/README.md) for provenance and CRS.
