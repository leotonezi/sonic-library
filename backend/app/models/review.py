from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    external_book_id = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    rate = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('rate BETWEEN 1 AND 5', name='check_rate_range'),
    )    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "(book_id IS NOT NULL AND external_book_id IS NULL) OR (book_id IS NULL AND external_book_id IS NOT NULL)",
            name="check_one_book_reference"
        ),
        CheckConstraint('rate BETWEEN 1 AND 5', name='check_rate_range'),
    )

    book = relationship("Book", back_populates="reviews")