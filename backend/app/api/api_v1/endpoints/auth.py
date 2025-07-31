from fastapi import APIRouter, HTTPException, status, Depends
from app.core.supabase_auth import get_current_user_supabase
from app.core.database import get_supabase

router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user_supabase)):
    """Get current user information from Supabase"""
    return {k: v for k, v in current_user.items() if k != "hashed_password"}


@router.get("/health")
async def auth_health():
    """Check if auth system is working"""
    return {"status": "healthy", "auth_type": "supabase"}