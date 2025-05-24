from app.models.book import Book, Genre
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from app.services.base_service import BaseService

class BookService(BaseService[Book]):
    def __init__(self, db):
        super().__init__(db, Book)

    def filter_books(self, search: str = None, genre: str = None):
        query = self.db.query(self.model)

        if search:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.author.ilike(f"%{search}%")
                )
            )

        if genre:
            query = query.join(self.model.genres).filter(Genre.name == genre)

        query = query.options(joinedload(self.model.genres))

        return query.all()

    def get_by_external_id(self, external_id: str):
        """
        Get a book by its external_id.

        Args:
            external_id: The external ID of the book to retrieve

        Returns:
            The book if found, None otherwise
        """
        return self.db.query(self.model).filter(self.model.external_id == external_id).first()

    def create(self, obj_in: dict):
        try:
            genre_names = []
            if "genres" in obj_in:
                genres = obj_in.get("genres")
                if isinstance(genres, str):
                    genre_names = [g.strip() for g in genres.split("/") if g.strip()]
                elif isinstance(genres, list):
                    genre_names = genres
                elif genres:
                    genre_names = [str(genres)]

                del obj_in["genres"]

            book = super().create(obj_in)

            if genre_names:
                for genre_name in genre_names:
                    genre = self.db.query(Genre).filter(Genre.name == genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        self.db.add(genre)
                        self.db.flush()

                    book.genres.append(genre)

                self.db.commit()
                self.db.refresh(book)

            return book
        except Exception as e:
            # Log the error with traceback
            import traceback
            print("Error in BookService.create:", e)
            print(traceback.format_exc())
            raise
