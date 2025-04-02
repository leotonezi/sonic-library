import pytest
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

# Optional: remove old test.db before tests
import os
if os.path.exists("test.db"):
    os.remove("test.db")

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply Alembic migrations before tests."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")