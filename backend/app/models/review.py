from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    rate = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('rate BETWEEN 1 AND 5', name='check_rate_range'),
    )    
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    book = relationship("Book", back_populates="reviews")