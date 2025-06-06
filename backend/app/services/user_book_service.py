from app.models.user_book import UserBook
from app.services.base_service import BaseService
from app.models.user_book import StatusEnum
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

class UserBookService(BaseService[UserBook]):
    def __init__(self, db):
        super().__init__(db, UserBook)

    def get_by_user(self, user_id: int):
        return self.db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_books_by_user(self, user_id: int):
        """
        Return all UserBook entries for the user with the related Book loaded.
        """
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.book))  # eager load the Book relationship
            .filter(self.model.user_id == user_id)
            .all()
        )
    def get_by_book(self, book_id: int):
        return self.db.query(self.model).filter(self.model.book_id == book_id).all()

    def get_by_user_and_book(self, user_id: int, book_id: int):
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.book_id == book_id)
            .first()
        )

    def update_status(self, user_id: int, book_id: int, status):
        user_book = self.get_by_user_and_book(user_id, book_id)
        if user_book:
            user_book.status = status
            self.db.commit()
            self.db.refresh(user_book)
        return user_book

    def delete_by_id(self, user_book_id: int):
        user_book = self.db.query(self.model).filter(self.model.id == user_book_id).first()
        if user_book:
            self.db.delete(user_book)
            self.db.commit()
        return user_book

    def get_by_external_book(self, external_book_id: str):
      return self.db.query(self.model).filter(self.model.external_book_id == external_book_id).first()

    def get_by_internal_or_external_book(self, external_book_id: str = None, internal_book_id: int = None):
        query = self.db.query(self.model)
        if external_book_id and internal_book_id:
            return query.filter(
                or_(
                    self.model.external_book_id == external_book_id,
                    self.model.id == internal_book_id
                )
            ).first()
        elif external_book_id:
            return query.filter(self.model.external_book_id == external_book_id).first()
        elif internal_book_id:
            return query.filter(self.model.id == internal_book_id).first()
        else:
            return None

    def get_by_user_and_external_book(self, user_id: int, external_book_id: str):
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.external_book_id == external_book_id)
            .first()
        )

    def get_by_user_and_status(self, user_id: int, status: StatusEnum):
      return (
          self.db.query(self.model)
          .filter(
              self.model.user_id == user_id,
              self.model.status == status
          )
          .all()
      )
