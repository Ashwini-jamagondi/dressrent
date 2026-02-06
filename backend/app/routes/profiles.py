from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import shutil
import os
from datetime import datetime
from pathlib import Path

from ..database import get_db
from ..models import User
from ..auth import get_current_user # Changed from ..auth to ..utils.auth
from ..utils.security import verify_password, get_password_hash

router = APIRouter()

# Request models
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Upload directory
UPLOAD_DIR = Path("uploads/profiles")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile - returns all user data including profile photo"""
    print(f"\n📋 Getting profile for user: {current_user.username}")
    print(f"   Profile photo URL: {current_user.profile_photo_url}")
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "address": current_user.address,
        "location": current_user.location,
        "profile_photo_url": current_user.profile_photo_url,
        "created_at": current_user.created_at
    }


@router.put("/me")
async def update_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile details"""
    print(f"\n✏️ Updating profile for user: {current_user.username}")
    
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    if profile.full_name is not None:
        user.full_name = profile.full_name
        print(f"   Updated full_name: {profile.full_name}")
    
    if profile.phone is not None:
        user.phone = profile.phone
        print(f"   Updated phone: {profile.phone}")
    
    if profile.location is not None:
        user.location = profile.location
        print(f"   Updated location: {profile.location}")
    
    if profile.address is not None:
        user.address = profile.address
        print(f"   Updated address: {profile.address}")
    
    db.commit()
    db.refresh(user)
    
    print(f"✅ Profile updated successfully")
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "location": user.location,
            "address": user.address,
            "profile_photo_url": user.profile_photo_url
        }
    }


@router.post("/photo")
async def upload_profile_photo(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile photo - saves permanently to database"""
    print(f"\n📸 User '{current_user.username}' uploading profile photo")
    
    # Validate file type
    if not photo.content_type or not photo.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (5MB max)
    photo.file.seek(0, 2)  # Seek to end
    file_size = photo.file.tell()
    photo.file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    print(f"   File size: {file_size / 1024:.2f} KB")
    
    # Get user from database (refresh to ensure we have latest data)
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete old photo if exists
    if user.profile_photo_url:
        old_path = user.profile_photo_url.lstrip('/')
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f"   Deleted old photo: {old_path}")
            except Exception as e:
                print(f"   Warning: Could not delete old photo: {e}")
    
    # Create unique filename
    file_extension = photo.filename.split('.')[-1] if photo.filename else 'jpg'
    filename = f"profile_{current_user.id}_{int(datetime.now().timestamp())}.{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    print(f"   Saving to: {file_path}")
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        print(f"   File saved successfully")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update user in database - THIS SAVES IT PERMANENTLY
    photo_url = f"/uploads/profiles/{filename}"
    user.profile_photo_url = photo_url
    db.commit()
    db.refresh(user)
    
    print(f"✅ Profile photo saved to database: {photo_url}")
    print(f"   User photo URL now: {user.profile_photo_url}")
    
    return {
        "message": "Profile photo uploaded successfully",
        "photo_url": user.profile_photo_url,
        "profile_photo_url": user.profile_photo_url  # Return both for compatibility
    }


@router.get("/photo")
async def get_profile_photo(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile photo URL"""
    return {
        "photo_url": current_user.profile_photo_url,
        "has_photo": current_user.profile_photo_url is not None
    }


@router.delete("/photo")
async def delete_profile_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete profile photo"""
    print(f"\n🗑️ User '{current_user.username}' deleting profile photo")
    
    if not current_user.profile_photo_url:
        raise HTTPException(status_code=404, detail="No profile photo to delete")
    
    # Delete file
    try:
        filepath = Path(current_user.profile_photo_url.lstrip('/'))
        if filepath.exists():
            filepath.unlink()
            print(f"   File deleted: {filepath}")
    except Exception as e:
        print(f"   Warning: Could not delete file: {e}")
    
    # Update database
    user = db.query(User).filter(User.id == current_user.id).first()
    user.profile_photo_url = None
    db.commit()
    
    print(f"✅ Profile photo deleted from database")
    
    return {"message": "Profile photo deleted"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    print(f"\n🔐 User '{current_user.username}' changing password")
    
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        print(f"❌ Current password incorrect")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password length
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    print(f"✅ Password changed successfully")
    
    return {"message": "Password changed successfully"}