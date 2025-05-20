from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional
from app.models.book import GenreEnum

class BookBase(BaseModel):
    external_id: Optional[str] = Field(None, max_length=255)
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    page_count: Optional[int] = None
    published_date: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = Field(
        None, description="ISBN-10 or ISBN-13"
    )
    image_url: Optional[str] = None
    language: Optional[str] = Field("pt-BR", max_length=10)
    genre: Optional[GenreEnum] = None

    @validator("isbn")
    def validate_isbn(cls, v):
        if v is None:
            return v
        isbn = v.replace("-", "").replace(" ", "")
        if len(isbn) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 characters long (excluding hyphens/spaces)")
        if not isbn.isdigit():
            raise ValueError("ISBN must contain only digits (excluding hyphens/spaces)")
        return v

    @property
    def short_description(self) -> str:
        if self.description:
            return (self.description[:50] + "...") if len(self.description) > 50 else self.description
        return "No description available"

    model_config = ConfigDict(from_attributes=True)

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)