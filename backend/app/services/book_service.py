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