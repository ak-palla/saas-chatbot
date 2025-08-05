from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import logging
from app.models.chatbot import Chatbot, ChatbotCreate, ChatbotUpdate
from app.core.database import get_supabase_admin
from app.core.config import settings  # Import settings directly
from app.services.document_service import document_service
from pydantic import BaseModel
import os
from groq import Groq
import time

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/", response_model=Chatbot)
async def create_chatbot(chatbot: ChatbotCreate, user_email: str):
    """Create a new chatbot - Simplified Supabase-native approach"""
    logger.info("🚀 Creating new chatbot (Supabase-native)")
    logger.info(f"📝 Chatbot data: {chatbot.dict()}")
    logger.info(f"👤 User email: {user_email}")
    
    supabase = get_supabase_admin()
    
    try:
        # Find or create user in our custom users table by email
        logger.info(f"🔍 Looking up user by email in users table: {user_email}")
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            # User doesn't exist in our users table, create them
            logger.info(f"👤 Creating new user record for: {user_email}")
            import uuid
            new_user_id = str(uuid.uuid4())
            
            new_user_data = {
                "id": new_user_id,
                "email": user_email,
                "hashed_password": "supabase_auth",  # Placeholder since Supabase handles auth
                "is_active": True,
                "subscription_tier": "free"
            }
            
            create_user_response = supabase.table("users").insert(new_user_data).execute()
            user_id = create_user_response.data[0]["id"]
            logger.info(f"✅ Created new user with ID: {user_id}")
        else:
            user_id = user_response.data[0]["id"]
            logger.info(f"✅ Found existing user ID: {user_id}")
        
        # Create chatbot with user_id
        chatbot_data = {
            **chatbot.dict(),
            "user_id": user_id
        }
        
        logger.info(f"💾 Creating chatbot: {chatbot_data}")
        response = supabase.table("chatbots").insert(chatbot_data).execute()
        
        logger.info(f"🎉 Chatbot created successfully: {response.data[0]}")
        return response.data[0]
        
    except Exception as e:
        logger.error(f"💥 Error creating chatbot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chatbot: {str(e)}"
        )


@router.get("/", response_model=List[Chatbot])
async def get_user_chatbots(user_email: str):
    """Get all chatbots for the current user - Simplified approach"""
    logger.info(f"📋 Getting chatbots for user: {user_email}")
    
    supabase = get_supabase_admin()
    
    try:
        # Get user ID from our users table
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            # User doesn't exist in our users table, create them
            logger.info(f"👤 Creating new user record for: {user_email}")
            import uuid
            new_user_id = str(uuid.uuid4())
            
            new_user_data = {
                "id": new_user_id,
                "email": user_email,
                "hashed_password": "supabase_auth",  # Placeholder since Supabase handles auth
                "is_active": True,
                "subscription_tier": "free"
            }
            
            create_user_response = supabase.table("users").insert(new_user_data).execute()
            user_id = create_user_response.data[0]["id"]
            logger.info(f"✅ Created new user with ID: {user_id}")
        else:
            user_id = user_response.data[0]["id"]
            logger.info(f"✅ Found existing user ID: {user_id}")
        
        # Get user's chatbots
        response = supabase.table("chatbots").select("*").eq("user_id", user_id).execute()
        logger.info(f"✅ Found {len(response.data)} chatbots")
        return response.data
        
    except Exception as e:
        logger.error(f"💥 Error getting chatbots: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbots: {str(e)}"
        )


@router.get("/{chatbot_id}", response_model=Chatbot)
async def get_chatbot(chatbot_id: str, user_email: str):
    """Get a specific chatbot - Simplified approach"""
    logger.info(f"🔍 Getting chatbot {chatbot_id} for user: {user_email}")
    
    supabase = get_supabase_admin()
    
    try:
        # Get user ID from our users table
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            # User doesn't exist in our users table, create them
            logger.info(f"👤 Creating new user record for: {user_email}")
            import uuid
            new_user_id = str(uuid.uuid4())
            
            new_user_data = {
                "id": new_user_id,
                "email": user_email,
                "hashed_password": "supabase_auth",  # Placeholder since Supabase handles auth
                "is_active": True,
                "subscription_tier": "free"
            }
            
            create_user_response = supabase.table("users").insert(new_user_data).execute()
            user_id = create_user_response.data[0]["id"]
            logger.info(f"✅ Created new user with ID: {user_id}")
        else:
            user_id = user_response.data[0]["id"]
            logger.info(f"✅ Found existing user ID: {user_id}")
        
        # Get chatbot belonging to this user
        response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        logger.info(f"✅ Found chatbot: {response.data[0]['name']}")
        return response.data[0]
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"💥 Error getting chatbot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbot: {str(e)}"
        )


@router.put("/{chatbot_id}", response_model=Chatbot)
async def update_chatbot(chatbot_id: str, chatbot_update: ChatbotUpdate, user_email: str):
    """Update a chatbot - Simplified approach"""
    logger.info(f"🔄 VOICE DEBUG: ==================== BACKEND UPDATE ====================")
    logger.info(f"🔄 VOICE DEBUG: Updating chatbot {chatbot_id} for user: {user_email}")
    logger.info(f"🔄 VOICE DEBUG: Received chatbot_update object: {chatbot_update}")
    logger.info(f"🔄 VOICE DEBUG: chatbot_update.dict(): {chatbot_update.dict()}")
    logger.info(f"🔄 VOICE DEBUG: behavior_config in update: {chatbot_update.behavior_config}")
    logger.info(f"🔄 VOICE DEBUG: enableVoice in behavior_config: {chatbot_update.behavior_config.get('enableVoice') if chatbot_update.behavior_config else 'N/A'}")
    
    supabase = get_supabase_admin()
    
    # Get user ID from our users table
    user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
    if not user_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_id = user_response.data[0]["id"]
    
    # Check if chatbot exists and belongs to user
    existing = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    
    logger.info(f"🔄 VOICE DEBUG: Existing chatbot data: {existing.data[0]}")
    logger.info(f"🔄 VOICE DEBUG: Existing behavior_config: {existing.data[0].get('behavior_config')}")
    
    # Update chatbot
    update_data = {k: v for k, v in chatbot_update.dict().items() if v is not None}
    logger.info(f"🔄 VOICE DEBUG: Final update_data being sent to Supabase: {update_data}")
    logger.info(f"🔄 VOICE DEBUG: behavior_config in final update_data: {update_data.get('behavior_config')}")
    
    try:
        response = supabase.table("chatbots").update(update_data).eq("id", chatbot_id).execute()
        logger.info(f"✅ VOICE DEBUG: Chatbot updated successfully")
        logger.info(f"✅ VOICE DEBUG: Updated chatbot data: {response.data[0]}")
        logger.info(f"✅ VOICE DEBUG: Updated behavior_config: {response.data[0].get('behavior_config')}")
        
        updated_chatbot = response.data[0]
        
        # Process documents and generate embeddings after chatbot update
        logger.info(f"🔄 EMBEDDING: Starting automatic document processing for chatbot {chatbot_id}")
        logger.info(f"🔍 EMBEDDING DEBUG: user_id type: {type(user_id)}")
        logger.info(f"🔍 EMBEDDING DEBUG: user_id value: {user_id}")
        logger.info(f"🔍 EMBEDDING DEBUG: chatbot_id type: {type(chatbot_id)}")
        logger.info(f"🔍 EMBEDDING DEBUG: chatbot_id value: {chatbot_id}")
        logger.info(f"🔍 EMBEDDING DEBUG: document_service type: {type(document_service)}")
        logger.info(f"🔍 EMBEDDING DEBUG: method exists: {hasattr(document_service, 'process_chatbot_documents')}")
        
        try:
            logger.info(f"🔍 EMBEDDING DEBUG: About to call: document_service.process_chatbot_documents('{chatbot_id}', '{user_id}')")
            processing_result = await document_service.process_chatbot_documents(chatbot_id, user_id)
            logger.info(f"✅ EMBEDDING: Document processing completed: {processing_result}")
            
            # Add embedding stats to the response
            updated_chatbot["embedding_stats"] = processing_result
            
        except Exception as embed_error:
            logger.error(f"⚠️ EMBEDDING: Document processing failed: {str(embed_error)}")
            # Don't fail the chatbot update if embedding processing fails
            updated_chatbot["embedding_stats"] = {
                "success": False,
                "error": str(embed_error),
                "processed_count": 0,
                "total_embeddings": 0
            }
        
        return updated_chatbot
        
    except Exception as e:
        logger.error(f"💥 VOICE DEBUG: Error updating chatbot: {str(e)}")
        logger.error(f"💥 VOICE DEBUG: Error type: {type(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update chatbot")


@router.delete("/{chatbot_id}")
async def delete_chatbot(chatbot_id: str, user_email: str):
    """Delete a chatbot - Simplified approach"""
    logger.info(f"🗑️ Deleting chatbot {chatbot_id} for user: {user_email}")
    
    supabase = get_supabase_admin()
    
    # Get user ID from our users table
    user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
    if not user_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_id = user_response.data[0]["id"]
    
    # Check if chatbot exists and belongs to user
    existing = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    
    try:
        supabase.table("chatbots").delete().eq("id", chatbot_id).execute()
        logger.info(f"✅ Chatbot deleted successfully")
        return {"message": "Chatbot deleted successfully"}
    except Exception as e:
        logger.error(f"💥 Error deleting chatbot: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete chatbot")


# Chat testing models
class TestChatMessage(BaseModel):
    role: str
    content: str

class TestChatRequest(BaseModel):
    message: str
    conversation_history: List[TestChatMessage] = []

class TestChatResponse(BaseModel):
    response: str
    conversation_id: str = "test"
    rag_enabled: bool = False
    context_count: int = 0
<<<<<<< Updated upstream
    model: str = "unknown"
=======
    model_used: Optional[str] = None
>>>>>>> Stashed changes


@router.post("/{chatbot_id}/test-chat", response_model=TestChatResponse)
async def test_chatbot_chat(chatbot_id: str, chat_request: TestChatRequest, user_email: str):
    """Test chat endpoint for chatbot - RAG-enabled chat using message service"""
    logger.info(f"🧪 Testing chat for chatbot {chatbot_id} by user: {user_email}")
    logger.info(f"📨 Chat request: {chat_request.dict()}")
    
    try:
        supabase = get_supabase_admin()
        
        # Get user ID from our users table
        logger.info(f"🔍 Looking up user: {user_email}")
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        if not user_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user_id = user_response.data[0]["id"]
        logger.info(f"✅ Found user ID: {user_id}")
        
        # Get chatbot and verify ownership
        logger.info(f"🔍 Looking up chatbot: {chatbot_id}")
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        chatbot = chatbot_response.data[0]
        logger.info(f"✅ Found chatbot: {chatbot['name']}")
        
        print(f"🧪 RAG DEBUG: Using RAG-enabled message service for test chat")
        
        # Use the message service for proper RAG integration
        from app.services.message_service import message_service
        from app.models.message import ChatRequest
        
        # Convert test request to ChatRequest format
        conversation_history = []
        for msg in chat_request.conversation_history:
            role = msg.role.lower()
            if role == "bot":
                role = "assistant"
            conversation_history.append({
                "role": role,
                "content": msg.content
            })
        
        # Create ChatRequest for message service
        chat_req = ChatRequest(
            chatbot_id=chatbot_id,
            message=chat_request.message,
            model=chatbot.get("model", "llama-3.1-8b-instant"),
            use_rag=True,  # Enable RAG for testing
            temperature=0.7,
            max_tokens=1000
        )
        
        print(f"🎯 RAG DEBUG: Processing test chat with RAG enabled")
        
        # Process message through message service (includes RAG)
        response = await message_service._generate_llm_response(
            request=chat_req,
            chatbot=chatbot,
            conversation_history=conversation_history
        )
        
        print(f"✅ RAG DEBUG: Test chat response generated successfully")
        print(f"📊 RAG DEBUG: Response metadata - RAG enabled: {response.get('rag_enabled')}, Context count: {response.get('context_count', 0)}")
        
        return TestChatResponse(
            response=response["content"],
            conversation_id="test",
            rag_enabled=response.get("rag_enabled", False),
            context_count=response.get("context_count", 0),
<<<<<<< Updated upstream
            model=response.get("model", "unknown")
=======
            model_used=response.get("model", chat_req.model)
>>>>>>> Stashed changes
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"💥 Unexpected error in test chat: {str(e)}")
        logger.error(f"💥 Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )