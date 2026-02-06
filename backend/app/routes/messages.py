from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from ..database import get_db
from ..models import Message, User
from ..schemas import MessageCreate, MessageResponse
from ..auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a message"""
    from sqlalchemy.orm import joinedload
    
    print(f"📨 Received message data: {message.dict()}")
    print(f"👤 Current user: {current_user.id}")
    
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    if not receiver:
        print(f"❌ Receiver {message.receiver_id} not found")
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Can't send message to yourself
    if message.receiver_id == current_user.id:
        print(f"❌ Cannot send message to yourself")
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    print(f"✅ Creating message from {current_user.id} to {message.receiver_id}")
    
    # Create message (only with fields that exist in the Message model)
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        message=message.message
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Load relationships
    db_message = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver)
    ).filter(Message.id == db_message.id).first()
    
    # Create notification for receiver
    try:
        from ..models import Notification
        notification = Notification(
            user_id=message.receiver_id,
            type='message',
            title='💬 New Message',
            message=f'You have a new message from {current_user.username}',
            related_id=current_user.id
        )
        db.add(notification)
        db.commit()
        print(f"✅ Notification created for user {message.receiver_id}")
    except Exception as e:
        print(f"⚠️  Failed to create notification: {e}")
    
    print(f"✅ Message created with ID: {db_message.id}")
    return db_message

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all messages for current user"""
    from sqlalchemy.orm import joinedload
    
    messages = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver)
    ).filter(
        or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).all()
    return messages

@router.get("/conversation/{other_user_id}", response_model=List[MessageResponse])
async def get_conversation(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation between current user and another user"""
    from sqlalchemy.orm import joinedload
    
    messages = db.query(Message).options(
        joinedload(Message.sender),
        joinedload(Message.receiver)
    ).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    
    db.commit()
    return messages

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread messages"""
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    return {"unread_count": count}

@router.put("/{message_id}/read")
async def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark message as read"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    return {"message": "Marked as read"}

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a message"""
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.sender_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    db.delete(message)
    db.commit()
    return {"message": "Message deleted"}