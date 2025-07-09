# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Run tests
pytest

# Run with specific test file
pytest tests/test_books.py

# Run with verbose output
pytest -v

# Start development server (via Docker)
docker-compose up --build
```

### Frontend (Next.js)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Full Application
```bash
# Start both backend and frontend with Docker
docker-compose up --build

# Access frontend: http://localhost:3000
# Access backend API docs: http://localhost:8000/docs
```

## Architecture Overview

### Technology Stack
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS
- **AI**: LangChain + OpenAI for book recommendations
- **Database**: PostgreSQL (via Docker)
- **Authentication**: JWT with cookie-based auth

### Project Structure
```
sonic-library/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/v1/   # API endpoints
│   │   ├── core/     # Config, database, security
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   ├── alembic/      # Database migrations
│   └── tests/        # Pytest tests
├── frontend/         # Next.js application
│   └── src/
│       ├── app/      # App Router pages
│       ├── components/
│       ├── services/
│       └── store/    # Zustand state management
└── docker-compose.yml
```

### Key Backend Patterns
- **Service Layer**: Business logic in `services/` directory using generic `BaseService`
- **Repository Pattern**: Database operations abstracted through services
- **JWT Authentication**: Cookie-based auth with access/refresh tokens
- **Pagination**: Standardized pagination with consistent metadata format
- **Error Handling**: HTTPException for API errors, early returns for validation

### Key Frontend Patterns
- **App Router**: Next.js 15 file-based routing with layout.tsx
- **Server Components**: Default to server components, client components when needed
- **State Management**: Zustand for global state (auth, search)
- **Protected Routes**: Authentication wrapper for protected pages
- **API Integration**: Service layer in `services/` for backend communication

### Database Models
- **User**: Authentication and profile data
- **Book**: Local book storage with external API integration
- **UserBook**: User's reading status and progress
- **Review**: User reviews and ratings

### Key Features
- **Book Management**: Local storage + Google Books API integration
- **Reading Lists**: Personal libraries with reading status tracking
- **AI Recommendations**: LangChain-powered book suggestions
- **Review System**: User ratings and reviews
- **Pagination**: Implemented across all major endpoints and frontend components

### Authentication Flow
1. Login via `/api/v1/auth/login`
2. JWT tokens stored in HTTP-only cookies
3. Frontend auth state managed via Zustand store
4. Protected routes check auth status on server-side

### Development Rules (from .cursorrules)
- **Backend**: Follow FastAPI best practices, use async/await, type hints, Pydantic models
- **Frontend**: Server components by default, TypeScript for type safety, follow Next.js conventions
- **Code Style**: Functional programming preferred, descriptive variable names, early returns for error handling

### Pagination Implementation
- **Backend**: Consistent pagination metadata across all endpoints
- **Frontend**: Reusable pagination components (`Pagination`, `LibraryPagination`)
- **API Integration**: All services updated to handle paginated responses
- **State Management**: Zustand store tracks pagination state for search results

### API Pagination Format
All paginated endpoints return:
```json
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 50,
    "page_size": 10,
    "has_next": true,
    "has_previous": false,
    "start_index": 0,
    "end_index": 10
  }
}
```

### Testing
- **Backend**: pytest with comprehensive test coverage including pagination tests
- **Frontend**: ESLint for code quality
- **Database**: Test database isolation via pytest fixtures