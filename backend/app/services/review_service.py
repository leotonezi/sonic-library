from sqlalchemy.orm import joinedload
from typing import Tuple, List
from app.models.review import Review
from app.models.user import User
from app.services.base_service import BaseService


class ReviewService(BaseService[Review]):
    def __init__(self, db):
        super().__init__(db, Review)

    def get_by_book(self, book_id: int) -> List[Review]:
        return (
            self.db.query(self.model)
            .options(joinedload(Review.book))
            .filter(self.model.book_id == book_id)
            .all()
        )

    def get_by_external_book(self, book_id: str) -> List[Review]:
        return (
            self.db.query(self.model)
            .options(joinedload(Review.book))
            .filter(self.model.external_book_id == book_id)
            .all()
        )

    def delete_by_id(self, review_id: int):
        review = self.db.query(self.model).filter(self.model.id == review_id).first()
        if review:
            self.db.delete(review)
            self.db.commit()
        return review

    # ------------------------------------------------------------------
    # Non-paginated helpers (kept for internal use; prefer paginated ones)
    # ------------------------------------------------------------------

    def get_by_book_with_user(self, book_id: int) -> list:
        return (
            self.db.query(
                self.model,
                User.name.label("user_name"),
                User.profile_picture.label("user_profile_picture"),
            )
            .join(User, self.model.user_id == User.id)
            .filter(self.model.book_id == book_id)
            .all()
        )

    def get_by_external_book_with_user(self, external_book_id: str) -> list:
        return (
            self.db.query(
                self.model,
                User.name.label("user_name"),
                User.profile_picture.label("user_profile_picture"),
            )
            .join(User, self.model.user_id == User.id)
            .filter(self.model.external_book_id == external_book_id)
            .all()
        )

    # ------------------------------------------------------------------
    # Paginated variants
    # ------------------------------------------------------------------

    def get_all_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> Tuple[list, int]:
        """Return all reviews with pagination.  page_size is clamped by BaseService."""
        return self.get_paginated(page=page, page_size=page_size)

    def get_by_book_with_user_paginated(
        self, book_id: int, page: int = 1, page_size: int = 20
    ) -> Tuple[list, int]:
        """Paginated reviews for a local book, joined with user info."""
        from app.core.config import settings

        page_size = max(1, min(page_size, settings.MAX_PAGE_SIZE))
        base_query = (
            self.db.query(
                self.model,
                User.name.label("user_name"),
                User.profile_picture.label("user_profile_picture"),
            )
            .join(User, self.model.user_id == User.id)
            .filter(self.model.book_id == book_id)
        )
        total_count: int = base_query.count()
        offset = (page - 1) * page_size
        rows = base_query.offset(offset).limit(page_size).all()
        return rows, total_count

    def get_by_external_book_with_user_paginated(
        self, external_book_id: str, page: int = 1, page_size: int = 20
    ) -> Tuple[list, int]:
        """Paginated reviews for an external book, joined with user info."""
        from app.core.config import settings

        page_size = max(1, min(page_size, settings.MAX_PAGE_SIZE))
        base_query = (
            self.db.query(
                self.model,
                User.name.label("user_name"),
                User.profile_picture.label("user_profile_picture"),
            )
            .join(User, self.model.user_id == User.id)
            .filter(self.model.external_book_id == external_book_id)
        )
        total_count: int = base_query.count()
        offset = (page - 1) * page_size
        rows = base_query.offset(offset).limit(page_size).all()
        return rows, total_count
