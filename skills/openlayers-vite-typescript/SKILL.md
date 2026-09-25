---
name: openlayers-vite-typescript
description: Creates and configures an OpenLayers project with Vite and TypeScript. Use when the user wants to start a map application (carte, fond de plan, couche) with OpenLayers, Vite or TypeScript, or follow the official ol-vite template.
---

# OpenLayers project with Vite and TypeScript

Bootstrap an OpenLayers application with the official template, then convert it to
TypeScript.

Reference: [ol-vite](https://github.com/openlayers/ol-vite),
[create-ol-app](https://github.com/openlayers/create-ol-app).

## Create the project

Requires Node 14+ and `git`.

```bash
npx create-ol-app my-app --template vite
cd my-app
npm start
```

`npm start` serves the application on <http://localhost:5173>. Without a name,
`npx create-ol-app` initializes the project in the current directory.

## Build

```bash
npm run build
```

Deploy the contents of `dist/`. Preview the build with `npm run serve`.

| Command         | Effect             |
|-----------------|--------------------|
| `npm start`     | Dev server (Vite)  |
| `npm run build` | Build into `dist/` |
| `npm run serve` | Preview of `dist/` |

## Switch to TypeScript

The ol-vite template is JavaScript. Converting it takes three steps:

```bash
npm install -D typescript
```

1. Add a `tsconfig.json` at the root.
2. Rename `main.js` to `src/main.ts` and update the script tag in `index.html`.
3. Import from `ol` as usual — the package ships its own types, so `@types/ol` is not
   needed and must not be installed.

See [references/typescript-setup.md](references/typescript-setup.md) for the full
`tsconfig.json`, a working `src/main.ts` and the resulting project layout.

## Troubleshooting

- **"could not find commit hash"** — install [git](https://git-scm.com/).
- **Other templates** — `npx create-ol-app --help` lists them, e.g. `--template webpack`.
