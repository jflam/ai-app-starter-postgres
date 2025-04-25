# Petbnb Starter 🐾

Petbnb Starter is an **opinionated TypeScript/Node template** built to be **modified by a large‑language model (LLM)**.  
It focuses on clear structure, strict typing, and automated tooling so you can prototype quickly or hand over incremental tasks to an LLM with minimal friction.

---

## Table of Contents
1. Purpose
2. Prerequisites
3. Quick Start
4. Project Structure
5. Environment Variables
6. Scripts
7. Testing, Linting & Formatting
8. Build & Deployment
9. Extending with an LLM
10. Contributing
11. License

---

## 1. Purpose

• Provide a minimal yet realistic backend scaffold.  
• Demonstrate best‑practice tooling (TypeScript, ESLint, Prettier, Husky, Jest).  
• Keep code small and well‑typed so GPT‑style models can reason about it easily.  
• Be opinionated—but replace anything you dislike.

---

## 2. Prerequisites

| Tool | Version (tested) | Notes              |
| ---- | ---------------- | ------------------ |
| Node | ≥ 18.x           | Runtime            |
| npm  | ≥ 9.x            | Dependency manager |
| git  | any              | Version control    |

Verify:

```bash
node -v
npm -v
git --version
```

---

## 3. Quick Start

```bash
git clone https://github.com/your‑org/petbnb-starter.git
cd petbnb-starter
cp .env.example .env   # fill in required vars
npm install            # or: npm ci
npm run dev            # hot‑reload server
```

The dev server uses `ts-node-dev`; source lives in `src/` and is not transpiled to disk.

---

## 4. Project Structure

```
petbnb-starter
├── src/
│   ├── config/        # Runtime configuration & env validation
│   ├── controllers/   # Request handlers
│   ├── models/        # Data models (ORM/Prisma/etc.)
│   ├── services/      # Business logic
│   ├── utils/         # Reusable helpers
│   └── index.ts       # App entry
├── test/              # Jest test suites
├── .github/           # CI workflows
├── .husky/            # Git hooks
├── dist/              # Transpiled output (git‑ignored)
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

---

## 5. Environment Variables

1. Copy `.env.example` → `.env`.  
2. Update values:

```
PORT=3000
DATABASE_URL=postgres://user:pass@localhost:5432/petbnb
```

`src/config/env.ts` validates required keys at startup and throws on missing/invalid values.

---

## 6. Scripts

| Command            | Description                                   |
| ------------------ | --------------------------------------------- |
| `npm run dev`      | Start dev server with hot‑reload              |
| `npm run build`    | Transpile to `dist/`                          |
| `npm start`        | Run compiled code from `dist/`                |
| `npm test`         | Run Jest test suites                          |
| `npm run lint`     | ESLint codebase                               |
| `npm run format`   | Prettier – write                              |
| `npm run typecheck`| Run `tsc` without emitting code               |

Husky hooks execute `lint` + `test` on `pre‑commit`, blocking unsafe pushes.

---

## 7. Testing, Linting & Formatting

```bash
npm run test       # jest --coverage
npm run lint       # eslint .
npm run format     # prettier --write .
```

Rules follow Airbnb style with TypeScript, no implicit `any`, and Prettier for consistent whitespace.

---

## 8. Build & Deployment

### Local production build

```bash
npm run build
NODE_ENV=production node dist/index.js
```

### Docker (optional)

```bash
docker build -t petbnb .
docker run -p 3000:3000 --env-file .env petbnb
```

### CI (GitHub Actions)

`.github/workflows/ci.yml`:

1. Checkout & install  
2. Run `lint`, `test`, `build`  
3. Publish Docker image / deploy (placeholder – adapt for your cloud)

---

## 9. Extending with an LLM

Guidelines for best results:

1. **Be explicit.** Point the model to a file/path and ask for diff‑style edits.  
2. **Keep prompts small.** Provide only the code needed to answer.  
3. **Request minimal patches.** Helps avoid merge conflicts.  
4. **Trust but verify.** Run `npm test` and `npm run lint` after every change.

> The project’s small, typed files make it easier for a model to navigate and reason about dependencies.

---

## 10. Contributing

1. Fork → create branch → commit → open PR.  
2. CI must pass (`lint` + `test`).  
3. Describe *why* not just *what* in your PR.  
4. Squash commits before merge.

---

## 11. License

MIT © 2023 Petbnb Starter contributors
