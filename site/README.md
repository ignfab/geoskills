# Website

The website, <https://ignfab.github.io/geoskills/>, presents the skills for reading. It is
built with [Hugo](https://gohugo.io/) and the [Blowfish](https://blowfish.page/) theme from
the Markdown of this repository: nothing is written twice.

| Site | Generated from |
| --- | --- |
| English home page | Root `README.md`, without `Résumé (FR)`, `Contributing` and `License`; its first paragraph goes to the title block |
| French home page (`/fr/`) | The `Résumé (FR)` section of the root `README.md` |
| Skills, one page per family | `skills/<family>/README.md` |
| One page per skill, with child pages | The skill `README.md`; `SKILL.md` (as `instructions`) and `references/*.md` |
| Guide | `docs/*.md` |
| `llms.txt` | Families, skills and descriptions, linking to each `SKILL.md` |
| `.well-known/agent-skills/index.json` | One zip archive per skill ([Agent Skills Discovery](https://github.com/cloudflare/agent-skills-discovery-rfc) v0.2.0), so that `npx skills add https://ignfab.github.io/geoskills` installs from the site |

The French site shares the English skill and guide pages; only its home page and its
interface are French.

## Look

Green and white, with the details of a topographic map sheet: a graduated border, faint
grid lines and, on the home page, contour lines with spot heights, a north arrow, a scale
bar, a title cartouche and a legend of the six families. The terrain is invented; the
longitude ticks are those of Saint-Mandé, where IGN is based.

| File | Content |
| --- | --- |
| [assets/css/schemes/geoskills.css](assets/css/schemes/geoskills.css) | The colour scheme: Blowfish primary, secondary and neutral shades |
| [assets/css/custom.css](assets/css/custom.css) | Map details, home page, legend, cards with corner marks, light and dark modes |
| [layouts/partials/home/custom.html](layouts/partials/home/custom.html) | The home page: map sheet, legend built from the family pages, then the README content |
| [assets/img/contours.svg](assets/img/contours.svg) | Contour lines drawn from a synthetic terrain, coloured by the stylesheet |
| [assets/img/logo.svg](assets/img/logo.svg) | Logo and favicon |
| [assets/img/logo-mteattvl.png](assets/img/logo-mteattvl.png), [assets/img/logo-ign.png](assets/img/logo-ign.png) | State brand block of the ministries (left) and IGN logo (right), shown unchanged on a white band at the top of every page by [layouts/partials/header/geoskills.html](layouts/partials/header/geoskills.html). Replace the ministry block when the ministries change. |
| [assets/icons/](assets/icons/) | One map symbol per family (`gs-*.svg`) |
| [i18n/](i18n/) | Home page labels in English and French |

The English tagline of the title block is `description` in
[languages.en.toml](config/_default/languages.en.toml): keep it in line with the first
paragraph of the root README.

## How it is generated

[generate.py](generate.py) writes the content into `site/generated/`, which is not
committed:

- The first heading becomes the page title. The front matter takes its description from
  `SKILL.md` and its summary from the first paragraph, and links to the source file on
  GitHub.
- A link to another published page becomes a Hugo `relref`, so a broken link fails the Hugo
  build. A link to any other file (scripts, tests, `CLAUDE.md`) points to GitHub. Links in
  code are left unchanged.
- It stops with an error on a broken link, a link leaving the repository, a source file
  containing `{{<` or `{{%`, or a generated file named `SKILL.md`.

[tests/test_site_generator.py](../tests/test_site_generator.py) covers it without Hugo.

## Build and preview

Fetch the theme, pinned to Blowfish v3.10.0, then generate the content:

```bash
git submodule update --init --depth 1 site/themes/blowfish
python3 site/generate.py
```

Previewing needs Hugo 0.166 to 0.169, the range Blowfish v3.10.0 supports. The extended
edition used in CI is
[`hugo_extended_0.169.0`](https://github.com/gohugoio/hugo/releases/tag/v0.169.0). Install
it yourself if you want a preview, then run:

```bash
hugo server --source site
```

## Deployment

The [Site workflow](../.github/workflows/pages.yml) builds the site on every pull request
and deploys it from `main`. GitHub Pages must be enabled once, in **Settings → Pages →
Source: GitHub Actions**. The workflow keeps the hidden `.well-known/` folder in the
uploaded artifact.

To change the theme version, check out another tag in `site/themes/blowfish`, commit the
submodule and set `HUGO_VERSION` in the workflow to a Hugo version that tag supports.
