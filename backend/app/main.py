from fastapi import FastAPI
from app.api.v1.endpoints import books, users, reviews, recommendations, auth, user_books
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger("sonic")

app = FastAPI(title="SonicLibrary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(user_books.router, prefix="/user-books", tags=["User-Books"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])