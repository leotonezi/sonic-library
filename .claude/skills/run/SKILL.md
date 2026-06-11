---
description: "Launch Sonic Library via Docker Compose and verify all services are healthy. Use when asked to run, start, or restart the app, or before manually testing a feature."
triggers:
  - run the app
  - start the app
  - start docker
  - bring up services
  - docker-compose up
---

# Run Sonic Library

## Services

| Service  | URL                        | Port |
|----------|----------------------------|------|
| Frontend | http://localhost:3000      | 3000 |
| Backend  | http://localhost:8000/docs | 8000 |
| DB       | PostgreSQL                 | 5432 |
| Redis    | redis://localhost:6379     | 6379 |

## Steps

### 1. Check if already running

```bash
docker ps --format "{{.Names}}\t{{.Status}}" | grep sonic-library
```

If all four containers show `Up`, skip to step 3.

### 2. Start services

Run from project root (`/Users/leonardotonezi/Documents/github/sonic-library`):

```bash
docker-compose up --build -d
```

Wait for output confirming `sonic-library-frontend-1  Started`.

### 3. Smoke-check

```bash
# Backend (expect: Swagger HTML or {"detail":"..."})
curl -sf http://localhost:8000/docs | head -3

# Frontend (expect: HTML with redirect to /login)
curl -sf http://localhost:3000 | grep -o 'Sonic Library'
```

Both must respond. Frontend redirecting to `/login` is correct — the app is protected.

### 4. Stop services (when needed)

```bash
docker-compose down
```

## Notes

- Requires `.env` at project root with `SECRET_KEY`, `OPENAI_API_KEY`, `GOOGLE_BOOKS_API_KEY`, mail vars.
- Test environment uses a separate compose file: `docker-compose -f docker-compose.test.yml up --build` (ports 3001/8001).
- `--build` flag rebuilds images when source changes. Omit for faster restart when only config changed.
