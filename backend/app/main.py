from fastapi import FastAPI
from app.api.v1.endpoints import books, users, auth

app = FastAPI(title="SonicLibrary API")

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])