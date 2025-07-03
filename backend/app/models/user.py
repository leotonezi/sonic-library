from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)

    books = relationship("UserBook", back_populates="user", cascade="all, delete-orphan")