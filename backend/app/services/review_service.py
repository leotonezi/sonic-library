from app.models.review import Review
from app.models.user import User
from app.services.base_service import BaseService

class ReviewService(BaseService[Review]):
    def __init__(self, db):
        super().__init__(db, Review)

    def get_by_book(self, book_id: int):
        return self.db.query(self.model).filter(self.model.book_id == book_id).all()

    def get_by_external_book(self, book_id: str):
        return self.db.query(self.model).filter(self.model.external_book_id == book_id).all()

    def delete_by_id(self, review_id: int):
        review = self.db.query(self.model).filter(self.model.id == review_id).first()
        if review:
            self.db.delete(review)
            self.db.commit()
        return review

    def get_by_book_with_user(self, book_id: int):
        return (
            self.db.query(self.model, User.name.label("user_name"))
            .join(User, self.model.user_id == User.id)
            .filter(self.model.book_id == book_id)
            .all()
        )
