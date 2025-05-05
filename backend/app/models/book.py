from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import Enum as SqlEnum
import enum

class GenreEnum(str, enum.Enum):
    FANTASY = "Fantasy"
    SCIENCE_FICTION = "Science Fiction"
    MYSTERY = "Mystery"
    THRILLER = "Thriller"
    ROMANCE = "Romance"
    WESTERN = "Western"
    DYSTOPIAN = "Dystopian"
    CONTEMPORARY = "Contemporary"
    HISTORICAL = "Historical"
    HORROR = "Horror"
    BIOGRAPHY = "Biography"
    AUTOBIOGRAPHY = "Autobiography"
    MEMOIR = "Memoir"
    SELF_HELP = "Self Help"
    HEALTH = "Health"
    TRAVEL = "Travel"
    GUIDE = "Guide"
    RELIGION = "Religion"
    SCIENCE = "Science"
    HISTORY = "History"
    MATH = "Math"
    POETRY = "Poetry"
    ART = "Art"
    COOKING = "Cooking"
    JOURNAL = "Journal"
    DIARY = "Diary"
    COMICS = "Comics"
    GRAPHIC_NOVEL = "Graphic Novel"
    CHILDRENS = "Children's"
    YOUNG_ADULT = "Young Adult"

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(String(1000), nullable=True)
    page_count = Column(Integer, nullable=True)
    published_date = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    isbn = Column(String(13), nullable=True, unique=True)
    image_url = Column(String, nullable=True)
    language = Column(String, nullable=True, default="pt-BR")
    genre = Column(SqlEnum(GenreEnum, name="genre_enum"), nullable=True)

    reviews = relationship("Review", back_populates="book")