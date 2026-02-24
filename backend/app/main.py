from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
from jose import jwt, JWTError

from .database import engine, get_db, Base, init_db
from .models import User, Product, DressRequest
from .schemas import UserCreate, UserResponse, Token
from .utils.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .routes import messages, users, products, cart, orders, reviews, bookings, profiles, images, requests, notifications, auth
from .routes.password_reset import router as password_reset_router

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create upload directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "products").mkdir(exist_ok=True)
(UPLOAD_DIR / "profiles").mkdir(exist_ok=True)

# Get paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

# Create app
app = FastAPI(title="DressRent API", version="1.0.0")

# CORS middleware - single, permissive for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 Application started!")

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(requests.router, prefix="/api/requests", tags=["requests"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(password_reset_router, prefix="/api", tags=["password-reset"])

# ============================================================
# REGISTRATION ENDPOINT
# ============================================================
@app.post("/api/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    print("\n" + "="*60)
    print("📝 REGISTRATION ATTEMPT")
    print("="*60)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        print(f"❌ Email '{user.email}' already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        print(f"❌ Username '{user.username}' already taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    print(f"🔐 Password hashed successfully")

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

    print(f"✅ User created successfully! ID: {db_user.id}")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )

    print(f"🔑 Access token generated")
    print("="*60 + "\n")

    return {"access_token": access_token, "token_type": "bearer", "user": db_user}


# ============================================================
# LOGIN ENDPOINT
# ============================================================
@app.post("/api/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print("\n" + "="*60)
    print("🔍 LOGIN ATTEMPT")
    print("="*60)
    print(f"Username: {form_data.username}")

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        print(f"❌ User '{form_data.username}' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"✅ User found: {user.id}")
    password_valid = verify_password(form_data.password, user.hashed_password)
    print(f"🔐 Password verification: {password_valid}")

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    print(f"✅ Login successful! Token generated.")
    print("="*60 + "\n")

    return {"access_token": access_token, "token_type": "bearer", "user": user}


# ============================================================
# MATCHING ENDPOINT
# ============================================================
@app.get("/api/requests/{request_id}/matches")
async def get_matching_dresses(
    request_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        parts = authorization.split()
        if len(parts) != 2:
            raise HTTPException(status_code=401, detail="Invalid authorization format")

        scheme, token = parts
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        from .utils.security import SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        user_id = user.id

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

    dress_request = db.query(DressRequest).filter(DressRequest.id == request_id).first()
    if not dress_request:
        raise HTTPException(status_code=404, detail="Request not found")

    if dress_request.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = db.query(Product).filter(Product.is_available == True)

    if hasattr(dress_request, 'dress_type') and dress_request.dress_type:
        query = query.filter(Product.category.ilike(f"%{dress_request.dress_type}%"))
    if hasattr(dress_request, 'size') and dress_request.size:
        query = query.filter(Product.size == dress_request.size)
    if hasattr(dress_request, 'budget_min') and dress_request.budget_min:
        query = query.filter(Product.price_per_day >= dress_request.budget_min)
    if hasattr(dress_request, 'budget_max') and dress_request.budget_max:
        query = query.filter(Product.price_per_day <= dress_request.budget_max)

    matches = query.all()

    results = []
    for dress in matches:
        owner = db.query(User).filter(User.id == dress.owner_id).first()
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


# ============================================================
# PAGE ROUTES
# ============================================================
@app.get("/")
async def home():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "DressRent API - Visit /docs for documentation"}

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

@app.get("/customer-requests")
async def customer_requests_page():
    return FileResponse(str(TEMPLATES_DIR / "customer-requests.html"))

@app.get("/my-requests")
async def my_requests_page():
    return FileResponse(str(TEMPLATES_DIR / "my-requests.html"))

@app.get("/forgot-password")
async def forgot_password_page():
    return FileResponse(str(TEMPLATES_DIR / "forgot-password.html"))

@app.get("/reset-password")
async def reset_password_page():
    return FileResponse(str(TEMPLATES_DIR / "reset-password.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)