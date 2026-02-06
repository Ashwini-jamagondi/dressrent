from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base
from typing import Optional


# Request Status Enum
class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    profile_photo_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    profile_image = Column(String, nullable=True)
    trust_score = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    member_since = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="owner")
    
    # Relationships
    products = relationship("Product", back_populates="owner", foreign_keys="Product.owner_id")
    cart_items = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    messages_received = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")
    dress_requests = relationship("DressRequest", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    requests = relationship("Request", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(Text)
    price_per_day = Column(Float)
    category = Column(String, index=True)
    size = Column(String)
    color = Column(String)
    brand = Column(String, nullable=True)
    condition = Column(String, default="Excellent")
    security_deposit = Column(Float, default=0.0)
    location = Column(String, nullable=True, index=True)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_bookings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    dress_type = Column(String, nullable=True, index=True)
    
    # Relationships - KEEP ONLY ONE of each!
    owner = relationship("User", back_populates="products")
    cart_items = relationship("Cart", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="dress", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="dress", cascade="all, delete-orphan")
    
    @property
    def primary_image(self):
        """Get the primary image URL or first image"""
        primary = next((img.image_url for img in self.images if img.is_primary), None)
        if primary:
            return primary
        return self.images[0].image_url if self.images else None

class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    image_url = Column(String)
    is_primary = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="images")


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    dress_id = Column(Integer, ForeignKey("products.id"))
    renter_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    total_days = Column(Integer)
    total_price = Column(Float)
    security_deposit = Column(Float)
    status = Column(String, default="pending")
    is_owner_block = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    dress = relationship("Product", back_populates="bookings")
    renter = relationship("User")
    review = relationship("Review", back_populates="booking", uselist=False)
    messages = relationship("Message", back_populates="booking")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    dress_id = Column(Integer, ForeignKey("products.id"))
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    owner_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dress = relationship("Product", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")
    reviewer = relationship("User", back_populates="reviews_given")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    booking = relationship("Booking")


class Cart(Base):
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    rental_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    status = Column(String, default="pending")
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    rental_days = Column(Integer)
    price_per_day = Column(Float)
    total_price = Column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class DressRequest(Base):
    __tablename__ = "dress_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dress_type = Column(String, nullable=False)
    occasion = Column(String)
    size = Column(String)
    color = Column(String)
    budget_min = Column(Float)
    budget_max = Column(Float)
    rental_start_date = Column(Date)
    rental_end_date = Column(Date)
    description = Column(Text)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="dress_requests")


class Request(Base):
    """Model for customer dress requests (alternative/legacy)"""
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dress_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    size = Column(String(10), nullable=True)
    color = Column(String(50), nullable=True)
    occasion = Column(String(100), nullable=True)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    needed_by_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="requests")


# FIXED: Single Notification Model (removed duplicates)
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # 'dress_match', 'message', 'booking', 'interest'
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    related_id = Column(Integer, nullable=True)  # ID of related entity (product, message, etc)
    request_id = Column(Integer, ForeignKey("dress_requests.id"), nullable=True)  # Legacy field
    is_read = Column(Boolean, default=False)
   
    created_at = Column(DateTime, default=func.now(), nullable=False)
    # Relationships
    user = relationship("User", back_populates="notifications")
    request = relationship("DressRequest", foreign_keys=[request_id])