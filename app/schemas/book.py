from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class BookBase(BaseModel):
    title: str = Field(..., max_length=255)
    author: str
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    short_description: str

    def __init__(self, **data):
        super().__init__(**data)
        self.short_description = (self.description[:50] + "...") if self.description else "No description available"

    class Config:
        from_attributes = True