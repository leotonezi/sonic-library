import os
from dotenv import load_dotenv
load_dotenv(override=True)
import sys
import importlib
from sqlalchemy import create_engine, pool
from alembic import context
from logging.config import fileConfig

# Import Base from database setup
from app.core.database import Base

# Ensure Alembic finds all models
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.models.user_book import UserBook
from app.models.user_book import StatusEnum

# Load Alembic configuration
config = context.config
fileConfig(config.config_file_name)

# Ensure Alembic finds all models
models_dir = os.path.join(os.path.dirname(__file__), "../app/models")
sys.path.append(models_dir)

# Auto-import all models in app/models/
for filename in os.listdir(models_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"app.models.{filename[:-3]}"  # Remove `.py`
        importlib.import_module(module_name)

# Assign metadata to Alembic
target_metadata = Base.metadata

# ✅ Use DATABASE_URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/fastlibrary")

def run_migrations_online():
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()