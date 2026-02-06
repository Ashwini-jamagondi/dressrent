from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime
from ..database import get_db
from ..models import ProductImage, Product, User
from ..schemas import ProductImageCreate, ProductImageResponse
from ..auth import get_current_active_user

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/{product_id}")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a product image"""
    # Check if product exists and user is owner
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed")
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = file.filename.split(".")[-1]
    filename = f"product_{product_id}_{timestamp}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # If this is primary image, unset other primary images
    if is_primary:
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        ).update({"is_primary": False})
    
    # Create database record
    image = ProductImage(
        product_id=product_id,
        image_url=f"/{file_path}",
        is_primary=is_primary
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return {
        "id": image.id,
        "image_url": image.image_url,
        "is_primary": image.is_primary,
        "message": "Image uploaded successfully"
    }

@router.post("/{product_id}", response_model=ProductImageResponse)
async def add_product_image(
    product_id: int,
    image: ProductImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add product image URL"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # If primary, unset others
    if image.is_primary:
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        ).update({"is_primary": False})
    
    db_image = ProductImage(
        product_id=product_id,
        image_url=image.image_url,
        is_primary=image.is_primary
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.get("/{product_id}", response_model=List[ProductImageResponse])
async def get_product_images(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all images for a product"""
    images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    return images

@router.delete("/{image_id}")
async def delete_product_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a product image"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    product = db.query(Product).filter(Product.id == image.product_id).first()
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete file if it exists
    if os.path.exists(image.image_url.lstrip("/")):
        os.remove(image.image_url.lstrip("/"))
    
    db.delete(image)
    db.commit()
    return {"message": "Image deleted"}

@router.put("/{image_id}/set-primary")
async def set_primary_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Set image as primary"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    product = db.query(Product).filter(Product.id == image.product_id).first()
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Unset other primary images
    db.query(ProductImage).filter(
        ProductImage.product_id == image.product_id,
        ProductImage.is_primary == True
    ).update({"is_primary": False})
    
    image.is_primary = True
    db.commit()
    return {"message": "Primary image updated"}