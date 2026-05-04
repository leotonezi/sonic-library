# Backend Tests

## Commands

```bash
pytest                                      # Run all tests
pytest tests/test_books.py                  # Run specific file
pytest tests/test_books.py::test_create_book -v  # Run single test
pytest --cov=app                            # With coverage
```

## Test Infrastructure

Tests use a separate `fastlibrary_test` database, auto-created from the main `DATABASE_URL` by appending `_test`. Works in both Docker and local environments.

### Key Fixtures (in `conftest.py`)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `apply_migrations` | session | Creates test DB if needed, runs Alembic migrations once |
| `db_session` | function | Provides a SQLAlchemy session bound to test DB |
| `client` | function | FastAPI `TestClient` with DB dependency overridden to test DB |
| `clean_database` | function (autouse) | Truncates all tables after each test |

### How it works

1. `TESTING=true` is set at import time
2. Test DB is created by connecting to the `postgres` default DB
3. Alembic migrations run once per session
4. Each test gets a fresh `client` or `db_session`
5. `clean_database` runs after every test — deletes from all tables with FK checks disabled

### DB cleanup order
Tables are cleaned in reverse dependency order:
`reviews → user_books → book_genres → books → genres → users`

## Writing New Tests

- Use the `client` fixture for endpoint/integration tests
- Use the `db_session` fixture for direct DB/service tests
- No need to handle cleanup — `clean_database` is autouse
- Tests run against real PostgreSQL, not mocks

## Test Files

- `test_admin.py` — Admin functionality
- `test_books.py` — Book CRUD and search
- `test_users.py` — User operations
- `test_pagination.py` — Pagination logic
- `test_profile_pictures.py` — Profile picture handling
- `test_circuit_breaker.py` — Circuit breaker pattern
- `test_openai_circuit_breaker.py` — OpenAI API circuit breaker
- `test_rate_limiter.py` — Rate limiting
- `test_multi_user_interactions.py` — Multi-user scenarios
- `test_query_performance.py` — N+1 query regression tests (uses SQLAlchemy event listeners to count queries)
