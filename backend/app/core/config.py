import os
from dotenv import load_dotenv
from pathlib import Path

# Detect if running tests
is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None

# Load the appropriate .env file
env_file = ".env.test" if is_testing else ".env"
env_path = Path(__file__).resolve().parents[2] / env_file
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "SonicLibrary")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost/fastlibrary")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()