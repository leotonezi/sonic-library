from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.base_schema import ApiResponse
from app.core.security import get_current_user
from app.models.user import User
from app.core.logging_decorator import log_exceptions

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency function to inject UserService."""
    return UserService(db)

@router.post("/", response_model=ApiResponse[UserResponse])
@log_exceptions("POST /users")
def create(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    try:
        user_obj = user_service.create(user)
        return ApiResponse(data=UserResponse.model_validate(user_obj))
    except Exception as e:
        # Log the full error details
        print(f"Error creating user: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

@router.get("/", response_model=ApiResponse[list[UserResponse]])
@log_exceptions("GET /users")
def index(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Get all users (Protected Route)"""
    users = user_service.get_all()
    return ApiResponse(data=[UserResponse.model_validate(u) for u in users])

@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    """Get details of the logged-in user (Protected Route)"""
    return ApiResponse(data=UserResponse.model_validate(current_user))

@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
@log_exceptions("GET /users/{user_id}")
def get(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a user by ID (Protected Route)"""
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(data=UserResponse.model_validate(user))