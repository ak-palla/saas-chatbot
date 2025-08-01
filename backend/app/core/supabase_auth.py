"""
Supabase Authentication Integration
Handles Supabase JWT tokens for frontend-backend auth alignment
"""

import logging
from jose import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_supabase_admin
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

security = HTTPBearer()


class SupabaseAuth:
    """Handles Supabase JWT token verification"""
    
    def __init__(self):
        self.supabase_admin = get_supabase_admin()
    
    async def _sync_user_to_database(self, user) -> None:
        """
        Sync user from Supabase Auth to our users table
        Creates user record if it doesn't exist
        """
        try:
            logger.info(f"🔄 Syncing user {user.id} to users table...")
            logger.info(f"🔍 User object details: id={user.id}, email={user.email}, created_at={user.created_at}")
            logger.info(f"🔍 User metadata: {getattr(user, 'user_metadata', 'No metadata')}")
            
            # Check if user already exists in users table
            logger.info(f"🔍 Checking if user {user.id} exists in users table...")
            response = self.supabase_admin.table("users").select("id").eq("id", user.id).execute()
            logger.info(f"🔍 User existence check response: {response.data}")
            
            if response.data:
                logger.info(f"✅ User {user.id} already exists in users table")
                return
            
            # Create user record in users table
            # For Supabase Auth users, we use a placeholder password since auth is handled by Supabase
            user_metadata = getattr(user, 'user_metadata', {}) or {}
            full_name = user_metadata.get('full_name') if user_metadata else None
            
            user_data = {
                "id": user.id,
                "email": user.email,
                "hashed_password": "supabase_auth",  # Placeholder since auth is handled by Supabase
                "created_at": user.created_at,
                "updated_at": user.created_at,
                "is_active": True,
                "full_name": full_name,
            }
            
            logger.info(f"📝 Creating user record: {user_data}")
            insert_response = self.supabase_admin.table("users").insert(user_data).execute()
            logger.info(f"✅ User {user.id} created in users table: {insert_response.data}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync user to database: {str(e)}")
            logger.error(f"🔍 Sync error type: {type(e)}")
            logger.error(f"📊 Sync error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
            # Re-raise the exception so we can see what's going wrong
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to sync user to database: {str(e)}"
            )
    
    async def verify_supabase_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Supabase JWT token using the admin client
        Returns user data if token is valid
        """
        try:
            logger.info("🔐 Verifying Supabase token...")
            logger.info(f"🔍 Token preview: {token[:20]}...{token[-10:]}")
            
            # Use admin client to get user from JWT token
            try:
                user_response = self.supabase_admin.auth.get_user(token)
                logger.info(f"🔍 Auth response: {user_response}")
                
                if hasattr(user_response, 'user') and user_response.user:
                    user = user_response.user
                    logger.info(f"✅ Token verified for user: {user.id}")
                    
                    # Return user data compatible with the existing code
                    user_data = {
                        "id": user.id,
                        "email": user.email,
                        "created_at": user.created_at,
                        "user_metadata": getattr(user, 'user_metadata', {}),
                        "app_metadata": getattr(user, 'app_metadata', {})
                    }
                    
                    logger.info(f"✅ User authenticated: {user_data['id']}")
                    return user_data
                else:
                    logger.error("❌ Invalid token - no user found in response")
                    logger.error(f"🔍 Response details: {user_response}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                    
            except Exception as auth_error:
                logger.error(f"❌ Supabase auth.get_user failed: {str(auth_error)}")
                logger.error(f"🔍 Auth error type: {type(auth_error)}")
                
                # Fallback: try to decode JWT manually for debugging
                try:
                    # Decode without verification to see token contents
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    logger.info(f"🔍 JWT payload (unverified): {decoded}")
                    
                    # Check if token has expected structure
                    if 'sub' in decoded:
                        logger.info(f"🔍 Token subject (user ID): {decoded['sub']}")
                        logger.info(f"🔍 Token expiry: {decoded.get('exp', 'No expiry')}")
                        logger.info(f"🔍 Token issuer: {decoded.get('iss', 'No issuer')}")
                    
                except Exception as jwt_error:
                    logger.error(f"❌ JWT decode failed: {str(jwt_error)}")
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"❌ Token verification failed: {str(e)}")
            logger.error(f"🔍 Exception type: {type(e)}")
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