from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import get_supabase

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info("🔐 Authenticating user...")
    logger.info(f"🎫 Token received: {credentials.credentials[:20]}...")  # Log first 20 chars only
    
    token = credentials.credentials
    try:
        payload = verify_token(token)
        logger.info(f"✅ Token verified successfully")
        logger.info(f"📋 Token payload: {payload}")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {str(e)}")
        raise
    
    user_id: str = payload.get("sub")
    if user_id is None:
        logger.error("❌ No user ID in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    logger.info(f"👤 User ID from token: {user_id}")
    
    # Get user from Supabase
    supabase = get_supabase()
    try:
        logger.info("📡 Fetching user from database...")
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        logger.info(f"🔍 Database response: {response}")
        
        if not response.data:
            logger.error("❌ User not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        user = response.data[0]
        logger.info(f"✅ User authenticated successfully: {user['id']}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Database error during user lookup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate user: {str(e)}",
        )


async def get_current_user_websocket(token: str) -> dict:
    """
    Get current user for WebSocket connections
    Similar to get_current_user but works with token string directly
    """
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise ValueError("Could not validate credentials")
    
    # Get user from Supabase
    supabase = get_supabase()
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            raise ValueError("User not found")
        return response.data[0]
    except Exception as e:
        raise ValueError(f"Could not validate user: {str(e)}")


async def get_user_id_from_email(email: str) -> str:
    """
    Get user ID from email address
    Used by performance monitoring and other services
    """
    supabase = get_supabase()
    try:
        response = supabase.table("users").select("id").eq("email", email).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return response.data[0]["id"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user ID from email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not get user ID: {str(e)}"
        )