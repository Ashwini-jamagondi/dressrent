from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Cart, Product, User
from ..schemas import CartItemCreate, CartItemResponse
from ..auth import get_current_active_user

router = APIRouter()

@router.get("", response_model=List[CartItemResponse])
async def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's cart"""
    print(f"🛒 GET cart for user: {current_user.username}")
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    return cart_items

@router.post("", response_model=CartItemResponse)
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add dress to cart with rental dates"""
    print("\n" + "="*60)
    print("🛒 ADD TO CART")
    print("="*60)
    print(f"User: {current_user.username} (ID: {current_user.id})")
    print(f"Product ID: {item.product_id}")
    print(f"Rental: {item.rental_start_date} to {item.rental_end_date}")
    
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        print("❌ Product not found")
        raise HTTPException(status_code=404, detail="Dress not found")
    
    print(f"✅ Product found: {product.name}")
    
    # Check dates
    if item.rental_end_date <= item.rental_start_date:
        print("❌ Invalid dates")
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Calculate days
    days = (item.rental_end_date - item.rental_start_date).days
    print(f"Rental days: {days}")
    
    # Check if already in cart
    existing = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == item.product_id
    ).first()
    
    if existing:
        print(f"Updating existing cart item")
        existing.rental_days = days
        existing.start_date = item.rental_start_date
        existing.end_date = item.rental_end_date
        db.commit()
        db.refresh(existing)
        print("✅ Cart updated successfully")
        print("="*60 + "\n")
        return existing
    
    print(f"Creating new cart item")
    cart_item = Cart(
        user_id=current_user.id,
        product_id=item.product_id,
        rental_days=days,  # Changed from quantity
        start_date=item.rental_start_date,  # Changed from rental_start_date
        end_date=item.rental_end_date  # Changed from rental_end_date
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    print("✅ Added to cart successfully")
    print("="*60 + "\n")
    return cart_item

@router.delete("/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove item from cart"""
    cart_item = db.query(Cart).filter(
        Cart.id == cart_item_id,
        Cart.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Removed from cart"}

@router.delete("")
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Clear cart"""
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}