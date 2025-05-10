import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.database import Base

# Create test database engine
test_engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply Alembic migrations before tests."""
    # Drop all existing tables and recreate schema
    with test_engine.connect() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.commit()

    # Apply migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield

    # Cleanup after tests (optional)
    with test_engine.connect() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.commit()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

    # Cleanup after test
    Base.metadata.drop_all(bind=test_engine)