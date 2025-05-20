from app.models.book import Book
from sqlalchemy import or_
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
            query = query.filter(self.model.genre == genre)
        
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