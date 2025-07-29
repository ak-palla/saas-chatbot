"""
Chat completion API endpoints
Handles AI-powered chat conversations
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json

from app.models.message import ChatRequest, ChatResponse, StreamingChatChunk
from app.core.auth import get_current_user
from app.services.message_service import message_service
# Rate limiting handled at middleware level

router = APIRouter()


@router.post("/completions", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI response for chat message
    
    This endpoint processes user messages and generates AI responses using:
    - RAG (Retrieval-Augmented Generation) for knowledge-based responses
    - LangChain agents with tool calling capabilities
    - Context from uploaded documents
    """
    try:
        # Validate request
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        if len(request.message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long (max 10,000 characters)"
            )
        
        # Process chat message
        response = await message_service.process_chat_message(
            request=request,
            user_id=current_user["id"]
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        )


@router.post("/completions/stream")
async def chat_completion_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate streaming AI response for chat message
    
    Returns Server-Sent Events (SSE) stream of response chunks
    """
    try:
        # Validate request
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Set streaming flag
        request.stream = True
        
        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generate SSE stream"""
            try:
                async for chunk in message_service.process_streaming_chat(
                    request=request,
                    user_id=current_user["id"]
                ):
                    # Format as SSE
                    chunk_json = json.dumps(chunk.dict())
                    yield f"data: {chunk_json}\n\n"
                    
                    if chunk.finished:
                        break
                
                # Send final SSE message
                yield "event: close\ndata: Stream complete\n\n"
                
            except Exception as e:
                error_chunk = StreamingChatChunk(
                    content="",
                    full_content="",
                    finished=True,
                    error=str(e)
                )
                error_json = json.dumps(error_chunk.dict())
                yield f"data: {error_json}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming chat failed: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a summary of a conversation"""
    try:
        summary = await message_service.get_conversation_summary(
            conversation_id=conversation_id,
            user_id=current_user["id"]
        )
        
        return {"summary": summary}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation summary: {str(e)}"
        )


@router.get("/models")
async def list_available_models():
    """List available AI models"""
    try:
        from app.services.llm_service import llm_service
        
        models = llm_service.list_available_models()
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/knowledge-stats")
async def get_knowledge_base_stats(
    chatbot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge base statistics for a chatbot"""
    try:
        # Verify chatbot ownership
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Get knowledge stats
        from app.services.vector_store_service import vector_store_service
        
        stats = await vector_store_service.get_chatbot_knowledge_stats(chatbot_id)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge stats: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/tools")
async def list_chatbot_tools(
    chatbot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List available tools for a chatbot's agent"""
    try:
        # Verify chatbot ownership
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Get available tools
        from app.services.agent_service import agent_service
        
        tools = agent_service.list_available_tools(chatbot_id)
        return {"tools": tools}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )