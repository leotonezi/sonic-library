from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, Response
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
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user_service = UserService(db)
    user = user_service.get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is not active")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    return ApiResponse(
        data={"user": {"email": user.email, "name": user.name}},
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

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        path="/"
    )
    return ApiResponse(data=None, status="success", message="Logged out")