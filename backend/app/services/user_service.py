from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import timedelta
from email_validator import validate_email, EmailNotValidError

from app.models.user import User
from app.services.base_service import BaseService
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate
from app.core.config import settings


class UserService(BaseService[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def create(self, user_data: UserCreate):
        """Validates email, hashes password, and creates a new user."""

        try:
            validated = validate_email(user_data.email)
            normalized_email = validated.normalized

            if self.get_user_by_email(normalized_email):
                raise HTTPException(status_code=400, detail="Email is already registered")

            from app.core.security import hash_password

            hashed_password = hash_password(user_data.password)
            db_user = User(
                name=user_data.name,
                email=normalized_email,
                password=hashed_password,
                is_active=False
            )

            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            print(f"Error in UserService.create: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def authenticate_user(self, email: str, password: str):
        """Authenticates user and returns the user object if credentials are valid."""

        from app.core.security import verify_password

        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid email or password")
        return user

    def generate_token(self, user_id: int):
        """Generates a JWT access token."""

        from app.core.security import create_access_token

        token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token({"sub": str(user_id)}, expires_delta=token_expires)

    def get_user_by_email(self, email: str) -> User:
        """Retrieves a user by their email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Retrieves a user by their ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_profile(self, user_id: int, profile_data: UserProfileUpdate) -> User:
        """Update user profile information."""
        user = self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if profile_data.name is not None:
            user.name = profile_data.name
        
        if profile_data.profile_picture is not None:
            # Delete old profile picture if it exists
            if user.profile_picture:
                from app.core.file_utils import delete_profile_picture
                delete_profile_picture(user.profile_picture)
            user.profile_picture = profile_data.profile_picture
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        user = self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if user_data.name is not None:
            user.name = user_data.name
        
        if user_data.email is not None:
            try:
                validated = validate_email(user_data.email)
                normalized_email = validated.normalized
                
                # Check if email is already taken by another user
                existing_user = self.get_user_by_email(normalized_email)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(status_code=400, detail="Email is already registered")
                
                user.email = normalized_email
            except EmailNotValidError:
                raise HTTPException(status_code=400, detail="Invalid email format")
        
        self.db.commit()
        self.db.refresh(user)
        return user