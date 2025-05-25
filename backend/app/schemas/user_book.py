from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from .book import BookBase, BookResponse

class StatusEnum(str, Enum):
    READ = "READ"
    READING = "READING"
    TO_READ = "TO_READ"

class UserBookBase(BaseModel):
    book_id: Optional[int] = None
    external_book_id: Optional[str] = None
    status: StatusEnum = StatusEnum.TO_READ

class UserBookCreate(UserBookBase):
    book: Optional[BookBase] = None
    pass

class UserBookUpdate(BaseModel):
    status: StatusEnum

class UserBookResponse(BaseModel):
    id: int
    user_id: int
    book_id: Optional[int]
    external_book_id: Optional[str]
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
    book: Optional[BookResponse]

    class Config:
        from_attributes = True

class BookInLibrary(BaseModel):
    id: int
    title: str
    author: str
    cover_image: Optional[str] = None

class UserBookWithDetails(UserBookResponse):
    book: BookInLibrary

    class Config:
        from_attributes = True


def serialize_user_book(user_book) -> UserBookResponse:
    book = user_book.book
    genres = [genre.name for genre in book.genres] if book and book.genres else []
    book_data = {
        **book.__dict__,
        "genres": genres,
    } if book else None

    user_book_data = {
        **user_book.__dict__,
        "book": book_data,
    }
    return UserBookResponse.model_validate(user_book_data)
