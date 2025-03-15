import os
import sys
import importlib
from sqlalchemy import engine_from_config, pool
from alembic import context
from logging.config import fileConfig

# Import Base from database setup
from app.core.database import Base

# Ensure Alembic finds all models
from app.models.book import Book
from app.models.review import Review
from app.models.user import User

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

# Database connection setup
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()