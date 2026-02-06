from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Product, User
from ..schemas import ProductCreate, ProductUpdate, ProductResponse
from ..auth import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pathlib import Path
import shutil
import os
from datetime import datetime

router = APIRouter()

@router.get("/products/my/listings", response_model=List[ProductResponse])
async def get_my_dresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's dress listings"""
    from sqlalchemy.orm import joinedload
    
    # Load products with owner relationship
    dresses = db.query(Product).options(joinedload(Product.owner)).filter(
        Product.owner_id == current_user.id
    ).all()
    
    # Build response with owner info - RETURN DICTIONARIES, NOT OBJECTS
    result = []
    for product in dresses:
        product_dict = {
            "id": product.id,
            "owner_id": product.owner_id,
            "owner_username": product.owner.username if product.owner else "Unknown",
            "name": product.name,
            "description": product.description,
            "price_per_day": product.price_per_day,
            "category": product.category,
            "size": product.size,
            "color": product.color,
            "brand": product.brand,
            "condition": product.condition,
            "security_deposit": product.security_deposit,
            "location": product.location,
            "image_url": product.image_url,
            "is_available": product.is_available,
            "created_at": product.created_at,
        }
        result.append(product_dict)
    
    return result


@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    size: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all dresses with filters and owner information"""
    from sqlalchemy.orm import joinedload
    
    # Always load the owner relationship
    query = db.query(Product).options(joinedload(Product.owner))
    
    if category:
        query = query.filter(Product.category == category)
    
    if size:
        query = query.filter(Product.size == size)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.offset(skip).limit(limit).all()
    
    # Build response with owner info - make sure owner exists
    result = []
    for product in products:
        product_dict = {
            "id": product.id,
            "owner_id": product.owner_id,
            "owner_username": product.owner.username if product.owner else "Unknown",  # This line is critical
            "name": product.name,
            "description": product.description,
            "price_per_day": product.price_per_day,
            "category": product.category,
            "size": product.size,
            "color": product.color,
            "brand": product.brand,
            "condition": product.condition,
            "security_deposit": product.security_deposit,
            "location": product.location,
            "image_url": product.image_url,
            "is_available": product.is_available,
            "created_at": product.created_at,
        }
        result.append(product_dict)
    
    return result

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    size: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all dresses with filters and owner information"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Product).options(joinedload(Product.owner))
    
    if category:
        query = query.filter(Product.category == category)
    
    if size:
        query = query.filter(Product.size == size)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.offset(skip).limit(limit).all()
    
    # Manually build response with owner info
    result = []
    for product in products:
        product_dict = {
            "id": product.id,
            "owner_id": product.owner_id,
            "owner_username": product.owner.username if product.owner else "Unknown",  # This is correct!
            "name": product.name,
            "description": product.description,
            "price_per_day": product.price_per_day,
            "category": product.category,
            "size": product.size,
            "color": product.color,
            "brand": product.brand,
            "condition": product.condition,
            "security_deposit": product.security_deposit,
            "location": product.location,
            "image_url": product.image_url,
            "is_available": product.is_available,
            "created_at": product.created_at,
        }
        result.append(product_dict)
    
    return result
async def notify_matching_requests(db: Session, new_dress):
    """Find and notify users with matching requests"""
    from ..models import DressRequest, Notification, RequestStatus
    
    print(f"\n🔔 Checking matching requests for: {new_dress.name}")
    
    # Get all PENDING requests (use DressRequest, not Request!)
    open_requests = db.query(DressRequest).filter(
        DressRequest.status == RequestStatus.PENDING  # Use ENUM not string
    ).all()
    
    matched_count = 0
    for request in open_requests:
        # Skip owner's own requests
        if request.user_id == new_dress.owner_id:
            continue
        
        # Check if dress matches
        matches = False
        
        # Check dress type/category
        if request.dress_type:
            dress_type_lower = request.dress_type.lower()
            dress_name_lower = new_dress.name.lower()
            dress_category_lower = (new_dress.category or "").lower()
            
            if (dress_type_lower in dress_name_lower or 
                dress_name_lower in dress_type_lower or
                dress_type_lower in dress_category_lower or
                dress_category_lower in dress_type_lower):
                matches = True
        
        # Check size if specified
        if matches and request.size and new_dress.size:
            if request.size.upper() == new_dress.size.upper():
                matches = True
            else:
                matches = False
        
        # Check color if specified (DressRequest uses 'color' not 'color_preference')
        if matches and request.color and new_dress.color:
            if request.color.lower() in new_dress.color.lower():
                matches = True
            else:
                matches = False
        
        # Check budget if specified
        if matches and request.budget_max:
            if new_dress.price_per_day <= request.budget_max:
                matches = True
            else:
                matches = False
        
        if matches:
            # Create notification
            notification = Notification(
                user_id=request.user_id,
                type="dress_match",
                title="New Dress Match!",
                message=f"'{new_dress.name}' matches your '{request.dress_type}' request!",
                related_id=new_dress.id,
                request_id=request.id,
                is_read=False
            )
            db.add(notification)
            matched_count += 1
            print(f"   ✅ Matched request #{request.id} for user #{request.user_id}")
    
    if matched_count > 0:
        db.commit()
        print(f"   ✅ Notified {matched_count} users")
    else:
        print(f"   ℹ️ No matching requests found")
@router.post("/products", response_model=ProductResponse)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price_per_day: float = Form(...),
    category: str = Form(...),
    security_deposit: float = Form(...),
    size: str = Form(""),
    color: str = Form(""),
    brand: str = Form(""),
    condition: str = Form(""),
    location: str = Form(""),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List a new dress for rent with optional image"""
    from sqlalchemy.orm import joinedload
    
    # Handle image upload
    image_url = None
    if image and image.filename:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        file_extension = os.path.splitext(image.filename)[1]
        filename = f"product_{current_user.id}_{int(datetime.now().timestamp())}{file_extension}"
        file_path = Path("uploads/products") / filename
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_url = f"/uploads/products/{filename}"
        print(f"✅ Image saved: {image_url}")
    
    db_product = Product(
        owner_id=current_user.id,
        name=name,
        description=description,
        price_per_day=price_per_day,
        category=category,
        security_deposit=security_deposit,
        size=size or None,
        color=color or None,
        brand=brand or None,
        condition=condition or None,
        location=location or None,
        image_url=image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Notify matching requests
    await notify_matching_requests(db, db_product)
    
    # Load owner relationship
    db_product = db.query(Product).options(joinedload(Product.owner)).filter(
        Product.id == db_product.id
    ).first()
    
    return {
        "id": db_product.id,
        "owner_id": db_product.owner_id,
        "owner_username": db_product.owner.username if db_product.owner else "Unknown",
        "name": db_product.name,
        "description": db_product.description,
        "price_per_day": db_product.price_per_day,
        "category": db_product.category,
        "size": db_product.size,
        "color": db_product.color,
        "brand": db_product.brand,
        "condition": db_product.condition,
        "security_deposit": db_product.security_deposit,
        "location": db_product.location,
        "image_url": db_product.image_url,
        "is_available": db_product.is_available,
        "created_at": db_product.created_at,
    }
# NEW: Update endpoint with image support
@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price_per_day: float = Form(None),
    category: str = Form(None),
    security_deposit: float = Form(None),
    size: str = Form(None),
    color: str = Form(None),
    brand: str = Form(None),
    condition: str = Form(None),
    location: str = Form(None),
    is_available: bool = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a dress (owner only) with optional image upload"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Dress not found")
    
    if db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Handle image upload if provided
    if image and image.filename:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Delete old image if exists
        if db_product.image_url:
            old_image_path = Path(".") / db_product.image_url.lstrip('/')
            if old_image_path.exists():
                old_image_path.unlink()
        
        file_extension = os.path.splitext(image.filename)[1]
        filename = f"product_{current_user.id}_{int(datetime.now().timestamp())}{file_extension}"
        file_path = Path("uploads/products") / filename
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        db_product.image_url = f"/uploads/products/{filename}"
        print(f"✅ Image updated: {db_product.image_url}")
    
    # Update other fields if provided
    if name is not None:
        db_product.name = name
    if description is not None:
        db_product.description = description
    if price_per_day is not None:
        db_product.price_per_day = price_per_day
    if category is not None:
        db_product.category = category
    if security_deposit is not None:
        db_product.security_deposit = security_deposit
    if size is not None:
        db_product.size = size
    if color is not None:
        db_product.color = color
    if brand is not None:
        db_product.brand = brand
    if condition is not None:
        db_product.condition = condition
    if location is not None:
        db_product.location = location
    if is_available is not None:
        db_product.is_available = is_available
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a dress (owner only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Dress not found")
    
    if db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete image file if exists
    if db_product.image_url:
        image_path = Path(".") / db_product.image_url.lstrip('/')
        if image_path.exists():
            image_path.unlink()
    
    db.delete(db_product)
    db.commit()
    return {"message": "Dress deleted successfully"}
# In your products.py or notifications.py router

from ..models import Notification, Request

@router.post("/products/upload-for-request/{request_id}")
async def upload_matching_dress(
    request_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price_per_day: float = Form(...),
    category: str = Form(...),
    security_deposit: float = Form(...),
    size: str = Form(""),
    color: str = Form(""),
    brand: str = Form(""),
    condition: str = Form(""),
    location: str = Form(""),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a dress matching a customer request"""
    from sqlalchemy.orm import joinedload
    
    # Get the request
    dress_request = db.query(Request).filter(Request.id == request_id).first()
    if not dress_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Handle image upload
    image_url = None
    if image and image.filename:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        file_extension = os.path.splitext(image.filename)[1]
        filename = f"product_{current_user.id}_{int(datetime.now().timestamp())}{file_extension}"
        file_path = Path("uploads/products") / filename
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_url = f"/uploads/products/{filename}"
    
    # Create the product
    db_product = Product(
        owner_id=current_user.id,
        name=name,
        description=description,
        price_per_day=price_per_day,
        category=category,
        security_deposit=security_deposit,
        size=size or None,
        color=color or None,
        brand=brand or None,
        condition=condition or None,
        location=location or None,
        image_url=image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create notification for the customer
    notification = Notification(
        user_id=dress_request.user_id,
        type="dress_match",
        title="🎉 Perfect Match Found!",
        message=f"{current_user.username} uploaded a dress matching your request for {dress_request.dress_type}!",
        related_id=db_product.id
    )
    db.add(notification)
    db.commit()
    
    # Load owner relationship for response
    db_product = db.query(Product).options(joinedload(Product.owner)).filter(
        Product.id == db_product.id
    ).first()
    
    return {
        "id": db_product.id,
        "owner_id": db_product.owner_id,
        "owner_username": db_product.owner.username if db_product.owner else "Unknown",
        "name": db_product.name,
        "description": db_product.description,
        "price_per_day": db_product.price_per_day,
        "category": db_product.category,
        "size": db_product.size,
        "color": db_product.color,
        "brand": db_product.brand,
        "condition": db_product.condition,
        "security_deposit": db_product.security_deposit,
        "location": db_product.location,
        "image_url": db_product.image_url,
        "is_available": db_product.is_available,
        "created_at": db_product.created_at,
    }