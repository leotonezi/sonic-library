import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command
import sys
import os
from typing import Generator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.database import Base

# Create test database URL by appending _test to database name
DATABASE_URL = settings.DATABASE_URL

# Create test database engine
test_engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> Generator:
    """Apply Alembic migrations at the start of testing session."""

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    # Apply migrations
    command.upgrade(alembic_cfg, "head")

    # Print tables for debugging
    with test_engine.connect() as connection:
        result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';"))
        print("Tables after migration:", [row[0] for row in result])

    yield

@pytest.fixture(scope="function")
def db_session():
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client() -> Generator:
    """Create a test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_db

    # Override the database dependency
    def override_get_db():
        db = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=test_engine
        )()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear any overrides after the test
    app.dependency_overrides.clear()