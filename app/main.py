from fastapi import FastAPI
from app.api.v1.endpoints import books

app = FastAPI(title="FastLibrary API")

app.include_router(books.router, prefix="/books", tags=["Books"])