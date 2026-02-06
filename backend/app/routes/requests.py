from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt
from ..database import get_db
from ..models import DressRequest, User, Notification, RequestStatus
from ..schemas import DressRequestCreate, DressRequestResponse, DressRequestUpdate
from ..utils.security import SECRET_KEY, ALGORITHM
from ..models import Booking, User, Product, DressRequest, RequestStatus
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current user from token
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

router = APIRouter()

@router.post("/", response_model=DressRequestResponse)
async def create_dress_request(
    request: DressRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dress request"""
    
    # Create the request
    db_request = DressRequest(
        user_id=current_user.id,
        **request.dict()
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Create notifications for all other users (potential owners)
    all_users = db.query(User).filter(User.id != current_user.id).all()
    for user in all_users:
        notification = Notification(
            user_id=user.id,
            type="new_request", 
            title="New Dress Request",  
            message=f"New dress request: {request.dress_type}",
            request_id=db_request.id
        )
        db.add(notification)
    
    db.commit()
    
    # Add username to response
    response = DressRequestResponse.from_orm(db_request)
    response.username = current_user.username
    
    return response

@router.get("/all", response_model=List[DressRequestResponse])
async def get_all_requests(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all dress requests (for owners to see)"""
    
    query = db.query(DressRequest).filter(
        DressRequest.user_id != current_user.id  # Don't show own requests
    )
    
    if status_filter:
        query = query.filter(DressRequest.status == status_filter)
    
    requests = query.order_by(DressRequest.created_at.desc()).all()
    
    # Add username to each request
    result = []
    for req in requests:
        response = DressRequestResponse.from_orm(req)
        response.username = req.user.username
        result.append(response)
    
    return result

@router.get("/my-requests", response_model=List[DressRequestResponse])
async def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's dress requests"""
    
    requests = db.query(DressRequest).filter(
        DressRequest.user_id == current_user.id
    ).order_by(DressRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        response = DressRequestResponse.from_orm(req)
        response.username = current_user.username
        result.append(response)
    
    return result

@router.put("/{request_id}", response_model=DressRequestResponse)
async def update_request(
    request_id: int,
    request_update: DressRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a dress request"""
    
    db_request = db.query(DressRequest).filter(DressRequest.id == request_id).first()
    
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    for field, value in request_update.dict(exclude_unset=True).items():
        setattr(db_request, field, value)
    
    db.commit()
    db.refresh(db_request)
    
    response = DressRequestResponse.from_orm(db_request)
    response.username = current_user.username
    
    return response

@router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a dress request"""
    
    db_request = db.query(DressRequest).filter(DressRequest.id == request_id).first()
    
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_request)
    db.commit()
    
    return {"message": "Request deleted successfully"}

@router.get("/{request_id}", response_model=DressRequestResponse)
async def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific dress request"""
    
    db_request = db.query(DressRequest).filter(DressRequest.id == request_id).first()
    
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    response = DressRequestResponse.from_orm(db_request)
    response.username = db_request.user.username
    
    return response

@router.get("/debug/all-requests-debug")
async def debug_all_requests(db: Session = Depends(get_db)):
    """DEBUG: Show all requests in database"""
    requests = db.query(DressRequest).all()
    return {
        "total_requests": len(requests),
        "requests": [
            {
                "id": req.id,
                "dress_type": req.dress_type,
                "description": req.description,
                "status": req.status,
                "user_id": req.user_id,
                "size": req.size,
                "occasion": req.occasion,
                "budget_min": req.budget_min,
                "budget_max": req.budget_max,
                "username": req.user.username if req.user else "Unknown"
            }
            for req in requests
        ]
    }