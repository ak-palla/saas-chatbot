from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging
from app.models.chatbot import Chatbot, ChatbotCreate, ChatbotUpdate
from app.core.supabase_auth import get_current_user_supabase
from app.core.database import get_supabase

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/", response_model=Chatbot)
async def create_chatbot(
    
    chatbot: ChatbotCreate,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Create a new chatbot"""
    logger.info("🚀 Creating new chatbot")
    logger.info(f"📝 Chatbot data: {chatbot.dict()}")
    logger.info(f"👤 Current user: {current_user}")
    
    supabase = get_supabase()
    
    chatbot_data = {
        **chatbot.dict(),
        "user_id": current_user["id"]
    }
    
    logger.info(f"💾 Final chatbot data to insert: {chatbot_data}")
    
    try:
        logger.info("📡 Inserting chatbot into database...")
        response = supabase.table("chatbots").insert(chatbot_data).execute()
        logger.info(f"✅ Database response: {response}")
        logger.info(f"🎉 Chatbot created successfully: {response.data[0]}")
        return response.data[0]
    except Exception as e:
        logger.error(f"💥 Error creating chatbot: {str(e)}")
        logger.error(f"🔍 Exception type: {type(e)}")
        logger.error(f"📊 Exception details: {e.__dict__ if hasattr(e, '__dict__') else 'No details'}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chatbot: {str(e)}"
        )


@router.get("/", response_model=List[Chatbot])

async def get_user_chatbots(
    
    current_user: dict = Depends(get_current_user_supabase)
):
    """Get all chatbots for the current user"""
    supabase = get_supabase()
    
    response = supabase.table("chatbots").select("*").eq("user_id", current_user["id"]).execute()
    return response.data


@router.get("/{chatbot_id}", response_model=Chatbot)

async def get_chatbot(
    
    chatbot_id: str,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Get a specific chatbot"""
    supabase = get_supabase()
    
    response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", current_user["id"]).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    return response.data[0]


@router.put("/{chatbot_id}", response_model=Chatbot)

async def update_chatbot(
    
    chatbot_id: str,
    chatbot_update: ChatbotUpdate,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Update a chatbot"""
    supabase = get_supabase()
    
    # Check if chatbot exists and belongs to user
    existing = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", current_user["id"]).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    # Update chatbot
    update_data = {k: v for k, v in chatbot_update.dict().items() if v is not None}
    
    try:
        response = supabase.table("chatbots").update(update_data).eq("id", chatbot_id).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chatbot"
        )


@router.delete("/{chatbot_id}")

async def delete_chatbot(
    
    chatbot_id: str,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Delete a chatbot"""
    supabase = get_supabase()
    
    # Check if chatbot exists and belongs to user
    existing = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", current_user["id"]).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    try:
        supabase.table("chatbots").delete().eq("id", chatbot_id).execute()
        return {"message": "Chatbot deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chatbot"
        )