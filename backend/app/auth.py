
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import TokenData
from .utils.security import SECRET_KEY, ALGORITHM, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
# Add these imports at the top of your auth.py if not already present
from passlib.context import CryptContext

# Add this password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Add these two functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    print("\n" + "="*60)
    print("🔐 AUTHENTICATING USER")
    print("="*60)
    print(f"Token (first 30 chars): {token[:30]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decoded successfully")
        print(f"Payload: {payload}")
        
        username: str = payload.get("sub")
        if username is None:
            print("❌ No username in token payload")
            raise credentials_exception
        
        print(f"Username from token: {username}")
        
        # Check token expiration
        exp = payload.get("exp")
        if exp:
            from datetime import datetime
            exp_time = datetime.fromtimestamp(exp)
            now = datetime.utcnow()
            print(f"Token expires at: {exp_time}")
            print(f"Current time: {now}")
            if exp_time < now:
                print("❌ Token has expired!")
            else:
                time_left = (exp_time - now).total_seconds() / 60
                print(f"✅ Token valid for {time_left:.1f} more minutes")
        
        token_data = TokenData(username=username)
        
    except JWTError as e:
        print(f"❌ JWT Error: {type(e).__name__}: {str(e)}")
        print("="*60 + "\n")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        print(f"❌ User '{token_data.username}' not found in database")
        print("="*60 + "\n")
        raise credentials_exception
    
    print(f"✅ User found: {user.username} (ID: {user.id})")
    print(f"Active: {user.is_active}")
    print("="*60 + "\n")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        print(f"❌ User {current_user.username} is not active")
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user