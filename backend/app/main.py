from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import os
from pathlib import Path
from fastapi import Header

from .routes import notifications
from .models import Request, Product
from jose import jwt, JWTError
from .models import User, Product, DressRequest  # Add Request here


from .database import engine, get_db, Base
from .models import User
from .schemas import UserCreate, UserResponse, Token
from .utils.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Import all routers (UPDATED - includes requests and notifications)
from .routes import messages, users, products, cart, orders, reviews, bookings, profiles, images, requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, products, bookings, reviews, profiles
from .routes.password_reset import router as password_reset_router
# Create database tables
Base.metadata.create_all(bind=engine)
from dotenv import load_dotenv
load_dotenv()
Base.metadata.create_all(bind=engine)
# Create upload directories
from .routes import products, users, requests, messages, notifications  # Add these
from .database import init_db
app = FastAPI()
app = FastAPI(title="DressRent API", version="1.0.0")

# CORS configuration for production
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.onrender.com",  # Render domains
    # Add your custom domain when ready
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 Application started!")
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "products").mkdir(exist_ok=True)
(UPLOAD_DIR / "profiles").mkdir(exist_ok=True)

# In uploads section:
(UPLOAD_DIR / "profiles").mkdir(exist_ok=True)

app = FastAPI(
    title="DressRent - Dress Rental Platform",
    description="Rent and List Dresses",
    version="2.0.0"
)
app=FastAPI()
#from .routers import users
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files for uploads
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Get paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

# Mount static files if they exist
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include API routers (no trailing slashes)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(products.router, prefix="/api", tags=["products"])


app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(profiles.router, prefix="/api/users", tags=["profiles"])
# Where you include routers:
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
# NEW: Add request and notification routes
app.include_router(requests.router, prefix="/api/requests", tags=["requests"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(password_reset_router, prefix="/api", tags=["password-reset"]) 
app.include_router(requests.router, prefix="/api/requests", tags=["requests"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])  # Add this
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])


app.include_router(users.router, prefix="/api/users", tags=["users"])

# Root endpoint
@app.get("/")
async def home():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "DressRent API - Visit /docs for documentation"}


# ============================================================
# REGISTRATION ENDPOINT - Step 1: Create Account
# ============================================================
@app.post("/api/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    - Checks if email/username already exists
    - Hashes the password securely
    - Saves user to database
    - Returns access token
    """
    print("\n" + "="*60)
    print("📝 REGISTRATION ATTEMPT")
    print("="*60)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        print(f"❌ Email '{user.email}' already registered")
        print("="*60 + "\n")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        print(f"❌ Username '{user.username}' already taken")
        print("="*60 + "\n")
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password securely
    hashed_password = get_password_hash(user.password)
    print(f"🔐 Password hashed successfully")
    
    # Create new user in database
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    print(f"✅ User created successfully!")
    print(f"   User ID: {db_user.id}")
    print(f"   Username: {db_user.username}")
    print(f"   Email: {db_user.email}")
    
    # Create access token for immediate login
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    print(f"🔑 Access token generated")
    print("="*60 + "\n")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# ============================================================
# LOGIN ENDPOINT - Step 2: Login with Saved Credentials
# ============================================================
@app.post("/api/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with registered credentials
    - Checks if user exists in database
    - Verifies password matches the saved hash
    - Returns access token if successful
    """
    print("\n" + "="*60)
    print("🔍 LOGIN ATTEMPT")
    print("="*60)
    print(f"Username: {form_data.username}")
    
    # Step 1: Find user in database
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        print(f"❌ User '{form_data.username}' not found in database")
        print("💡 Hint: User needs to register first!")
        print("="*60 + "\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ User found in database")
    print(f"   User ID: {user.id}")
    print(f"   Email: {user.email}")
    
    # Step 2: Verify password
    password_valid = verify_password(form_data.password, user.hashed_password)
    print(f"🔐 Password verification: {password_valid}")
    
    if not password_valid:
        print(f"❌ Invalid password for user '{form_data.username}'")
        print("="*60 + "\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ Authentication successful!")
    
    # Step 3: Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    print(f"🔑 Access token generated")
    print("="*60 + "\n")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
@app.get("/api/requests/{request_id}/matches")
async def get_matching_dresses(
    request_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Find dresses that match a user's request"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Split Bearer token
        parts = authorization.split()
        if len(parts) != 2:
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        scheme, token = parts
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        # Import SECRET_KEY from your security utils
        from .utils.security import SECRET_KEY
        ALGORITHM = "HS256"
        from jose import jwt, JWTError
        
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Get user from database using username
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        user_id = user.id
            
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
    
    # Use DressRequest instead of Request
    from .models import DressRequest, Product
    
    # Get the request
    dress_request = db.query(DressRequest).filter(DressRequest.id == request_id).first()
    if not dress_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if user owns this request
    if dress_request.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Build query to find matching dresses
    query = db.query(Product).filter(Product.is_available == True)
    
    # Match by dress type - check if attribute exists
    if hasattr(dress_request, 'dress_type') and dress_request.dress_type:
        query = query.filter(Product.category.ilike(f"%{dress_request.dress_type}%"))
    
    # Match by size - check if attribute exists
    if hasattr(dress_request, 'size') and dress_request.size:
        query = query.filter(Product.size == dress_request.size)
    
    # Match by budget - check if attributes exist
    if hasattr(dress_request, 'budget_min') and dress_request.budget_min:
        query = query.filter(Product.price_per_day >= dress_request.budget_min)
    if hasattr(dress_request, 'budget_max') and dress_request.budget_max:
        query = query.filter(Product.price_per_day <= dress_request.budget_max)
    
    matches = query.all()
    
    # Return matching dresses with owner info
    results = []
    for dress in matches:
        owner = db.query(User).filter(User.id == dress.owner_id).first()
        
        # Build image URL
        image_url = None
        if hasattr(dress, 'image_url') and dress.image_url:
            image_url = dress.image_url if dress.image_url.startswith('http') else f"/uploads/{dress.image_url}"
        
        results.append({
            "id": dress.id,
            "name": dress.name,
            "price_per_day": dress.price_per_day,
            "size": dress.size,
            "color": dress.color,
            "image_url": image_url,
            "owner_name": owner.username if owner else "Unknown",
            "owner_id": dress.owner_id
        })
    
    return results

# HTML page routes
@app.get("/login")
async def login_page():
    return FileResponse(str(TEMPLATES_DIR / "login.html"))

@app.get("/register")
async def register_page():
    return FileResponse(str(TEMPLATES_DIR / "register.html"))

@app.get("/products")
async def products_page():
    return FileResponse(str(TEMPLATES_DIR / "products.html"))

@app.get("/add-dress")
async def add_dress_page():
    return FileResponse(str(TEMPLATES_DIR / "add-dress.html"))

@app.get("/my-dresses")
async def my_dresses_page():
    return FileResponse(str(TEMPLATES_DIR / "my-dresses.html"))

@app.get("/my-rentals")
async def my_rentals_page():
    return FileResponse(str(TEMPLATES_DIR / "my-rentals.html"))

@app.get("/reviews")
async def reviews_page():
    return FileResponse(str(TEMPLATES_DIR / "reviews.html"))

@app.get("/messages")
async def messages_page():
    return FileResponse(str(TEMPLATES_DIR / "messages.html"))

@app.get("/profile")
async def profile_page():
    return FileResponse(str(TEMPLATES_DIR / "profile.html"))

@app.get("/product-details")
async def product_details_page():
    return FileResponse(str(TEMPLATES_DIR / "product-details.html"))

# NEW: Request pages
@app.get("/customer-requests")
async def customer_requests_page():
    """Page for owners to see customer requests"""
    return FileResponse(str(TEMPLATES_DIR / "customer-requests.html"))

@app.get("/my-requests")
async def my_requests_page():
    """Page for customers to create and manage their requests"""
    return FileResponse(str(TEMPLATES_DIR / "my-requests.html"))
@app.get("/profile")
async def profile_page():
    return FileResponse("frontend/profile.html")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
@app.get("/forgot-password")
async def serve_forgot_password():
    return FileResponse("frontend/forgot-password.html")

@app.get("/reset-password")
async def serve_reset_password():
    return FileResponse("frontend/reset-password.html")

# Optional: Add route for login page if you need it
@app.get("/login")
async def serve_login():
    return FileResponse("frontend/login.html")

@app.get("/")
async def serve_home():
    return FileResponse("frontend/index.html")  # or whatever your home page is

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)