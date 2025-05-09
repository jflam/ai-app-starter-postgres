# AI Starter App with PostgreSQL and Prisma

Opinionated full‑stack skeleton meant to be **forked and cloned** so you (or your AI pair‑programmer) can start coding features immediately instead of scaffolding a project from scratch.

## Repository overview
This monorepo ships a minimal "random fortune" demo to prove everything works end‑to‑end, but the real goal is to provide a ready‑to‑hack stack for rapid AI‑assisted development:

• Backend – an Express + Prisma + PostgreSQL API that returns one random fortune
• Front‑end – a React/Vite SPA that fetches and shows it
• Docker – containerized development environment for PostgreSQL and API

## Folder layout

```text
/ (root)
├─ server/     → Express + Prisma backend
│  ├─ prisma/  → Prisma schema and seeds
├─ client/     → React + Vite front‑end
├─ docker-compose.yml → Container configuration
└─ README.md
```

### server/ (Backend)

**Key files**
- `index.ts` – Express entry point (exposes `GET /api/fortunes/random`)
- `db.ts` – Prisma client instance and data access functions
- `prisma/schema.prisma` – Prisma schema defining the database models
- `prisma/seed.ts` – Seeds the database with sample fortunes
- `Dockerfile` – Container configuration for the API

**npm scripts**

| Script | Purpose |
| ------ | ------- |
| `npm run dev` | Runs Prisma migrations, seeds the database, then hot‑reloads via `ts-node-dev` |
| `npm run migrate` | `prisma migrate deploy` |
| `npm run seed` | `prisma db seed` |
| `npm run build` | Type‑checks & emits JS to `server/dist/` |

Server listens on **http://localhost:4000** (`PORT` env var overrides).

### client/ (Front‑end)

**Key files**
- `App.tsx` – React component that shows the fortune
- `main.tsx` – App bootstrap
- `vite.config.ts` – Dev server on port 3000 (proxy `/api` → `http://localhost:4000`)
- `.env` – Environment variables including API URL for production

**Environment Variables**

| Variable | Purpose |
| -------- | ------- |
| `VITE_API_BASE_URL` | Base URL for API requests in production |

**npm scripts**

| Script | Purpose |
| ------ | ------- |
| `npm run dev` | Launch Vite dev server with HMR |
| `npm run build` | Production build to `client/dist/` |
| `npm run preview` | Preview the build locally |

The SPA calls `/api/fortunes/random`; Vite proxies the request to the Express server during development. In production, it uses the `VITE_API_BASE_URL` environment variable to target the deployed API.

### docker-compose.yml

Defines two services:
- `db` - PostgreSQL database running on port 5433
- `api` - Express API running on port 4001

### root/

Contains only a `package.json` that orchestrates both apps.

| Script | Runs |
| ------ | ---- |
| `npm run dev` | Starts Docker services (API + PostgreSQL) and client in parallel |
| `npm run dev:client` | `cd client && npm run dev` |
| `npm run dev:api` | `docker compose up --build` |
| `npm run server` | `cd server && npm run dev` (runs directly on host, not in Docker) |
| `npm run client` | `cd client && npm run dev` |
| `npm run bootstrap` | Installs dependencies and generates Prisma client |
| `npm run prisma:generate` | Generates Prisma client |

## Why this repo?
* **Curated dependencies** – Express, Prisma, React, Vite, TypeScript, ESLint & Prettier all pre‑configured.  
* **Batteries included** – hot reload, DB migrations, seeding, proxying, and split dev servers work out of the box.  
* **Docker ready** – PostgreSQL and API run in Docker containers for consistent development.
* **AI friendly** – consistent code style and simple architecture make it easy for tools like GitHub Copilot or ChatGPT to suggest accurate changes.  
* **Zero scaffolding** – fork ➜ clone ➜ `npm run dev` ➜ start prompting.

## Getting started

### Prerequisites
To run the stack you need:
- **Node.js 20 LTS** (npm is bundled)
- **Docker** (Desktop or Engine)

```bash
# check your versions
node -v   # → v20.x
npm -v    # → 10.x
docker --version # → Docker version 24.x
```

If you need to install or upgrade Node.js:

- **nvm (recommended)**  
  ```bash
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  nvm install 20
  nvm use 20
  ```

- **Homebrew (macOS)**  
  ```bash
  brew install node@20
  ```

- **Windows** – download the 20 LTS installer from <https://nodejs.org> or use `nvm-windows`.

For Docker, download and install Docker Desktop from https://www.docker.com/products/docker-desktop/

> After installing, reopen your terminal so `node`, `npm`, and `docker` are in PATH.

1. **Fork & clone**
   ```bash
   gh repo create your-new-repo --template jflam/ai-app-starter-postgres --private --clone
   cd your-new-repo
   ```

2. **Install dependencies**

   **Option A (one‑liner)**  
   ```bash
   npm run bootstrap
   ```

   **Option B (manual)**  
   ```bash
   npm install          # root
   cd server && npm install
   cd ../client && npm install
   cd ..
   cd server && npx prisma generate
   ```

3. **Run the dev stack**

   ```bash
   npm run dev
   ```

   • React/Vite SPA on **http://localhost:3000**  
   • Express/Prisma API on **http://localhost:4001** (in Docker)
   • PostgreSQL on **localhost:5433** (in Docker)

### Understanding the architecture

The application is composed of three main parts:

1. **PostgreSQL Database** - Runs in a Docker container, accessible on port 5433.
2. **Express API** - Also runs in a Docker container, exposing port 4001, and connecting to the PostgreSQL container.
3. **React Frontend** - Runs directly on the host, connecting to the API container.

When you run `npm run dev`, the following happens:
- Docker Compose starts both the PostgreSQL container and the API container
- The API container applies Prisma migrations and seeds the database
- The React dev server starts on your host machine

### Testing the API

```bash
curl http://localhost:4001/api/fortunes/random
```

Returns: `{ "id": 7, "text": "Your persistence will pay off soon.", "created": "2025-05-02T17:34:42.839Z" }`

### Prisma commands

To interact with the database using Prisma:

```bash
# Generate Prisma client after schema changes
cd server && npx prisma generate

# Run migrations
cd server && npx prisma migrate dev --name your_migration_name

# Seed the database
cd server && npx prisma db seed

# Open Prisma Studio (web UI for database)
cd server && npx prisma studio
```

## Building for production

### 1. Compile the backend (server)

The backend is containerized and can be built with:

```bash
docker compose build api
```

Or running directly:

```bash
cd server
npm install        # first‑time only
npm run build      # emits JS to server/dist/
NODE_ENV=production node dist/index.js
```

### 2. Build the front‑end (client)

```bash
cd client
npm install        # first‑time only
npm run build      # outputs static assets to client/dist/
```

### 3. Serve the SPA

Any static host (Nginx, Netlify, Vercel, S3, etc.) can serve the `client/dist/` folder.

Local preview:

```bash
cd client
npm run preview    # opens http://localhost:4173
```

### 4. One‑shot helper from the repo root

```bash
npm run bootstrap                     # ensure all deps
docker compose build api \
  && (cd client && npm run build)
```

## Environment variables

- `PORT` - API port (default 4000 inside the container)
- `DATABASE_URL` - PostgreSQL connection string

## Docker Compose configuration

The `docker-compose.yml` defines:

- `db` service - PostgreSQL 16 Alpine with credentials in the compose file
- `api` service - Node.js API with Prisma connecting to the database

To run only the database:

```bash
docker compose up db -d
```

To rebuild and run the API:

```bash
docker compose up api --build
```

To run everything:

```bash
docker compose up
```

## TL;DR
1. Fork this repo and clone it locally.  
2. Ensure Docker is running.
3. `npm run bootstrap` to install all dependencies.
4. `npm run dev` in root  
   * SPA: http://localhost:3000  
   * API: http://localhost:4001 (Docker)
   * PostgreSQL: localhost:5433 (Docker)
5. Start chatting with your AI – all dependencies are already wired together.  
6. Example endpoint: `GET /api/fortunes/random` returns `{ id, text, created }`.