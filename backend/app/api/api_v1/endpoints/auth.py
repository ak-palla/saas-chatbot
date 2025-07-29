from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User, UserCreate
from app.core.auth import create_access_token, get_password_hash, verify_password, get_current_user
from app.core.database import get_supabase
from app.core.middleware import limiter, RATE_LIMITING_ENABLED

router = APIRouter()


@router.post("/register")
async def register(user: UserCreate):
    """Register a new user"""
    supabase = get_supabase()
    
    # Check if user already exists
    existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "subscription_tier": "free",
        "is_active": True
    }
    
    try:
        response = supabase.table("users").insert(user_data).execute()
        created_user = response.data[0]
        
        # Create access token
        access_token = create_access_token(data={"sub": created_user["id"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": created_user
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user"""
    supabase = get_supabase()
    
    # Get user by email
    response = supabase.table("users").select("*").eq("email", form_data.username).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = response.data[0]
    
    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {k: v for k, v in user.items() if k != "hashed_password"}
    }


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {k: v for k, v in current_user.items() if k != "hashed_password"}