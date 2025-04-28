from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic
from datetime import datetime

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
        return self.db.query(self.model).all()
    
    def update(self, obj_id: int, obj_in: dict):
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return None

        if 'updated_at' in self.model.__table__.columns:
            obj_in['updated_at'] = datetime.utcnow()

        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create(self, obj_in: dict):
        now = datetime.utcnow()

        if 'created_at' in self.model.__table__.columns and 'created_at' not in obj_in:
            obj_in['created_at'] = now

        if 'updated_at' in self.model.__table__.columns and 'updated_at' not in obj_in:
            obj_in['updated_at'] = now

        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj