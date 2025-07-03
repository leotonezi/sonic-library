import os
from dotenv import load_dotenv
from pathlib import Path
if Path(".env.test").exists():
    load_dotenv(".env.test", override=True)
else:
    load_dotenv(override=True)
import sys
from sqlalchemy import create_engine, pool
from alembic import context
from logging.config import fileConfig

# Import Base from database setup
from app.core.database import Base

# Explicitly import all models
from app.models.user import User
from app.models.book import Book
from app.models.review import Review
from app.models.user_book import UserBook, StatusEnum
from app.models import *

# Debug: Print all tables and columns registered with Base.metadata
print("[Alembic DEBUG] Tables registered with Base.metadata:")
for table_name, table in Base.metadata.tables.items():
    print(f"  {table_name}: {[col.name for col in table.columns]}")

# Load Alembic configuration
config = context.config

# Assign metadata to Alembic
target_metadata = Base.metadata

# Get database URL - prioritize TEST_DATABASE_URL for tests, then DATABASE_URL, then config
DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set! Please set it in the environment or alembic.ini.")

print("Alembic sqlalchemy.url:", DATABASE_URL)
print("Env DATABASE_URL:", os.environ.get("DATABASE_URL"))
print("Env TEST_DATABASE_URL:", os.environ.get("TEST_DATABASE_URL"))

def run_migrations_online():
    # DATABASE_URL is guaranteed to be a string at this point due to the check above
    engine = create_engine(str(DATABASE_URL), poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()