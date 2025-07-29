from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None


class User(UserBase):
    id: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}