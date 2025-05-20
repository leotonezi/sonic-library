from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from .book import BookBase

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

class UserBookResponse(UserBookBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

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