"""
Message Processing Service
Handles chat completion, context retrieval, and conversation management
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.core.database import get_supabase
from app.services.llm_service import llm_service
from app.services.vector_store_service import vector_store_service
from app.services.agent_service import agent_service
from app.models.message import ChatMessage, ChatRequest, ChatResponse, StreamingChatChunk

logger = logging.getLogger(__name__)


class MessageService:
    """Service for processing chat messages and managing conversations"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.llm_service = llm_service
        self.vector_store_service = vector_store_service
        self.agent_service = agent_service
    
    async def process_chat_message(
        self, 
        request: ChatRequest, 
        user_id: str
    ) -> ChatResponse:
        """
        Process a chat message and generate AI response
        
        Args:
            request: Chat request with message and configuration
            user_id: ID of the user sending the message
            
        Returns:
            Chat response with AI-generated content
        """
        try:
            start_time = datetime.now()
            
            # Verify chatbot ownership
            chatbot = await self._verify_chatbot_access(request.chatbot_id, user_id)
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                request.conversation_id,
                request.chatbot_id,
                request.session_id,
                user_id
            )
            
            # Add user message to conversation
            await self._add_message_to_conversation(
                conversation["id"],
                request.message,
                "user"
            )
            
            # Get conversation history
            conversation_history = await self._get_conversation_history(conversation["id"])
            
            # Generate AI response
            if chatbot.get("agent_enabled", True):  # Use agent by default
                response_data = await self._generate_agent_response(
                    request=request,
                    chatbot=chatbot,
                    conversation_history=conversation_history
                )
            else:
                response_data = await self._generate_llm_response(
                    request=request,
                    chatbot=chatbot,
                    conversation_history=conversation_history
                )
            
            # Add AI response to conversation
            await self._add_message_to_conversation(
                conversation["id"],
                response_data["content"],
                "assistant",
                metadata={
                    "model": response_data.get("model"),
                    "usage": response_data.get("usage"),
                    "tools_used": response_data.get("tools_used", []),
                    "rag_enabled": response_data.get("rag_enabled", False)
                }
            )
            
            # Record usage
            await self._record_usage(
                user_id=user_id,
                chatbot_id=request.chatbot_id,
                conversation_id=conversation["id"],
                usage=response_data.get("usage", {}),
                model=response_data.get("model", "unknown")
            )
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Build response
            return ChatResponse(
                content=response_data["content"],
                conversation_id=conversation["id"],
                model=response_data.get("model", "unknown"),
                usage=response_data.get("usage", {}),
                rag_enabled=response_data.get("rag_enabled", False),
                context_count=response_data.get("context_count", 0),
                tools_used=response_data.get("tools_used", []),
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Chat message processing failed: {str(e)}")
            raise Exception(f"Failed to process chat message: {str(e)}")
    
    async def process_streaming_chat(
        self, 
        request: ChatRequest, 
        user_id: str
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """
        Process streaming chat message
        
        Args:
            request: Chat request
            user_id: User ID
            
        Yields:
            Streaming response chunks
        """
        try:
            # Verify chatbot ownership
            chatbot = await self._verify_chatbot_access(request.chatbot_id, user_id)
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                request.conversation_id,
                request.chatbot_id,
                request.session_id,
                user_id
            )
            
            # Add user message
            await self._add_message_to_conversation(
                conversation["id"],
                request.message,
                "user"
            )
            
            # Get conversation history
            conversation_history = await self._get_conversation_history(conversation["id"])
            
            # Generate streaming response
            full_content = ""
            async for chunk in self._generate_streaming_response(
                request, chatbot, conversation_history
            ):
                if chunk.get("error"):
                    yield StreamingChatChunk(
                        content="",
                        full_content="",
                        finished=True,
                        conversation_id=conversation["id"],
                        error=chunk["error"]
                    )
                    return
                
                content = chunk.get("content", "")
                full_content = chunk.get("full_content", full_content + content)
                finished = chunk.get("finished", False)
                
                yield StreamingChatChunk(
                    content=content,
                    full_content=full_content,
                    finished=finished,
                    conversation_id=conversation["id"]
                )
                
                if finished:
                    # Add final response to conversation
                    await self._add_message_to_conversation(
                        conversation["id"],
                        full_content,
                        "assistant"
                    )
                    break
            
        except Exception as e:
            logger.error(f"Streaming chat failed: {str(e)}")
            yield StreamingChatChunk(
                content="",
                full_content="",
                finished=True,
                error=str(e)
            )
    
    async def _verify_chatbot_access(self, chatbot_id: str, user_id: str) -> Dict[str, Any]:
        """Verify user has access to chatbot"""
        response = self.supabase.table("chatbots") \
            .select("*") \
            .eq("id", chatbot_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise ValueError("Chatbot not found or access denied")
        
        return response.data[0]
    
    async def _get_or_create_conversation(
        self,
        conversation_id: Optional[str],
        chatbot_id: str,
        session_id: Optional[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Get existing conversation or create new one"""
        if conversation_id:
            # Verify existing conversation
            response = self.supabase.table("conversations") \
                .select("*, chatbots!inner(user_id)") \
                .eq("id", conversation_id) \
                .eq("chatbots.user_id", user_id) \
                .execute()
            
            if response.data:
                return response.data[0]
        
        # Create new conversation
        conversation_data = {
            "chatbot_id": chatbot_id,
            "session_id": session_id or str(uuid.uuid4()),
            "title": "New Conversation",
            "messages": []
        }
        
        response = self.supabase.table("conversations") \
            .insert(conversation_data) \
            .execute()
        
        return response.data[0]
    
    async def _add_message_to_conversation(
        self,
        conversation_id: str,
        content: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to conversation"""
        # Get current messages
        response = self.supabase.table("conversations") \
            .select("messages") \
            .eq("id", conversation_id) \
            .execute()
        
        if not response.data:
            raise ValueError("Conversation not found")
        
        current_messages = response.data[0]["messages"] or []
        
        # Add new message
        new_message = {
            "id": str(uuid.uuid4()),
            "content": content,
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        current_messages.append(new_message)
        
        # Update conversation
        self.supabase.table("conversations") \
            .update({
                "messages": current_messages,
                "updated_at": datetime.now().isoformat()
            }) \
            .eq("id", conversation_id) \
            .execute()
    
    async def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation message history"""
        response = self.supabase.table("conversations") \
            .select("messages") \
            .eq("id", conversation_id) \
            .execute()
        
        if not response.data:
            return []
        
        messages = response.data[0]["messages"] or []
        
        # Format for LLM service
        formatted_messages = []
        for msg in messages[-20:]:  # Keep last 20 messages
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_messages
    
    async def _generate_agent_response(
        self,
        request: ChatRequest,
        chatbot: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate response using LangChain agent"""
        try:
            response = await self.agent_service.run_agent(
                chatbot_id=request.chatbot_id,
                message=request.message,
                chat_history=conversation_history,
                system_prompt=chatbot.get("system_prompt")
            )
            
            return {
                "content": response["content"],
                "model": "agent",
                "usage": {"total_tokens": 0},  # Agent doesn't return token usage
                "tools_used": response.get("tools_used", []),
                "rag_enabled": len(response.get("tools_used", [])) > 0,
                "context_count": 0
            }
            
        except Exception as e:
            logger.error(f"Agent response failed: {str(e)}")
            # Fallback to LLM
            return await self._generate_llm_response(request, chatbot, conversation_history)
    
    async def _generate_llm_response(
        self,
        request: ChatRequest,
        chatbot: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate response using LLM with optional RAG"""
        try:
            print(f"🤖 RAG DEBUG: Starting LLM response generation")
            print(f"📊 RAG DEBUG: RAG enabled: {request.use_rag}")
            print(f"🎯 RAG DEBUG: Chatbot ID: {request.chatbot_id}")
            print(f"💬 RAG DEBUG: User message: '{request.message}'")
            
            if request.use_rag:
                print(f"🔍 RAG DEBUG: RAG mode - retrieving relevant context...")
                
                # Retrieve relevant context
                contexts, context_metadata = await self.vector_store_service.retrieve_relevant_context(
                    query=request.message,
                    chatbot_id=request.chatbot_id,
                    max_contexts=3
                )
                
                print(f"📚 RAG DEBUG: Retrieved {len(contexts)} context chunks")
                if contexts:
                    for i, context in enumerate(contexts):
                        print(f"📄 RAG DEBUG: Context {i+1} preview: {context[:150]}...")
                        print(f"📊 RAG DEBUG: Context {i+1} metadata: {context_metadata[i] if i < len(context_metadata) else 'N/A'}")
                else:
                    print(f"⚠️ RAG DEBUG: No relevant context found - falling back to standard response")
                
                if contexts:
                    print(f"🧠 RAG DEBUG: Generating RAG-enhanced response with context...")
                    # Generate RAG response
                    response = await self.llm_service.generate_rag_response(
                        query=request.message,
                        contexts=contexts,
                        conversation_history=conversation_history,
                        system_prompt=chatbot.get("system_prompt"),
                        model=request.model
                    )
                    
                    response["context_count"] = len(contexts)
                    response["rag_enabled"] = True
                    print(f"✅ RAG DEBUG: RAG response generated successfully with {len(contexts)} contexts")
                    return response
                else:
                    print(f"🔄 RAG DEBUG: No context available, generating standard response...")
                    # Fall back to standard response
                    messages = conversation_history + [{"role": "user", "content": request.message}]
                    
                    response = await self.llm_service.generate_response(
                        messages=messages,
                        model=request.model,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        system_prompt=chatbot.get("system_prompt")
                    )
                    
                    response["rag_enabled"] = False
                    response["context_count"] = 0
                    print(f"✅ RAG DEBUG: Standard response generated (no context available)")
                    return response
            else:
                print(f"🔄 RAG DEBUG: Standard mode - generating response without RAG...")
                
                # Generate standard response
                messages = conversation_history + [{"role": "user", "content": request.message}]
                
                response = await self.llm_service.generate_response(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    system_prompt=chatbot.get("system_prompt")
                )
                
                response["rag_enabled"] = False
                response["context_count"] = 0
                print(f"✅ RAG DEBUG: Standard response generated")
                return response
                
        except Exception as e:
            print(f"💥 RAG DEBUG: LLM response generation FAILED: {str(e)}")
            logger.error(f"LLM response failed: {str(e)}")
            raise
    
    async def _generate_streaming_response(
        self,
        request: ChatRequest,
        chatbot: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming LLM response"""
        try:
            messages = conversation_history + [{"role": "user", "content": request.message}]
            
            async for chunk in self.llm_service.generate_streaming_response(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=chatbot.get("system_prompt")
            ):
                yield chunk
                
        except Exception as e:
            yield {"error": str(e), "finished": True}
    
    async def _record_usage(
        self,
        user_id: str,
        chatbot_id: str,
        conversation_id: str,
        usage: Dict[str, int],
        model: str
    ):
        """Record usage statistics"""
        try:
            usage_data = {
                "user_id": user_id,
                "chatbot_id": chatbot_id,
                "conversation_id": conversation_id,
                "message_count": 1,
                "tokens_used": usage.get("total_tokens", 0),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.table("usage_records").insert(usage_data).execute()
            
        except Exception as e:
            logger.warning(f"Usage recording failed: {str(e)}")
    
    async def get_conversation_summary(self, conversation_id: str, user_id: str) -> str:
        """Get conversation summary"""
        try:
            # Verify access
            response = self.supabase.table("conversations") \
                .select("messages, chatbots!inner(user_id)") \
                .eq("id", conversation_id) \
                .eq("chatbots.user_id", user_id) \
                .execute()
            
            if not response.data:
                raise ValueError("Conversation not found")
            
            messages = response.data[0]["messages"] or []
            
            # Format messages for summarization
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
            
            # Generate summary
            summary = await self.llm_service.summarize_conversation(formatted_messages)
            return summary
            
        except Exception as e:
            logger.error(f"Conversation summary failed: {str(e)}")
            return "Summary unavailable"


# Global instance
message_service = MessageService()