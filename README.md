# AI Starter App

Opinionated full‑stack skeleton meant to be **forked and cloned** so you (or your AI pair‑programmer) can start coding features immediately instead of scaffolding a project from scratch.

## Repository overview
This monorepo ships a minimal “random fortune” demo to prove everything works end‑to‑end, but the real goal is to provide a ready‑to‑hack stack for rapid AI‑assisted development:

• Backend – an Express + Knex + SQLite API that returns one random fortune
• Front‑end – a React/Vite SPA that fetches and shows it

## Folder layout

```text
/ (root)
├─ server/     → Express + Knex backend
├─ client/     → React + Vite front‑end
└─ README.md
```

### server/ (Backend)

**Key files**
- `index.ts` – Express entry point (exposes `GET /api/fortunes/random`)
- `db.ts` – Knex instance configured via `knexfile.js`
- `migrations/20250423_create_fortunes_table.js` – creates the `fortunes` table
- `seeds/01_fortunes_seed.js` – inserts 20 sample fortunes

**npm scripts**

| Script | Purpose |
| ------ | ------- |
| `npm run dev` | Runs latest migration & seed, then hot‑reloads via `ts-node-dev` |
| `npm run migrate` | `knex migrate:latest` |
| `npm run seed` | `knex seed:run` |
| `npm run build` | Type‑checks & emits JS to `server/dist/` |

Server listens on **http://localhost:4000** (`PORT` env var overrides).

### client/ (Front‑end)

**Key files**
- `App.tsx` – React component that shows the fortune
- `main.tsx` – App bootstrap
- `vite.config.ts` – Dev server on port 3000 (proxy `/api` → `http://localhost:4000`)

**npm scripts**

| Script | Purpose |
| ------ | ------- |
| `npm run dev` | Launch Vite dev server with HMR |
| `npm run build` | Production build to `client/dist/` |
| `npm run preview` | Preview the build locally |

The SPA calls `/api/fortunes/random`; Vite proxies the request to the Express server during development.

### root/

Contains only a `package.json` that orchestrates both apps.

| Script | Runs |
| ------ | ---- |
| `npm run dev` | Starts server & client in parallel |
| `npm run server` | `cd server && npm run dev` |
| `npm run client` | `cd client && npm run dev` |
| `npm run bootstrap` | Installs dependencies in root, server and client |

## Why this repo?
* **Curated dependencies** – Express, Knex, React, Vite, TypeScript, ESLint & Prettier all pre‑configured.  
* **Batteries included** – hot reload, DB migrations, seeding, proxying, and split dev servers work out of the box.  
* **AI friendly** – consistent code style and simple architecture make it easy for tools like GitHub Copilot or ChatGPT to suggest accurate changes.  
* **Zero scaffolding** – fork ➜ clone ➜ `npm run dev` ➜ start prompting.

## Getting started

1. **Fork & clone**
   ```bash
   gh repo fork ai-starter-app --clone
   cd ai-starter-app
   ```

2. **Install dependencies**

   **Option A (one‑liner)**  
   ```bash
   npm run bootstrap
   ```

   **Option B (manual)**  
   ```bash
   npm install          # root
   cd server && npm install
   cd ../client && npm install
   cd ..
   ```

3. **Run the dev stack**

   ```bash
   npm run dev
   ```

   • React/Vite SPA on **http://localhost:3000**  
   • Express/Knex API on **http://localhost:4000**

   The first boot automatically:
   * runs the latest migration,
   * seeds the SQLite DB with sample fortunes,
   * hot‑reloads on TypeScript changes.

4. **Verify the demo endpoint**

   ```bash
   curl http://localhost:4000/api/fortunes/random
   ```

   Returns: `{ "id": 7, "text": "Your shoes will make you happy today." }`

5. **Start prompting your AI assistant** – the stack is live; add routes, components, or tests right away.

## Building for production
Backend

Frontend

Serve compiled assets with any static host or integrate into a single Express build as needed.

## Environment variables
Only the server respects PORT (default 4000). Add more as your app grows.

## TL;DR
1. Fork this repo (`gh repo fork ai-starter-app`) and clone it locally.  
2. `npm install` in **root**, **server**, and **client**.  
3. `npm run dev` in root  
   * SPA: http://localhost:3000  
   * API: http://localhost:4000  
4. Start chatting with your AI – all dependencies are already wired together.  
5. Example endpoint: `GET /api/fortunes/random` returns `{ id, text }`.