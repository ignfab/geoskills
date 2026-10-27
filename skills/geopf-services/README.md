# geopf-services

An orientation guide to the French
[Géoplateforme services](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/).
It helps an agent choose an API by the expected output: metadata, maps, vector features, dataset
files, coordinates, elevation, routes, reachable areas or standards-validation reports.

The skill distinguishes WMS-R/WMS-V, WMTS, TMS and WFS, explains when to prefer ready-made
downloads or authenticated extraction, and links to current official service guides.
It routes implementation to `geopf-wfs-download`, `geopf-wms-wmts` and `geopf-geocoding`
where appropriate rather than duplicating their workflows.

## Requirements

- No local tools for conceptual guidance; web access for official documentation and live
  metadata checks.
- Optional `curl` for the discovery examples. Install it yourself with
  `sudo apt install curl` (Debian/Ubuntu) or `brew install curl` (macOS).
- Extraction, standards validation and usage statistics require an account and appropriate
  access. The skill does not automate account creation or interactive login.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-services
```

Install the other service skills separately, or install the whole repository, if you
also want their execution workflows. The overview remains usable on its own through
the official documentation links.

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Service selection, discovery, handoff and validation |
| [references/data-delivery.md](references/data-delivery.md) | Map images, tiles, vector features, file downloads and extraction |
| [references/search-and-processing.md](references/search-and-processing.md) | CSW, dataset search, geocoding, elevation, navigation, validation and usage statistics |
| [Manual scenarios](../../tests/geopf-services.md) | French prompts for service choice and direct handoff to specialized skills |

The references are an original summary of the official guides, checked on 2026-10-27,
not a frozen API specification. Resource availability, permissions and limits must be
checked at use time.
