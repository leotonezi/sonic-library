# CLAUDE.md

Sonic Library — a book management app with AI-powered recommendations.

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| Database | PostgreSQL | 5432 |
| Test Frontend | http://localhost:3001 | 3001 |
| Test Backend | http://localhost:8001 | 8001 |

## Development Commands

```bash
# Start all services
docker-compose up --build

# Start test environment (isolated database)
docker-compose -f docker-compose.test.yml up --build
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| Frontend | Next.js 15 + React 19 + Zustand + Tailwind CSS |
| AI/LLM | LangChain + OpenAI (GPT-3.5-turbo) |
| E2E Testing | Cypress |
| Containerization | Docker Compose |

## Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Backend Models | PascalCase | `User`, `UserBook` |
| Backend Endpoints | kebab-case | `/user-books` |
| Backend Services | PascalCase + Service | `BookService` |
| Frontend Components | PascalCase | `NavBar`, `BookCard` |
| Frontend Files | kebab-case | `book-card.tsx` |
| Zustand Stores | camelCase + use prefix | `useAuthStore` |
| TypeScript Types | PascalCase | `Book`, `PaginatedResponse` |

## Agent Principles

1. Don't assume. Don't hide confusion. Surface tradeoffs.
2. Minimum code that solves the problem. Nothing speculative.
3. Touch only what you must. Clean up only your own mess.
4. Define success criteria. Loop until verified.

## Code Style

- Always use TypeScript types and Python type hints
- Use async/await for all I/O operations
- Prefer guard clauses over nested conditions
- Prefer pure functions, avoid mutations
- Don't store JWTs in localStorage (use HTTP-only cookies)
- Don't skip type annotations in new code
- Don't commit `.env` files or secrets

## Environment Variables

### Backend (`.env`)
```
DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, FRONTEND_URL, BACKEND_URL,
MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_SERVER, MAIL_PORT,
TESTING, POPULAR_BOOKS_CACHE_TTL
```

### Frontend (`.env.local`)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## PR Checklist

- [ ] Tests pass (`pytest` and `npm run lint`)
- [ ] Types correct (no `any` unless necessary)
- [ ] Database migrations created if schema changed
- [ ] No console.log or print statements left
