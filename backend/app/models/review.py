from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, DateTime, func, Index
from sqlalchemy.orm import relationship
from app.models.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True, index=True)
    external_book_id = Column(String, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(String, nullable=False)
    rate = Column(Integer, nullable=False, index=True)
    __table_args__ = (
        CheckConstraint('rate BETWEEN 1 AND 5', name='check_rate_range'),
        # Composite indexes for common query patterns
        Index('idx_book_user', 'book_id', 'user_id'),
        Index('idx_external_book_user', 'external_book_id', 'user_id'),
        Index('idx_book_rate', 'book_id', 'rate'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    book = relationship("Book", back_populates="reviews")
