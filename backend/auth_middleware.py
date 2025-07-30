"""
Authentication middleware for user isolation
"""
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
import os

security = HTTPBearer()

# In production, use a secure secret key
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class UserSession:
    """Manages user sessions for isolation"""
    
    @staticmethod
    def create_anonymous_session() -> str:
        """Create a new anonymous session ID"""
        return f"anon_{uuid.uuid4().hex}"
    
    @staticmethod
    def create_user_token(user_id: str) -> str:
        """Create a JWT token for a user"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=30),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("user_id")
        except:
            return None

async def get_current_user(request: Request) -> str:
    """Get current user ID from request"""
    # Check for JWT token in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user_id = UserSession.verify_token(token)
        if user_id:
            return user_id
    
    # Check for session cookie
    session_id = request.cookies.get("session_id")
    if session_id:
        return session_id
    
    # Create anonymous session
    return UserSession.create_anonymous_session()

def get_user_db_path(user_id: str) -> str:
    """Get database path for a specific user"""
    os.makedirs("data/users", exist_ok=True)
    return f"data/users/{user_id}.db"

def get_user_uploads_path(user_id: str) -> str:
    """Get uploads directory for a specific user"""
    path = f"data/uploads/{user_id}"
    os.makedirs(path, exist_ok=True)
    return path