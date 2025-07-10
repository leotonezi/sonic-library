from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional

class ReviewBase(BaseModel):
    book_id: Optional[int] = None
    external_book_id: Optional[str] = None
    content: str
    rate: int

class ReviewCreate(ReviewBase):
    user_id: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_book_reference(self):
        if not self.book_id and not self.external_book_id:
            raise ValueError('Either book_id or external_book_id must be provided')
        return self

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
    user_id: int
    user_name: Optional[str] = None
    user_profile_picture: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
