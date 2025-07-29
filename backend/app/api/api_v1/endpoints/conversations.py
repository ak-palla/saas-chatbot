from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.conversation import Conversation, ConversationCreate
from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.core.middleware import limiter

router = APIRouter()


@router.post("/", response_model=Conversation)

async def create_conversation(
    
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    supabase = get_supabase()
    
    # Verify chatbot belongs to user
    chatbot_response = supabase.table("chatbots").select("*").eq("id", conversation.chatbot_id).eq("user_id", current_user["id"]).execute()
    if not chatbot_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    conversation_data = {
        **conversation.dict(),
        "messages": []
    }
    
    try:
        response = supabase.table("conversations").insert(conversation_data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/chatbot/{chatbot_id}", response_model=List[Conversation])

async def get_chatbot_conversations(
    
    chatbot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for a specific chatbot"""
    supabase = get_supabase()
    
    # Verify chatbot belongs to user
    chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", current_user["id"]).execute()
    if not chatbot_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    response = supabase.table("conversations").select("*").eq("chatbot_id", chatbot_id).execute()
    return response.data


@router.get("/{conversation_id}", response_model=Conversation)

async def get_conversation(
    
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific conversation"""
    supabase = get_supabase()
    
    # Get conversation and verify ownership through chatbot
    conversation_response = supabase.table("conversations").select("*, chatbots!inner(user_id)").eq("id", conversation_id).execute()
    
    if not conversation_response.data or conversation_response.data[0]["chatbots"]["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation_response.data[0]


@router.delete("/{conversation_id}")

async def delete_conversation(
    
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    supabase = get_supabase()
    
    # Get conversation and verify ownership
    conversation_response = supabase.table("conversations").select("*, chatbots!inner(user_id)").eq("id", conversation_id).execute()
    
    if not conversation_response.data or conversation_response.data[0]["chatbots"]["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    try:
        supabase.table("conversations").delete().eq("id", conversation_id).execute()
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )