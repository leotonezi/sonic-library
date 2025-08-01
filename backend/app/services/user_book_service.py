from app.models.user_book import UserBook
from app.services.base_service import BaseService
from app.models.user_book import StatusEnum
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from typing import Tuple, List, Optional

class UserBookService(BaseService[UserBook]):
    def __init__(self, db):
        super().__init__(db, UserBook)

    def get_by_user(self, user_id: int):
        return self.db.query(self.model).filter(self.model.user_id == user_id).all()

    def get_books_by_user(self, user_id: int, status: str | None = None):
        query = (
            self.db.query(self.model)
            .options(joinedload(self.model.book))
            .filter(self.model.user_id == user_id)
        )
        if status:
            query = query.filter(self.model.status == status)
        return query.all()

    def get_books_by_user_paginated(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10, 
        status: Optional[str] = None
    ) -> Tuple[List[UserBook], int, int, int]:
        """
        Get paginated books for a user.
        
        Returns:
            Tuple of (books, total_count, total_pages, current_page)
        """
        query = (
            self.db.query(self.model)
            .options(joinedload(self.model.book))
            .filter(self.model.user_id == user_id)
        )
        
        if status:
            query = query.filter(self.model.status == status)
        
        # Get total count
        total_count = query.count()
        
        # Calculate pagination
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size
        
        # Get paginated results
        books = query.offset(offset).limit(page_size).all()
        
        return books, total_count, total_pages, page

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

    def get_by_internal_or_external_book(self, external_book_id: Optional[str] = None, internal_book_id: Optional[int] = None):
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

    def create(self, obj_in: dict):
        return super().create(obj_in)
