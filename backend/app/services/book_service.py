from app.models.book import Book
from app.services.base_service import BaseService

class BookService(BaseService[Book]):
    def __init__(self, db):
        super().__init__(db, Book)

    def get_by_title(self, title: str):
        return self.db.query(self.model).filter(self.model.title.ilike(f"%{title}%")).all()