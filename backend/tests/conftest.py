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
# This ensures tests use a separate database from development
DATABASE_URL = settings.DATABASE_URL

# Detect if we're running in Docker (database host is 'db') or locally (database host is 'localhost')
if 'db:5432' in DATABASE_URL:
    # Docker environment
    TEST_DATABASE_URL = DATABASE_URL.replace('/fastlibrary', '/fastlibrary_test')
else:
    # Local environment
    if DATABASE_URL.endswith('/fastlibrary'):
        TEST_DATABASE_URL = DATABASE_URL.replace('/fastlibrary', '/fastlibrary_test')
    else:
        # Fallback: append _test to the database name
        TEST_DATABASE_URL = DATABASE_URL + '_test'

# Create test database engine
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

@pytest.fixture(scope="session")
def apply_migrations() -> Generator:
    """Apply Alembic migrations at the start of testing session."""
    
    # Create test database if it doesn't exist
    try:
        # Connect to default postgres database to create test database
        default_engine = create_engine(DATABASE_URL.rsplit('/', 1)[0] + '/postgres')
        with default_engine.connect() as connection:
            connection.execute(text("COMMIT"))  # Close any open transaction
            connection.execute(text(f"CREATE DATABASE fastlibrary_test"))
    except Exception as e:
        # Database might already exist, which is fine
        print(f"Test database creation note: {e}")
    
    # Set up Alembic configuration for test database
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    
    # Temporarily override environment variables to ensure test database is used
    original_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    print(f"[DEBUG] Alembic config file: {alembic_cfg.config_file_name}")
    print(f"[DEBUG] Alembic sqlalchemy.url: {alembic_cfg.get_main_option('sqlalchemy.url')}")
    
    try:
        # Apply migrations
        command.upgrade(alembic_cfg, "head")
        
        # Verify tables were created
        with test_engine.connect() as connection:
            result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';"))
            tables = [row[0] for row in result]
            print("Tables after migration:", tables)
            
            # Ensure all expected tables exist
            expected_tables = ['users', 'books', 'genres', 'reviews', 'user_books', 'book_genres', 'alembic_version']
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                print(f"Warning: Missing tables: {missing_tables}")
                # Try to create tables using SQLAlchemy
                Base.metadata.create_all(bind=test_engine)
                print("Created missing tables using SQLAlchemy")
    finally:
        # Restore original environment variable
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    yield

    # Don't drop tables at session end - let function-level cleanup handle it
    print("Session ended - tables will be cleaned up by function-level fixtures.")

@pytest.fixture(scope="function")
def db_session(apply_migrations):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(apply_migrations) -> Generator:
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

@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Clean up database between tests."""
    yield
    # Clean up all data after each test
    with test_engine.connect() as connection:
        try:
            # Disable foreign key checks temporarily
            connection.execute(text("SET session_replication_role = replica;"))
            
            # Delete all data from tables in reverse dependency order
            tables = ['reviews', 'user_books', 'book_genres', 'books', 'genres', 'users']
            for table in tables:
                try:
                    connection.execute(text(f"DELETE FROM {table};"))
                except Exception as e:
                    # Table might not exist, which is fine
                    print(f"Note: Could not delete from {table}: {e}")
            
            # Re-enable foreign key checks
            connection.execute(text("SET session_replication_role = DEFAULT;"))
            connection.commit()
        except Exception as e:
            # If cleanup fails, just log it but don't fail the test
            print(f"Database cleanup warning: {e}")
            connection.rollback()
