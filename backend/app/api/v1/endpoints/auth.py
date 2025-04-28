from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.services.user_service import UserService
from .users import get_user_service
from app.core.security import verify_password, create_access_token, create_activation_token, verify_activation_token
from app.core.config import settings
from app.schemas.user import UserCreate
from app.schemas.base_schema import ApiResponse
from app.core.mail import send_activation_email
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/token")
async def login_for_access_token(
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
    
    if not user.is_active:
        activation_token = create_activation_token(user.email)
        activation_link = f"{settings.BACKEND_URL}/auth/activate?token={activation_token}"

        await send_activation_email(user.email, activation_link)

        raise HTTPException(
            status_code=401,
            detail="User is not active yet. A new activation email has been sent. Please, check your inbox."
        )

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

@router.post("/signup", response_model=ApiResponse[str])
async def signup(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    user_service: UserService = Depends(get_user_service),
):
    """Signup a new user and send activation email (Public Endpoint)"""
    existing_user = user_service.get_by_email(email)
    if existing_user:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/signup?error=email_registered",
            status_code=303
        )


    user_obj = user_service.create(UserCreate(name=name, email=email, password=password))

    activation_token = create_activation_token(user_obj.email)
    activation_link = f"{settings.BACKEND_URL}/users/activate?token={activation_token}"

    background_tasks.add_task(send_activation_email, email, activation_link)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/login?signup_success=true",
        status_code=303
    )

@router.get("/activate", response_model=ApiResponse[str])
def activate_account(
    token: str,
    user_service: UserService = Depends(get_user_service),
):
    """Activate user account with a valid token (Public Endpoint)"""
    try:
        email = verify_activation_token(token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired activation token.")

    user = user_service.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.is_active:
        return ApiResponse(data="Account already activated.")

    user.is_active = True
    user_service.db.commit()

    return ApiResponse(data="Account activated successfully.")