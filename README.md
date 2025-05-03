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
├─ infra/      → Azure infrastructure as code
│  ├─ main.bicep → Bicep template for Azure resources
│  ├─ azure-config.json → Centralized Azure configuration
├─ scripts/    → Deployment and utility scripts
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

**npm scripts**

| Script | Purpose |
| ------ | ------- |
| `npm run dev` | Launch Vite dev server with HMR |
| `npm run build` | Production build to `client/dist/` |
| `npm run preview` | Preview the build locally |

The SPA calls `/api/fortunes/random`; Vite proxies the request to the Express server during development.

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
- **Azure CLI** and **Azure Developer CLI (azd)** for deployment
- **uv** - Modern Python package installer

```bash
# check your versions
node -v   # → v20.x
npm -v    # → 10.x
docker --version # → Docker version 24.x
az --version # → azure-cli x.x.x
azd version # → x.x.x
uv --version # → x.x.x
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

For Azure tools:
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux
brew install azure-cli  # macOS
# Or download from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash  # Linux/macOS
# Or download from https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd
```

> After installing, reopen your terminal so all tools are in PATH.

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

## Deploying to Azure

This project includes infrastructure as code and deployment automation for Azure. The deployment process is managed through the Azure Developer CLI (azd) with additional tooling to check quotas and manage configuration.

### Python Dependencies Setup

The deployment tools require Python packages. Set these up using uv:

```bash
# Initialize Python project in the scripts directory
cd scripts
uv init

# Install required packages
uv add uvicorn fastapi pydantic rich aiohttp

# Return to project root
cd ..
```

### Configuration

All Azure resource configurations are centralized in `infra/azure-config.json`. This file defines:

- Required services and their SKUs
- Database configuration
- Allowed deployment regions
- Resource tags and naming conventions

Example configuration:
```json
{
  "required_services": {
    "postgresql": {
      "sku": {
        "name": "Standard_B2s",
        "tier": "Burstable"
      },
      "version": "16",
      "storage_gb": 32
    },
    "container_apps": {
      "resources": {
        "cpu": 0.5,
        "memory": "1Gi"
      }
    }
  }
}
```

### Deployment Steps

1. **Check Azure Quotas**

   Before deploying, check if your subscription has sufficient quota in your desired regions:

   ```bash
   export AZURE_SUBSCRIPTION_ID="your-subscription-id"
   
   # Run the quota check script using uv
   uv run scripts/check_azure_quota.py
   ```

   This will show available quotas across all configured regions and indicate which regions have sufficient capacity for deployment.

   You can also run it as a web service:
   ```bash
   uv run scripts/check_azure_quota.py --server
   ```

2. **Configure Azure**

   ```bash
   # Login to Azure
   az login
   
   # Set default subscription if needed
   az account set --subscription <subscription-id>
   
   # Initialize Azure Developer CLI environment
   azd init
   ```

3. **Set Required Environment Variables**

   ```bash
   azd env set POSTGRES_ADMIN_PASSWORD "your-secure-password"
   ```

4. **Deploy**

   ```bash
   azd up
   ```

   The deployment process will:
   - Generate Bicep parameters from azure-config.json
   - Create or update Azure resources
   - Build and deploy the application
   - Configure all necessary connections

### Deployment Architecture

The application deploys the following Azure resources:

- **Azure Container Apps** - Hosts the API
- **Azure Database for PostgreSQL Flexible Server** - Database
- **Azure Container Registry** - Stores Docker images
- **Azure Static Web Apps** - Hosts the front-end
- **Log Analytics Workspace** - Centralized logging

### Post-Deployment

After deployment completes:

1. **Run Database Migrations**
   ```bash
   cd server
   DATABASE_URL="<connection-string>" npx prisma migrate deploy
   ```

2. **Seed the Database**
   ```bash
   DATABASE_URL="<connection-string>" npx prisma db seed
   ```

3. **Verify the Deployment**
   ```bash
   # Get the deployed endpoints
   azd show
   ```

### Troubleshooting

- If deployment fails due to quota issues, run the quota check script and either:
  - Choose a different region with sufficient quota
  - Request a quota increase through Azure Portal
- For database connection issues, verify the firewall rules are correctly configured
- Check Container Apps logs in Azure Portal for API issues
- For Static Web App issues, verify the API URL environment variable is correctly set

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
- `AZURE_SUBSCRIPTION_ID` - Required for quota checks and deployment

## Docker Compose configuration

The `docker-compose.yml` defines:

- `db` service - PostgreSQL 16 Alpine with credentials in the compose file
- `api` service - Node.js API with Prisma connecting to the database

To run only the database:

```bash
docker compose up -d db
```

To rebuild and run the API:

```bash
docker compose up --build api
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
7. Deploy to Azure:
   * Check quotas: `python3 scripts/check_azure_quota.py`
   * Deploy: `azd up`

## Development Tools

### Python Package Management

This project uses uv for Python package management. Some useful commands:

```bash
# Initialize a new Python project
uv init

# Add packages
uv add <package-name>

# Run Python scripts in an isolated environment
uv run <script.py>

# Create a virtual environment
uv venv

# Install packages from requirements.txt
uv pip install -r requirements.txt
```