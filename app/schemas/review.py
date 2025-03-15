from pydantic import BaseModel

class ReviewBase(BaseModel):
    book_id: int
    user_id: int
    content: str

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int

    class Config:
        from_attributes = True