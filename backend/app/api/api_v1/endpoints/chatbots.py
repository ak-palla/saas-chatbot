from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from app.models.chatbot import Chatbot, ChatbotCreate, ChatbotUpdate
from app.core.database import get_supabase_admin
from app.core.config import settings  # Import settings directly
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
    
    # Get user ID from our users table
    user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
    if not user_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_id = user_response.data[0]["id"]
    
    # Get user's chatbots
    response = supabase.table("chatbots").select("*").eq("user_id", user_id).execute()
    logger.info(f"✅ Found {len(response.data)} chatbots")
    return response.data


@router.get("/{chatbot_id}", response_model=Chatbot)
async def get_chatbot(chatbot_id: str, user_email: str):
    """Get a specific chatbot - Simplified approach"""
    logger.info(f"🔍 Getting chatbot {chatbot_id} for user: {user_email}")
    
    supabase = get_supabase_admin()
    
    # Get user ID from our users table
    user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
    if not user_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_id = user_response.data[0]["id"]
    
    # Get chatbot belonging to this user
    response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    
    logger.info(f"✅ Found chatbot: {response.data[0]['name']}")
    return response.data[0]


@router.put("/{chatbot_id}", response_model=Chatbot)
async def update_chatbot(chatbot_id: str, chatbot_update: ChatbotUpdate, user_email: str):
    """Update a chatbot - Simplified approach"""
    logger.info(f"🔄 Updating chatbot {chatbot_id} for user: {user_email}")
    
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
    
    # Update chatbot
    update_data = {k: v for k, v in chatbot_update.dict().items() if v is not None}
    
    try:
        response = supabase.table("chatbots").update(update_data).eq("id", chatbot_id).execute()
        logger.info(f"✅ Chatbot updated successfully")
        return response.data[0]
    except Exception as e:
        logger.error(f"💥 Error updating chatbot: {str(e)}")
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


@router.post("/{chatbot_id}/test-chat", response_model=TestChatResponse)
async def test_chatbot_chat(chatbot_id: str, chat_request: TestChatRequest, user_email: str):
    """Test chat endpoint for chatbot - Simple Groq API integration"""
    logger.info(f"🧪 Testing chat for chatbot {chatbot_id} by user: {user_email}")
    logger.info(f"📨 Chat request: {chat_request.dict()}")
    
    try:
        # Test basic functionality first
        logger.info("🔧 Starting basic validation...")
        
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
        
        # Debug: Check all settings
        logger.info(f"🔍 Checking settings...")
        logger.info(f"🔍 Settings file exists: {settings.model_dump()}")
        logger.info(f"🔍 GROQ_API_KEY length: {len(settings.GROQ_API_KEY or '')}")
        
        # Use settings directly - this should resolve the environment variable issue
        groq_api_key = settings.GROQ_API_KEY
        if not groq_api_key:
            logger.error("❌ GROQ_API_KEY not found in settings")
            logger.error(f"❌ Available settings: {settings.model_dump().keys()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Groq API key not configured")
        logger.info(f"✅ Using GROQ_API_KEY from settings: {groq_api_key[:8]}...")
        logger.info(f"✅ Groq API key found: {groq_api_key[:8]}...")
        
        # Test Groq import
        logger.info("🔧 Testing Groq import...")
        try:
            from groq import Groq
            logger.info("✅ Groq import successful")
        except ImportError as import_error:
            logger.error(f"❌ Groq import failed: {import_error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Groq import failed: {import_error}")
        
        # Initialize Groq client
        logger.info("🔧 Initializing Groq client...")
        try:
            client = Groq(api_key=groq_api_key)
            logger.info("✅ Groq client initialized")
        except Exception as client_error:
            logger.error(f"❌ Groq client initialization failed: {client_error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Groq client init failed: {client_error}")
        
        # Build messages for Groq API
        messages = []
        
        # Add system prompt from chatbot configuration
        if chatbot.get("system_prompt"):
            messages.append({
                "role": "system",
                "content": chatbot["system_prompt"]
            })
            logger.info(f"✅ Added system prompt: {chatbot['system_prompt'][:50]}...")
        
        # Add conversation history
        for msg in chat_request.conversation_history:
            # Map frontend roles to proper API roles
            role = msg.role.lower()
            if role == "bot":
                role = "assistant"
            elif role == "user":
                role = "user"
            else:
                role = "assistant"  # default
            messages.append({
                "role": role,
                "content": msg.content
            })
        logger.info(f"✅ Added {len(chat_request.conversation_history)} history messages")
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": chat_request.message
        })
        logger.info(f"✅ Added user message: {chat_request.message[:50]}...")
        
# Use supported Groq models from llm_service
        from app.services.llm_service import llm_service
        available_models = list(llm_service.MODELS.keys())
        default_model = llm_service.DEFAULT_MODEL
        
        model_name = chatbot.get("model", default_model)
        
        # Validate model is supported
        if model_name not in available_models:
            logger.warning(f"⚠️ Model {model_name} not in supported list, using {default_model}")
            model_name = default_model
        logger.info(f"💬 Sending {len(messages)} messages to Groq API using model: {model_name}")
        
        # Call Groq API
        start_time = time.time()
        try:
            completion = client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=0.7,
                max_tokens=1000,
                timeout=30.0,  # Add timeout to prevent hanging
            )
            response_time = time.time() - start_time
            logger.info(f"⚡ Groq API response received in {response_time:.2f}s")
        except Exception as groq_error:
            logger.error(f"❌ Groq API call failed: {groq_error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Groq API call failed: {groq_error}")
        
        # Extract response content
        try:
            response_content = completion.choices[0].message.content
            logger.info(f"🤖 Bot response: {response_content[:100]}...")
        except Exception as extract_error:
            logger.error(f"❌ Response extraction failed: {extract_error}")
            logger.info(f"📋 Response object type: {type(completion)}")
            logger.info(f"📋 Choices: {completion.choices}")
            logger.info(f"📋 First choice type: {type(completion.choices[0])}")
            # Try to access content more defensively
            try:
                choice = completion.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    response_content = choice.message.content
                else:
                    response_content = str(choice)
                    logger.warning(f"⚠️ Using string representation: {response_content[:100]}...")
            except Exception as fallback_error:
                response_content = "I'm sorry, I encountered an issue processing your request. Please try again."
                logger.error(f"❌ Fallback response: {response_content}")
        
        return TestChatResponse(
            response=response_content,
            conversation_id="test"
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