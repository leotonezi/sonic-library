from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings
from dotenv import load_dotenv
import logging
import time
import os
from typing import Optional

# Configure logging for database operations
db_logger = logging.getLogger("database")

if os.getenv("PYTEST_CURRENT_TEST"):
    load_dotenv(".env.test", override=True)
else:
    load_dotenv(override=True)

DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Connection pooling configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections that can be created
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    echo=False,  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session with connection pooling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models import User, Book, Review, UserBook
    Base.metadata.create_all(bind=engine)


# Database query monitoring and optimization
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries and monitor database performance."""
    context._query_start_time = time.time()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time and identify slow queries."""
    total = time.time() - context._query_start_time
    
    # Log slow queries (queries taking more than 1 second)
    if total > 1.0:
        db_logger.warning(
            f"Slow query detected ({total:.3f}s): {statement[:200]}..."
        )
    
    # Log all queries in debug mode
    if db_logger.isEnabledFor(logging.DEBUG):
        db_logger.debug(f"Query executed in {total:.3f}s: {statement[:100]}...")


# Connection pool monitoring
def get_pool_status():
    """Get connection pool status for monitoring."""
    pool = engine.pool
    return {
        "pool_size": getattr(pool, 'size', lambda: 0)(),
        "checked_in": getattr(pool, 'checkedin', lambda: 0)(),
        "checked_out": getattr(pool, 'checkedout', lambda: 0)(),
        "overflow": getattr(pool, 'overflow', lambda: 0)(),
        "invalid": getattr(pool, 'invalid', lambda: 0)(),
    }


def log_pool_status():
    """Log connection pool status periodically."""
    status = get_pool_status()
    db_logger.info(f"Connection pool status: {status}")


# Database health check
def check_db_health():
    """Check database connectivity and pool health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        db_logger.error(f"Database health check failed: {e}")
        return False


# init_db()  # Commented out to avoid conflicts with Alembic migrations
