from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from dotenv import load_dotenv

import os

if os.getenv("PYTEST_CURRENT_TEST"):
    load_dotenv(".env.test", override=True)
else:
    load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import User, Book, Review, UserBook
    Base.metadata.create_all(bind=engine)


init_db()
