from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Enum as SqlEnum
import enum

class StatusEnum(str, enum.Enum):
    READ = "READ"
    READING = "READING"
    TO_READ = "TO_READ"

    @classmethod
    def get_default(cls) -> 'StatusEnum':
        return cls.TO_READ

class UserBook(Base):
    __tablename__ = "user_books"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    external_book_id = Column(String, nullable=True)
    status = Column(
        SqlEnum(StatusEnum, name="status_enum"),
        nullable=False,
        default=StatusEnum.get_default,
        server_default=StatusEnum.TO_READ.value
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User", back_populates="books")
    book = relationship("Book", back_populates="users")

    __table_args__ = (
        # Removed CheckConstraint here
        UniqueConstraint('user_id', 'book_id', name='_user_book_uc'),
        UniqueConstraint('user_id', 'external_book_id', name='_user_external_book_uc'),
    )

    def __repr__(self) -> str:
        return (
            f"<UserBook(user_id={self.user_id}, book_id={self.book_id}, "
            f"external_book_id={self.external_book_id}, status={self.status})>"
        )
