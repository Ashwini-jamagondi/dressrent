from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Order, OrderItem, Cart, Product, User, Booking
from ..schemas import OrderCreate, OrderResponse
from ..auth import get_current_active_user

router = APIRouter()

@router.get("", response_model=List[OrderResponse])
async def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's orders with items and product details"""
    print("\n" + "="*60)
    print("📋 GET ORDERS")
    print("="*60)
    print(f"User: {current_user.username} (ID: {current_user.id})")
    
    # Use joinedload to eagerly load items and products
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.images)  # CHANGED THIS LINE
    ).all()
    
    print(f"Found {len(orders)} orders")
    for order in orders:
        print(f"  Order #{order.id}: ₹{order.total_amount} - {order.status}")
        print(f"    Items: {len(order.items)}")
        for item in order.items:
            print(f"      - {item.product.name}: {item.rental_days} days × ₹{item.price_per_day}")
    print("="*60 + "\n")
    
    return orders

@router.post("", response_model=OrderResponse)
async def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create order from cart items"""
    print("\n" + "="*60)
    print("📦 CREATE ORDER")
    print("="*60)
    
    # Get cart items
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    print(f"Processing {len(cart_items)} cart items")
    
    # Calculate total and validate availability
    total_amount = 0
    order_data = []
    
    for item in cart_items:
        product = item.product
        
        # Check if product is available
        if not product.is_available:
            raise HTTPException(
                status_code=400, 
                detail=f"{product.name} is not available"
            )
        
        # Check for booking conflicts (optional but recommended)
        conflicting_bookings = db.query(Booking).filter(
            Booking.dress_id == product.id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.start_date < item.end_date,
            Booking.end_date > item.start_date
        ).first()
        
        if conflicting_bookings:
            raise HTTPException(
                status_code=400,
                detail=f"{product.name} is already booked for these dates"
            )
        
        # Calculate price
        rental_days = item.rental_days
        item_total = product.price_per_day * rental_days
        total_amount += item_total
        
        order_data.append({
            "product": product,
            "rental_days": rental_days,
            "price_per_day": product.price_per_day,
            "total_price": item_total,
            "start_date": item.start_date,
            "end_date": item.end_date
        })
        
        print(f"✓ {product.name}: {rental_days} days × ₹{product.price_per_day} = ₹{item_total}")
    
    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending",
        start_date=cart_items[0].start_date,
        end_date=cart_items[0].end_date
    )
    db.add(order)
    db.flush()  # Get order ID without committing
    
    # Create order items and bookings
    for data in order_data:
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=data["product"].id,
            rental_days=data["rental_days"],
            price_per_day=data["price_per_day"],
            total_price=data["total_price"]
        )
        db.add(order_item)
        
        # Create booking
        booking = Booking(
            dress_id=data["product"].id,
            renter_id=current_user.id,
            start_date=data["start_date"],
            end_date=data["end_date"],
            total_days=data["rental_days"],
            total_price=data["total_price"],
            security_deposit=data["product"].security_deposit,
            status="pending"
        )
        db.add(booking)
    
    # Clear cart
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    
    db.commit()
    
    # Refresh and reload with relationships
    db.refresh(order)
    order = db.query(Order).filter(Order.id == order.id).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.images)  # ADD .joinedload(Product.images)
    ).first()
    
    print(f"✅ Order #{order.id} created: ₹{total_amount}")
    print("="*60 + "\n")
    
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.images)  # ADD .joinedload(Product.images)
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order