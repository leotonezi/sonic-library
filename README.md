# Sonic Library

A full-stack digital library platform where users can browse books, track their reading, write reviews, and receive AI-powered recommendations based on their reading history.

## Live Demo

Try the live app: https://soniclibrary.vercel.app

## The Problem

Readers often struggle to:
- Keep track of books they want to read, are reading, or have finished
- Discover new books tailored to their tastes
- Find a centralized place to review and rate their reads

Sonic Library solves this by combining personal library management with AI-driven recommendations.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL |
| Frontend | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS |
| AI | LangChain + OpenAI GPT-3.5 |
| State | Zustand |
| Testing | Pytest, Cypress |
| Infrastructure | Docker, Docker Compose |

## Features

- **Authentication** - JWT-based auth with HTTP-only cookies
- **Book Search** - Search local database + Google Books API
- **Personal Library** - Track books as "To Read", "Reading", or "Read"
- **Reviews & Ratings** - Rate books 1-5 stars with written reviews
- **AI Recommendations** - Get personalized suggestions based on your reviews
- **Recommendation Graph** - Visual exploration of book relationships

## Quick Start

### Requirements

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

### Run with Docker

```bash
# Start all services
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Environment Variables

Create `.env` in `backend/`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/fastlibrary
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

Create `.env.local` in `frontend/`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Project Structure

```
sonic-library/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/v1/       # API endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   └── tests/
├── frontend/             # Next.js application
│   └── src/
│       ├── app/          # App Router pages
│       ├── components/
│       ├── store/        # Zustand state
│       └── services/     # API client
└── docker-compose.yml
```

## Running Tests

```bash
# Backend
cd backend && pytest

# Frontend lint
cd frontend && npm run lint

# E2E tests
cd frontend && npm run cypress:run
```

## Contributing

See the [Project Board](https://github.com/leotonezi/sonic-library/projects) for planned features and open issues.

## License

MIT
