from pydantic import BaseModel, ConfigDict

class ReviewBase(BaseModel):
    book_id: int
    user_id: int
    content: str
    rate: int

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int

    model_config = ConfigDict(from_attributes=True)