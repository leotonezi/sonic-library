from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.base_schema import ApiResponse

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/token")
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticate user and return JWT token in ApiResponse format."""
    user_service = UserService(db)
    user = user_service.get_user_by_email(form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="User does not exist")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return ApiResponse(
        data={
            "access_token": access_token,
            "token_type": "bearer"
        },
        status="success",
        message="Login successful"
    )