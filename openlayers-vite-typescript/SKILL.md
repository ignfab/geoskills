---
name: openlayers-vite-typescript
description: Creates and configures an OpenLayers project with Vite and TypeScript. Use when the user wants to start a map application with OpenLayers, Vite, TypeScript, or follow the official ol-vite template.
---

# OpenLayers Project with Vite and TypeScript

Reference: [ol-vite](https://github.com/openlayers/ol-vite), [create-ol-app](https://github.com/openlayers/create-ol-app).

## Create the project (official template)

1. **Create the application** (Node 14+, `git` installed):

```bash
npx create-ol-app my-app --template vite
```

Without a name: `npx create-ol-app` initializes the project in the current directory.

2. **Start the dev server** (http://localhost:5173):

```bash
cd my-app
npm start
```

3. **Production build**:

```bash
npm run build
```

Deploy the contents of `dist/`. Preview: `npm run serve`.

## Switching to TypeScript

The ol-vite template is in JavaScript. For a TypeScript project:

1. **Install TypeScript** (in the project directory):

```bash
npm install -D typescript
```

2. **Add `tsconfig.json`** at the root:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

3. **Rename the entry**: `main.js` → `src/main.ts` (and update the script in `index.html`: `<script type="module" src="/src/main.ts"></script>`).

4. **TypeScript entry example** (`src/main.ts`):

```typescript
import './style.css';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';

const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OSM(),
    }),
  ],
  view: new View({
    center: [0, 0],
    zoom: 2,
  }),
});
```

The `ol` package ships its own types; no need to install `@types/ol`.

## Typical structure after switching to TypeScript

- `index.html`: entry point, script `src="/src/main.ts"`
- `src/main.ts`: map initialization
- `src/style.css`: styles (move from root if needed)
- `vite.config.ts`: Vite config (optional)

## Useful commands

| Command         | Effect                    |
|-----------------|---------------------------|
| `npm start`     | Dev server (Vite)         |
| `npm run build` | Build into `dist/`        |
| `npm run serve` | Preview of `dist/`        |

## Troubleshooting

- **"could not find commit hash"**: install [git](https://git-scm.com/).
- **Available templates**: `npx create-ol-app --help` (e.g. `--template webpack`).
