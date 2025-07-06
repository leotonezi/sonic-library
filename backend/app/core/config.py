import os
from dotenv import load_dotenv

# Detect if running tests
is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None

load_dotenv(override=True)

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "SonicLibrary")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/fastlibrary")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "")
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "lax"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "local"
    POPULAR_BOOKS_CACHE_TTL: int = int(os.getenv("POPULAR_BOOKS_CACHE_TTL", 3600))  # 1 hour default


settings = Settings()