from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, date
from jose import JWTError, jwt
from ..database import get_db
from ..models import Booking, User, Product, DressRequest
from ..utils.security import SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Get current user from token - MUST BE DEFINED FIRST
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def check_date_conflict(db: Session, dress_id: int, start_date: date, end_date: date, exclude_booking_id: int = None):
    """Check if the requested dates conflict with existing bookings"""
    
    query = db.query(Booking).filter(
        Booking.dress_id == dress_id,
        Booking.status.in_(["pending", "confirmed", "active"])  # Only check non-cancelled bookings
    )
    
    # Exclude current booking if updating
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    existing_bookings = query.all()
    
    for booking in existing_bookings:
        # Check for date overlap
        # Overlap occurs if: start_date < booking.end_date AND end_date > booking.start_date
        if start_date < booking.end_date and end_date > booking.start_date:
            return True, booking  # Conflict found
    
    return False, None  # No conflict


@router.get("/product/{product_id}")
async def get_product_bookings(product_id: int, db: Session = Depends(get_db)):
    """Get all bookings for a specific product (for calendar display)"""
    
    bookings = db.query(Booking).filter(
        Booking.dress_id == product_id,
        Booking.status.in_(["pending", "confirmed", "active"])  # Only show active bookings
    ).all()
    
    return [
        {
            "id": booking.id,
            "start_date": booking.start_date.isoformat(),
            "end_date": booking.end_date.isoformat(),
            "status": booking.status
        }
        for booking in bookings
    ]


@router.get("/")
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings for the current user (as renter)"""
    
    print("\n" + "="*60)
    print("📋 GET USER BOOKINGS")
    print("="*60)
    print(f"User: {current_user.username} (ID: {current_user.id})")
    
    bookings = db.query(Booking).filter(
        Booking.renter_id == current_user.id
    ).options(
        joinedload(Booking.dress).joinedload(Product.owner)
    ).order_by(Booking.created_at.desc()).all()
    
    print(f"Found {len(bookings)} bookings")
    print("="*60 + "\n")
    
    # Format response
    result = []
    for booking in bookings:
        booking_dict = {
            "id": booking.id,
            "dress_id": booking.dress_id,
            "renter_id": booking.renter_id,
            "start_date": booking.start_date.isoformat() if booking.start_date else None,
            "end_date": booking.end_date.isoformat() if booking.end_date else None,
            "total_days": booking.total_days,
            "total_price": booking.total_price,
            "security_deposit": booking.security_deposit,
            "status": booking.status,
            "created_at": booking.created_at.isoformat(),
            "dress": None
        }
        
        # Add dress info
        if booking.dress:
            booking_dict["dress"] = {
                "id": booking.dress.id,
                "name": booking.dress.name,
                "owner_id": booking.dress.owner_id,
                "owner": {
                    "id": booking.dress.owner.id,
                    "username": booking.dress.owner.username
                } if booking.dress.owner else None
            }
        
        result.append(booking_dict)
    
    return result


@router.get("/owner")
async def get_owner_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings for dresses owned by current user (MY ORDERS)"""
    
    print("\n" + "="*60)
    print("📋 GET OWNER BOOKINGS (MY ORDERS)")
    print("="*60)
    print(f"Owner: {current_user.username} (ID: {current_user.id})")
    
    bookings = db.query(Booking).join(Product).filter(
        Product.owner_id == current_user.id
    ).options(
        joinedload(Booking.dress),
        joinedload(Booking.renter)
    ).order_by(Booking.created_at.desc()).all()
    
    print(f"Found {len(bookings)} bookings for owner's dresses")
    print("="*60 + "\n")
    
    result = []
    for booking in bookings:
        booking_dict = {
            "id": booking.id,
            "dress_id": booking.dress_id,
            "renter_id": booking.renter_id,
            "start_date": booking.start_date.isoformat() if booking.start_date else None,
            "end_date": booking.end_date.isoformat() if booking.end_date else None,
            "total_days": booking.total_days,
            "total_price": booking.total_price,
            "security_deposit": booking.security_deposit,
            "status": booking.status,
            "created_at": booking.created_at.isoformat(),
            "dress": {
                "id": booking.dress.id,
                "name": booking.dress.name
            } if booking.dress else None,
            "renter": {
                "id": booking.renter.id,
                "username": booking.renter.username,
                "email": booking.renter.email
            } if booking.renter else None
        }
        result.append(booking_dict)
    
    return result
from ..models import Booking, User, Product, DressRequest, RequestStatus

@router.post("/")
async def create_booking(
    dress_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new booking"""
    
    print("\n" + "="*60)
    print("📝 CREATE BOOKING")
    print("="*60)
    print(f"User: {current_user.username}")
    print(f"Dress ID: {dress_id}")
    print(f"Period: {start_date} to {end_date}")
    
    # Get the dress
    dress = db.query(Product).filter(Product.id == dress_id).first()
    if not dress:
        raise HTTPException(status_code=404, detail="Dress not found")
    
    # Check if user is trying to book their own dress
    if dress.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot book your own dress")
    
    # Validate dates
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Check for date conflicts
    has_conflict, conflicting_booking = check_date_conflict(db, dress_id, start_date, end_date)
    if has_conflict:
        conflict_start = conflicting_booking.start_date.strftime("%Y-%m-%d")
        conflict_end = conflicting_booking.end_date.strftime("%Y-%m-%d")
        raise HTTPException(
            status_code=400, 
            detail=f"These dates conflict with an existing booking ({conflict_start} to {conflict_end}). Please choose different dates."
        )
    
    # Calculate total days
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        raise HTTPException(status_code=400, detail="Invalid date range")
    
    # Calculate price
    total_price = dress.price_per_day * total_days
    
    # Create booking
    booking = Booking(
        dress_id=dress_id,
        renter_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        total_price=total_price,
        security_deposit=dress.security_deposit or 0,
        status="pending"
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    
    # ✅ AUTO-DELETE MATCHING REQUESTS AFTER BOOKING
    # ✅ AUTO-DELETE MATCHING REQUESTS AFTER BOOKING
    try:
        print(f"\n🔍 Looking for matching requests to delete...")
        print(f"   User: {current_user.username} (ID: {current_user.id})")
        print(f"   Booked Dress: {dress.name}")
        print(f"   Category: {dress.category}")
        
        # Find ALL pending requests from this user (using ENUM)
        all_requests = db.query(DressRequest).filter(
            DressRequest.user_id == current_user.id,
            DressRequest.status == RequestStatus.PENDING  # ✅ Use ENUM not string!
        ).all()
        
        print(f"   Found {len(all_requests)} pending requests for this user")
        
        deleted_count = 0
        for request in all_requests:
            should_delete = False
            
            # Match by dress type/category
            if request.dress_type:
                dress_type_lower = request.dress_type.lower()
                dress_name_lower = dress.name.lower()
                dress_category_lower = (dress.category or "").lower()
                
                if (dress_type_lower in dress_name_lower or 
                    dress_name_lower in dress_type_lower or
                    dress_type_lower in dress_category_lower or
                    dress_category_lower in dress_type_lower):
                    should_delete = True
                    print(f"   ✓ Request #{request.id} matches: '{request.dress_type}' ≈ '{dress.name}'")
            
            if should_delete:
                # Check size if specified
                if request.size and dress.size:
                    if request.size.upper() != dress.size.upper():
                        should_delete = False
                        print(f"   ✗ Size mismatch: {request.size} != {dress.size}")
                
                # Check color if specified (DressRequest uses 'color' not 'color_preference')
                if should_delete and request.color and dress.color:
                    if request.color.lower() not in dress.color.lower():
                        should_delete = False
                        print(f"   ✗ Color mismatch: {request.color} not in {dress.color}")
                
                # Check budget if specified
                if should_delete and request.budget_max:
                    if dress.price_per_day > request.budget_max:
                        should_delete = False
                        print(f"   ✗ Price too high: ₹{dress.price_per_day} > ₹{request.budget_max}")
            
            if should_delete:
                print(f"   🗑️ DELETING Request #{request.id}: {request.dress_type}")
                db.delete(request)
                deleted_count += 1
        
        if deleted_count > 0:
            db.commit()
            print(f"\n✅ Successfully deleted {deleted_count} matching request(s)")
        else:
            print(f"   ℹ️ No requests matched deletion criteria")
            
    except Exception as e:
        print(f"⚠️ Error auto-deleting requests: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"✅ Booking created: ID {booking.id}")
    print("="*60 + "\n")
    
    return {
        "id": booking.id,
        "dress_id": booking.dress_id,
        "renter_id": booking.renter_id,
        "start_date": booking.start_date.isoformat(),
        "end_date": booking.end_date.isoformat(),
        "total_days": booking.total_days,
        "total_price": booking.total_price,
        "security_deposit": booking.security_deposit,
        "status": booking.status,
        "created_at": booking.created_at.isoformat()
    }


@router.get("/{booking_id}")
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific booking"""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).options(
        joinedload(Booking.dress).joinedload(Product.owner)
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user has access (either renter or owner)
    if booking.renter_id != current_user.id and booking.dress.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "id": booking.id,
        "dress_id": booking.dress_id,
        "renter_id": booking.renter_id,
        "start_date": booking.start_date.isoformat(),
        "end_date": booking.end_date.isoformat(),
        "total_days": booking.total_days,
        "total_price": booking.total_price,
        "security_deposit": booking.security_deposit,
        "status": booking.status,
        "created_at": booking.created_at.isoformat(),
        "dress": {
            "id": booking.dress.id,
            "name": booking.dress.name,
            "owner": {
                "id": booking.dress.owner.id,
                "username": booking.dress.owner.username
            }
        }
    }


@router.put("/{booking_id}/status")
async def update_booking_status(
    booking_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update booking status (owner only)"""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).options(
        joinedload(Booking.dress)
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only owner can update status
    if booking.dress.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if new_status not in ["pending", "confirmed", "active", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    booking.status = new_status
    db.commit()
    
    return {"message": "Booking status updated", "status": new_status}


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking (renter only, before confirmed)"""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only renter can cancel
    if booking.renter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Can only cancel if not confirmed yet
    if booking.status not in ["pending"]:
        raise HTTPException(status_code=400, detail="Cannot cancel confirmed bookings")
    
    booking.status = "cancelled"
    db.commit()
    
    return {"message": "Booking cancelled"}