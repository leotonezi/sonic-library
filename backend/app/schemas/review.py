from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class ReviewBase(BaseModel):
    book_id: int
    user_id: int
    content: str
    rate: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    content: Optional[str] = Field(default=None, min_length=1)
    rate: Optional[int] = Field(default=None, ge=1, le=5)

    class Config:
        from_attributes = True

    @field_validator("content")
    def content_cannot_be_blank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Content cannot be blank")
        return value

class ReviewResponse(ReviewBase):
    id: int

    model_config = ConfigDict(from_attributes=True)