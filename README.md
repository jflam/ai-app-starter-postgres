# AI Starter App

Opinionated full‑stack skeleton meant to be **forked and cloned** so you (or your AI pair‑programmer) can start coding features immediately instead of scaffolding a project from scratch.

## Repository overview
This monorepo ships a minimal “random fortune” demo to prove everything works end‑to‑end, but the real goal is to provide a ready‑to‑hack stack for rapid AI‑assisted development:

• Backend – an Express + Knex + SQLite API that returns one random fortune
• Front‑end – a React/Vite SPA that fetches and shows it

## Folder layout

1. Backend (server)
Key files

index.ts – Express entry point with one route (GET /api/fortunes/random).
db.ts – Knex instance wired to SQLite via knexfile.js.
20250423_create_fortunes_table.js – creates fortunes table.
01_fortunes_seed.js – inserts 20 example fortunes.
Important npm scripts (see server/package.json)

Script	What it does
npm run dev	Runs latest migration & seed, then hot‑reloads via ts-node-dev.
npm run migrate	knex migrate:latest
npm run seed	knex seed:run
npm run build	Type‑checks & emits JS to server/dist/
Server starts on http://localhost:4000 (port can be overridden via PORT env).

2. Front‑end (client)
Key files

App.tsx – React component showing the fortune.
main.tsx – app bootstrap.
vite.config.ts – dev server on port 3000 with a proxy to /api → http://localhost:4000.
npm scripts (see client/package.json)

Script	Purpose
npm run dev	Launch Vite dev server with HMR
npm run build	Production build to client/dist/
npm run preview	Preview the build locally
The SPA calls /api/fortunes/random; the Vite proxy forwards it to the Express server during development.

3. Root workspace
package.json only installs concurrently and wires both apps:

Script	Runs
npm run dev	Starts server + client in parallel
npm run server	cd server && npm run dev
npm run client	cd client && npm run dev
## Why this repo?
* **Curated dependencies** – Express, Knex, React, Vite, TypeScript, ESLint & Prettier all pre‑configured.  
* **Batteries included** – hot reload, DB migrations, seeding, proxying, and split dev servers work out of the box.  
* **AI friendly** – consistent code style and simple architecture make it easy for tools like GitHub Copilot or ChatGPT to suggest accurate changes.  
* **Zero scaffolding** – fork ➜ clone ➜ `npm run dev` ➜ start prompting.

## Getting started
The first server start automatically:

Runs the migration creating fortunes table.
Seeds it with sample data.
Hot‑reloads on TypeScript changes.
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