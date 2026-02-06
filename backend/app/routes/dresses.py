from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import Dress, User
from ..auth import get_current_active_user
import shutil
import os
from datetime import datetime

router = APIRouter()

@router.post("/")
async def create_dress(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    size: str = Form(...),
    color: str = Form(...),
    price_per_day: float = Form(...),
    security_deposit: float = Form(...),
    condition: str = Form(...),
    brand: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dress listing"""
    # Image upload logic
    image_url = None
    if image:
        # Save image logic here
        pass
    
    # Create dress in database
    new_dress = Dress(
        name=name,
        description=description,
        category=category,
        size=size,
        color=color,
        brand=brand,
        price_per_day=price_per_day,
        security_deposit=security_deposit,
        condition=condition,
        location=location,
        image_url=image_url,
        is_available=is_available,
        owner_id=current_user.id
    )
    
    db.add(new_dress)
    db.commit()
    db.refresh(new_dress)
    
    return new_dress