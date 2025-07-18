# core/mail.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel

from app.core.config import settings, is_testing  # assuming you have a settings.py for env variables

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailSchema(BaseModel):
    email: EmailStr

async def send_activation_email(email: EmailStr, activation_link: str):
    # Skip email sending during tests
    if is_testing:
        print(f"[TEST] Email would be sent to {email} with activation link: {activation_link}")
        return
    
    message = MessageSchema(
        subject="Activate your Sonic Library account",
        recipients=[email],
        body=f"""Hi there!<br><br>
        Please click the link below to activate your account:<br><br>
        <a href="{activation_link}">{activation_link}</a><br><br>
        Thanks for joining Sonic Library! 🚀
        """,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)