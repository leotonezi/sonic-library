from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    profile_picture: Optional[str] = None
    books_count: int
    reviews_count: int

    model_config = ConfigDict(from_attributes=True)


class AdminUserDetailResponse(AdminUserResponse):
    books: List[dict] = []
    reviews: List[dict] = []

    model_config = ConfigDict(from_attributes=True)


class AdminReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    book_id: Optional[int] = None
    external_book_id: Optional[str] = None
    book_title: Optional[str] = None
    content: str
    rate: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserBookResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    book_id: Optional[int] = None
    external_book_id: Optional[str] = None
    book_title: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminStatsResponse(BaseModel):
    total_users: int
    total_active_users: int
    total_books: int
    total_reviews: int
    total_user_books: int
    avg_rating: float

    model_config = ConfigDict(from_attributes=True)


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class AdminReviewUpdate(BaseModel):
    content: Optional[str] = None
    rate: Optional[int] = Field(default=None, ge=1, le=5)
