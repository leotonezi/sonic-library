from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type hint for models

class BaseService(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, obj_id: int):
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def get_by_email(self, email: str):
        return self.db.query(self.model).filter(self.model.email == email).first()

    def get_all(self):
        logger.warning(
            "get_all() called on %s — this returns unbounded results and is deprecated. "
            "Use get_paginated() instead.",
            self.model.__name__,
        )
        return self.db.query(self.model).all()

    def get_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list, int]:
        """Return a page of results and the total row count.

        ``page_size`` is silently clamped to ``settings.MAX_PAGE_SIZE`` so that
        callers cannot request unbounded result sets.
        """
        from app.core.config import settings

        page_size = min(page_size, settings.MAX_PAGE_SIZE)
        page_size = max(page_size, 1)

        query = self.db.query(self.model)
        total_count: int = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total_count

    def update(self, obj_id: int, obj_in: dict):
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return None

        if 'updated_at' in self.model.__table__.columns:
            obj_in['updated_at'] = datetime.now(UTC)

        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create(self, obj_in: dict):
        now = datetime.now(UTC)

        if 'created_at' in self.model.__table__.columns and 'created_at' not in obj_in:
            obj_in['created_at'] = now

        if 'updated_at' in self.model.__table__.columns and 'updated_at' not in obj_in:
            obj_in['updated_at'] = now

        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
