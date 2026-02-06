from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# ============================================
# USER SCHEMAS
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    phone: str
    address: str
    location: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    location: Optional[str] = None
    trust_score: float = 0.0
    verified: bool = False
    member_since: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# PROFILE SCHEMAS
# ============================================

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    phone: str
    address: str
    bio: Optional[str]
    profile_image: Optional[str]
    location: Optional[str]
    trust_score: float
    verified: bool
    member_since: datetime
    is_active: bool
    total_products: int = 0
    total_rentals: int = 0
    total_reviews: int = 0
    average_rating: float = 0.0
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# PRODUCT SCHEMAS
# ============================================

# ============================================
# PRODUCT SCHEMAS
# ============================================

class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    is_primary: bool
    order: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""  
    price_per_day: float
    category: str
    size: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    security_deposit: float = 0.0
    location: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_day: Optional[float] = None
    category: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    security_deposit: Optional[float] = None
    location: Optional[str] = None
    is_available: Optional[bool] = None

from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional

class ProductResponse(BaseModel):
    id: int
    owner_id: int
    owner_username: str
    name: str
    description: Optional[str] = None
    price_per_day: float
    category: str
    size: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    security_deposit: float
    location: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True
    created_at: datetime
    
    
    class Config:
        from_attributes = True

# ============================================
# BOOKING SCHEMAS
# ============================================

class BookingCreate(BaseModel):
    dress_id: int
    start_date: date
    end_date: date

class BookingResponse(BaseModel):
    id: int
    dress_id: int
    renter_id: int
    start_date: date
    end_date: date
    total_days: int
    total_price: float
    security_deposit: float
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# MESSAGE SCHEMAS (SINGLE DEFINITION)
# ============================================

class MessageCreate(BaseModel):
    receiver_id: int
    message: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    is_read: bool
    created_at: datetime
    booking_id: Optional[int] = None
    
    # Optional nested objects
    sender: Optional[UserResponse] = None
    receiver: Optional[UserResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# REVIEW SCHEMAS
# ============================================

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    dress_id: int
    booking_id: int
    reviewer_id: int
    rating: int
    comment: Optional[str]
    owner_response: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# CART & ORDER SCHEMAS
# ============================================

class CartItemCreate(BaseModel):
    product_id: int
    rental_start_date: date
    rental_end_date: date

class OrderCreate(BaseModel):
    pass

# ============================================
# REQUEST SCHEMAS
# ============================================

class DressRequestCreate(BaseModel):
    dress_type: str
    occasion: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    rental_start_date: Optional[date] = None
    rental_end_date: Optional[date] = None
    description: Optional[str] = None

class DressRequestResponse(BaseModel):
    id: int
    user_id: int
    dress_type: str
    occasion: Optional[str]
    size: Optional[str]
    color: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    rental_start_date: Optional[date]
    rental_end_date: Optional[date]
    description: Optional[str]
    status: str
    created_at: datetime
    username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# NOTIFICATION SCHEMAS (SINGLE DEFINITION)
# ============================================

class NotificationBase(BaseModel):
    type: str
    title: str
    message: str
    related_id: Optional[int] = None
    

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ============================================
# TOKEN SCHEMAS
# ============================================
# ============================================
# CART & ORDER SCHEMAS
# ============================================

class CartItemCreate(BaseModel):
    product_id: int
    rental_start_date: date
    rental_end_date: date

class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rental_days: int
    start_date: date
    end_date: date
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    rental_days: int
    price_per_day: float
    total_price: float
    
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    start_date: date
    end_date: date
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    pass
# PRODUCT IMAGE SCHEMAS
class ProductImageCreate(BaseModel):
    image_url: str
    is_primary: bool = False
    order: int = 0
class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    is_primary: bool
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True
from datetime import date
from typing import Optional

# Dress Request Schemas
class DressRequestCreate(BaseModel):
    dress_type: str
    occasion: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    rental_start_date: Optional[date] = None
    rental_end_date: Optional[date] = None
    description: Optional[str] = None

class DressRequestUpdate(BaseModel):
    dress_type: Optional[str] = None
    occasion: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    rental_start_date: Optional[date] = None
    rental_end_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None

class DressRequestResponse(BaseModel):
    id: int
    user_id: int
    dress_type: str
    occasion: Optional[str]
    size: Optional[str]
    color: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    rental_start_date: Optional[date]
    rental_end_date: Optional[date]
    description: Optional[str]
    status: str
    created_at: datetime
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None

class TokenData(BaseModel):
    username: Optional[str] = None