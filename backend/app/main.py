from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import books, users, reviews, recommendations, auth, user_books, admin
from app.core.logging_config import setup_logging
from app.core.file_utils import UPLOAD_DIR
from app.core.exceptions import RateLimitExceeded
import logging

setup_logging()
logger = logging.getLogger("sonic")

app = FastAPI(title="SonicLibrary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Dev frontend
        "http://localhost:3001",  # Test frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for profile pictures
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR.parent)), name="uploads")

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "data": None,
            "message": f"Rate limit exceeded. Try again in {exc.retry_after} seconds.",
            "status": "error",
        },
        headers={"Retry-After": str(exc.retry_after)},
    )

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(user_books.router, prefix="/user-books", tags=["User-Books"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])