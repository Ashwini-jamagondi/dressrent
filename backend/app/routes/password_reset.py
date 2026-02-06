from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from ..database import get_db
from ..models import User
from ..email_config import send_reset_email
import secrets

router = APIRouter()

# Password hashing (if not available from auth.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# Secret key for password reset tokens (use a different one from your main JWT secret)
RESET_SECRET_KEY = "your-reset-secret-key-change-this-in-production"
ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_HOURS = 1

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordResetResponse(BaseModel):
    message: str
    email: str

def create_reset_token(email: str) -> str:
    """Create a password reset token"""
    expire = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    # Add a random string to make token unique even for same email
    random_string = secrets.token_urlsafe(32)
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset",
        "random": random_string
    }
    encoded_jwt = jwt.encode(to_encode, RESET_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_reset_token(token: str) -> str:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, RESET_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request a password reset - sends email with reset link"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    # Always return success even if email doesn't exist (security best practice)
    # This prevents email enumeration attacks
    if not user:
        return {
            "message": "If the email exists, a reset link has been sent",
            "email": request.email
        }
    
    # Create reset token
    reset_token = create_reset_token(user.email)
    
    # Create reset link
    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
    
    # Send email
    try:
        await send_reset_email(user.email, reset_link)  # Only 2 arguments!
        return {
            "message": "Password reset link has been sent to your email",
            "email": request.email
        }
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email. Please try again later."
        )

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using the token"""
    # Verify token
    email = verify_reset_token(request.token)
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate new password
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Hash new password
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {
        "message": "Password has been reset successfully",
        "email": user.email
    }

@router.get("/password-reset/verify-token")
async def verify_reset_token_endpoint(token: str):
    """Verify if a reset token is valid (used by frontend)"""
    try:
        email = verify_reset_token(token)
        return {
            "valid": True,
            "email": email
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )