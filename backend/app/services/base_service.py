from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic

T = TypeVar("T")  # Type hint for models

class BaseService(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, obj_id: int):
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self):
        return self.db.query(self.model).all()

    def create(self, obj_in: dict):
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj