from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Review, Product, User, Booking
from ..schemas import ReviewCreate, ReviewResponse
from ..auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a review for a product"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user has booked this product - FIXED: Use dress_id
    booking = db.query(Booking).filter(
        Booking.dress_id == review.product_id,
        Booking.renter_id == current_user.id,
        Booking.status == "completed"
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=400, 
            detail="You can only review products you have rented and completed"
        )
    
    # Check if review already exists for this booking
    existing_review = db.query(Review).filter(
        Review.booking_id == booking.id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this booking")
    
    # Create review - FIXED: Use dress_id
    db_review = Review(
        dress_id=review.product_id,
        booking_id=booking.id,
        reviewer_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update product average rating
    update_product_rating(db, review.product_id)
    
    return db_review

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all reviews for a product"""
    # FIXED: Use dress_id
    reviews = db.query(Review).filter(
        Review.dress_id == product_id
    ).order_by(Review.created_at.desc()).all()
    return reviews

@router.get("/product/{product_id}/average")
async def get_average_rating(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get average rating for a product"""
    # FIXED: Use dress_id
    reviews = db.query(Review).filter(Review.dress_id == product_id).all()
    
    if not reviews:
        return {"average_rating": 0, "total_reviews": 0}
    
    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    return {
        "average_rating": round(avg_rating, 1),
        "total_reviews": len(reviews)
    }

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.reviewer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review.rating = review_update.rating
    review.comment = review_update.comment
    
    db.commit()
    db.refresh(review)
    
    # Update product average rating - FIXED: Use dress_id
    update_product_rating(db, review.dress_id)
    
    return review

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.reviewer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    product_id = review.dress_id  # FIXED: Use dress_id
    
    db.delete(review)
    db.commit()
    
    # Update product average rating
    update_product_rating(db, product_id)
    
    return {"message": "Review deleted successfully"}

def update_product_rating(db: Session, product_id: int):
    """Update the average rating for a product"""
    # FIXED: Use dress_id
    reviews = db.query(Review).filter(Review.dress_id == product_id).all()
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            product.average_rating = round(avg_rating, 1)
        else:
            product.average_rating = 0.0
        
        db.commit()