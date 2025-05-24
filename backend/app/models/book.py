from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SqlEnum
from app.models.base import Base
import enum

book_genres = Table(
    "book_genres",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(String(3000), nullable=True)
    page_count = Column(Integer, nullable=True)
    published_date = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    isbn = Column(String(13), nullable=True, unique=True)
    image_url = Column(String, nullable=True)
    language = Column(String, nullable=True, default="pt-BR")
    genres = relationship("Genre", secondary=book_genres, backref="books")

    reviews = relationship("Review", back_populates="book")

    users = relationship("UserBook", back_populates="book", cascade="all, delete-orphan")    