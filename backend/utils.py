import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, Request
import os
from motor.motor_asyncio import AsyncIOMotorDatabase

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def utc_now() -> datetime:
    """Get current UTC datetime with timezone"""
    return datetime.now(timezone.utc)

def ensure_timezone(dt: datetime) -> datetime:
    """Ensure datetime has timezone info"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

async def get_authenticated_user(request: Request, db: AsyncIOMotorDatabase):
    """Extract and validate session token from cookies or Authorization header"""
    # Try to get token from cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session in database
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check if session is expired
    expires_at = ensure_timezone(session_doc["expires_at"])
    if expires_at < utc_now():
        # Delete expired session
        await db.user_sessions.delete_one({"session_token": session_token})
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user data
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user_doc