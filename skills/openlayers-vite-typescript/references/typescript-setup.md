# TypeScript setup

Applies to a project created with `npx create-ol-app my-app --template vite`.

## 1. Install TypeScript

```bash
npm install -D typescript
```

## 2. Add `tsconfig.json`

At the root of the project:

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

## 3. Move the entry point

Rename `main.js` to `src/main.ts`, move `style.css` to `src/style.css` if it sits at the
root, and update `index.html`:

```html
<script type="module" src="/src/main.ts"></script>
```

## 4. Entry point example

`src/main.ts`:

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

The `ol` package ships its own type declarations: do **not** install `@types/ol`.

## Resulting layout

```
my-app/
├── index.html        # entry point, script src="/src/main.ts"
├── tsconfig.json
├── vite.config.ts    # optional
└── src/
    ├── main.ts       # map initialization
    └── style.css
```

## Type checking

`vite` strips types without checking them. Add an explicit check to `package.json`:

```json
"scripts": {
  "typecheck": "tsc --noEmit"
}
```
