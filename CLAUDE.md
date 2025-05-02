# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- `npm run bootstrap` - Install all dependencies across the monorepo
- `npm run dev` - Start both client and server in development mode
- `npm run server` - Start only the server in development mode
- `npm run client` - Start only the client in development mode
- `(cd server && npm run build)` - Build the server
- `(cd client && npm run build)` - Build the client

## Database Commands
- `(cd server && npm run migrate)` - Run DB migrations
- `(cd server && npm run seed)` - Seed the database

## Code Style Guidelines
- **TypeScript**: Strong typing with strict mode enabled
- **Formatting**: 2-space indentation, single quotes
- **Error Handling**: Use try/catch blocks with appropriate logging
- **Imports**: Group imports (React/3rd-party/local) with a blank line between groups
- **Naming**: camelCase for variables/functions, PascalCase for components/classes
- **Components**: Function components with TypeScript interfaces for props
- **Backend**: RESTful Express routes with async/await pattern
- **Database**: Use Knex query builder for all database operations