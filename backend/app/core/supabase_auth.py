"""
Supabase Authentication Integration
Handles Supabase JWT tokens for frontend-backend auth alignment
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_supabase

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

security = HTTPBearer()


class SupabaseAuth:
    """Handles Supabase JWT token verification"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def verify_supabase_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Supabase JWT token
        Returns user data if token is valid
        """
        try:
            logger.info("🔐 Verifying Supabase token...")
            
            # Use Supabase auth to verify token
            auth_response = self.supabase.auth.get_user(token)
            
            if not auth_response.user:
                logger.error("❌ Invalid token - no user found")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = auth_response.user
            logger.info(f"✅ Token verified for user: {user.id}")
            
            # Get additional user data from users table
            response = self.supabase.table("users").select("*").eq("id", user.id).execute()
            
            if not response.data:
                logger.error("❌ User not found in database")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            
            user_data = response.data[0]
            logger.info(f"✅ User authenticated: {user_data['id']}")
            
            return user_data
            
        except Exception as e:
            logger.error(f"❌ Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Create singleton instance
supabase_auth = SupabaseAuth()


async def get_current_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current user from Supabase JWT token
    Replaces the old JWT-based authentication
    """
    token = credentials.credentials
    return await supabase_auth.verify_supabase_token(token)


async def get_current_user_websocket_supabase(token: str) -> Dict[str, Any]:
    """
    Get current user for WebSocket connections using Supabase token
    """
    try:
        return await supabase_auth.verify_supabase_token(token)
    except Exception as e:
        raise ValueError(f"WebSocket authentication failed: {str(e)}")