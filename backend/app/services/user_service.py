from app.models.user import User
from app.services.base_service import BaseService
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import timedelta
from app.core.config import settings

class UserService(BaseService[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def create(self, user_data: UserCreate):
        """Hashes password and creates a new user."""
        from app.core.security import hash_password  # Import inside function

        user_data.password = hash_password(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str):
        """Authenticates user and returns the user object if credentials are valid."""
        from app.core.security import verify_password  # Import inside function

        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid email or password")
        return user

    def generate_token(self, user_id: int):
        """Generates a JWT access token."""
        from app.core.security import create_access_token  # Import inside function

        token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token({"sub": str(user_id)}, expires_delta=token_expires)

    def get_user_by_email(self, email: str) -> User:
        """Retrieves a user by their email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieves a user by their ID."""
        return self.db.query(User).filter(User.id == user_id).first()