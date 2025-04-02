from fastapi import FastAPI
from app.api.v1.endpoints import books, users, reviews, recommendations, auth
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])