import os
import sys
from dotenv import load_dotenv

# Detect if running tests
is_testing = (
    os.getenv("PYTEST_CURRENT_TEST") is not None or
    os.getenv("TESTING") == "true" or
    "pytest" in sys.modules or
    "test" in sys.argv[0] if sys.argv else False
)

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
    MAIL_DISABLED: bool = os.getenv("MAIL_DISABLED", "false").lower() == "true"
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "lax"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "local"
    POPULAR_BOOKS_CACHE_TTL: int = int(os.getenv("POPULAR_BOOKS_CACHE_TTL", 3600))  # 1 hour default
    @property
    def ADMIN_EMAILS(self) -> list[str]:
        raw = os.getenv("ADMIN_EMAILS", "admin@sonic.com")
        return [e.strip().lower() for e in raw.split(",") if e.strip()]
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SEARCH_RATE_LIMIT: int = int(os.getenv("SEARCH_RATE_LIMIT", 30))
    SEARCH_RATE_LIMIT_WINDOW: int = int(os.getenv("SEARCH_RATE_LIMIT_WINDOW", 60))
    GOOGLE_BOOKS_GLOBAL_RATE_LIMIT: int = int(os.getenv("GOOGLE_BOOKS_GLOBAL_RATE_LIMIT", 100))
    CB_GOOGLE_FAILURE_THRESHOLD: int = int(os.getenv("CB_GOOGLE_FAILURE_THRESHOLD", 5))
    CB_GOOGLE_RECOVERY_TIMEOUT: int = int(os.getenv("CB_GOOGLE_RECOVERY_TIMEOUT", 30))
    CB_OPENAI_FAILURE_THRESHOLD: int = int(os.getenv("CB_OPENAI_FAILURE_THRESHOLD", 5))
    CB_OPENAI_RECOVERY_TIMEOUT: int = int(os.getenv("CB_OPENAI_RECOVERY_TIMEOUT", 30))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", 100))
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", 20))


settings = Settings()