"""
LLM Service for ChatGroq API Integration
Handles conversation generation and AI responses
"""

import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from groq import Groq
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations using ChatGroq API"""
    
    # Available Groq models - updated to remove decommissioned ones
    MODELS = {
        "llama-3.1-70b-versatile": {
            "max_tokens": 8000,
            "context_window": 128000,
            "description": "Large model for complex tasks"
        },
        "llama-3.1-8b-instant": {
            "max_tokens": 8000,
            "context_window": 128000,
            "description": "Fast model for quick responses"
        },
        "llama3-8b-8192": {
            "max_tokens": 8192,
            "context_window": 8192,
            "description": "Standard model for general use"
        },
        "llama3-70b-8192": {
            "max_tokens": 8192,
            "context_window": 8192,
            "description": "Large model for complex tasks"
        },
        "gemma2-9b-it": {
            "max_tokens": 8192,
            "context_window": 8192,
            "description": "Google Gemma 2 model"
        }
    }
    
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.chat_groq = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=self.DEFAULT_MODEL,
            temperature=self.DEFAULT_TEMPERATURE
        )
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response for conversation
        
        Args:
            messages: List of conversation messages
            model: Model to use (defaults to DEFAULT_MODEL)
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            system_prompt: Optional system prompt
            
        Returns:
            Generated response with metadata
        """
        try:
            model = model or self.DEFAULT_MODEL
            temperature = temperature or self.DEFAULT_TEMPERATURE
            max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
            
            # Validate model
            if model not in self.MODELS:
                raise ValueError(f"Unsupported model: {model}")
            
            # Build message history
            chat_messages = []
            
            # Add system message if provided
            if system_prompt:
                chat_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add conversation history
            for msg in messages:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Generate response using Groq API
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=chat_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # Extract response content
            ai_response = response.choices[0].message.content
            
            # Calculate token usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Generated response using {model} ({usage['total_tokens']} tokens)")
            
            return {
                "content": ai_response,
                "model": model,
                "usage": usage,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming AI response
        
        Args:
            messages: List of conversation messages
            model: Model to use
            temperature: Response creativity
            max_tokens: Maximum response length
            system_prompt: Optional system prompt
            
        Yields:
            Streaming response chunks
        """
        try:
            model = model or self.DEFAULT_MODEL
            temperature = temperature or self.DEFAULT_TEMPERATURE
            max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
            
            # Build message history
            chat_messages = []
            
            if system_prompt:
                chat_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            for msg in messages:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Generate streaming response
            stream = self.groq_client.chat.completions.create(
                model=model,
                messages=chat_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            full_content = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    
                    yield {
                        "content": content,
                        "full_content": full_content,
                        "finished": False,
                        "model": model
                    }
            
            # Final chunk
            yield {
                "content": "",
                "full_content": full_content,
                "finished": True,
                "model": model
            }
            
            logger.info(f"Completed streaming response using {model}")
            
        except Exception as e:
            logger.error(f"Streaming response failed: {str(e)}")
            yield {
                "error": str(e),
                "finished": True
            }
    
    async def generate_rag_response(
        self,
        query: str,
        contexts: List[str],
        conversation_history: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response using RAG (Retrieval-Augmented Generation)
        
        Args:
            query: User query
            contexts: Retrieved document contexts
            conversation_history: Previous conversation messages
            system_prompt: Base system prompt
            model: Model to use
            
        Returns:
            Generated response with context awareness
        """
        try:
            # Build RAG-enhanced system prompt
            base_system = system_prompt or "You are a helpful AI assistant."
            
            if contexts:
                context_text = "\n\n".join([f"[Context {i+1}]: {ctx}" for i, ctx in enumerate(contexts)])
                
                rag_system_prompt = f"""{base_system}

You have access to the following relevant information to help answer questions:

{context_text}

Instructions:
1. Use the provided context information to answer questions when relevant
2. If the context doesn't contain enough information, clearly state this
3. Don't make up information that isn't in the context
4. Maintain conversation flow and context from previous messages"""
            else:
                rag_system_prompt = base_system
            
            # Build message history with RAG context
            messages = conversation_history.copy()
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Generate response
            response = await self.generate_response(
                messages=messages,
                system_prompt=rag_system_prompt,
                model=model
            )
            
            # Add RAG metadata
            response["rag_enabled"] = len(contexts) > 0
            response["context_count"] = len(contexts)
            
            return response
            
        except Exception as e:
            logger.error(f"RAG response generation failed: {str(e)}")
            raise Exception(f"Failed to generate RAG response: {str(e)}")
    
    def create_langchain_memory(self, max_messages: int = 10) -> ConversationBufferWindowMemory:
        """
        Create LangChain conversation memory
        
        Args:
            max_messages: Maximum messages to keep in memory
            
        Returns:
            Configured memory instance
        """
        return ConversationBufferWindowMemory(
            k=max_messages,
            return_messages=True,
            memory_key="chat_history"
        )
    
    async def summarize_conversation(
        self, 
        messages: List[Dict[str, str]],
        max_length: int = 200
    ) -> str:
        """
        Generate a summary of a conversation
        
        Args:
            messages: Conversation messages
            max_length: Maximum summary length
            
        Returns:
            Conversation summary
        """
        try:
            if not messages:
                return "Empty conversation"
            
            # Build conversation text
            conversation_text = "\n".join([
                f"{msg['role'].title()}: {msg['content']}" 
                for msg in messages
            ])
            
            # Create summarization prompt
            summary_messages = [{
                "role": "user",
                "content": f"""Please provide a brief summary of the following conversation in {max_length} characters or less:

{conversation_text}

Summary:"""
            }]
            
            # Generate summary
            response = await self.generate_response(
                messages=summary_messages,
                max_tokens=100,
                temperature=0.3  # Lower temperature for consistent summaries
            )
            
            summary = response["content"].strip()
            
            # Truncate if needed
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Conversation summarization failed: {str(e)}")
            return "Conversation summary unavailable"
    
    async def validate_message(self, content: str) -> bool:
        """
        Validate message content for safety and appropriateness
        
        Args:
            content: Message content to validate
            
        Returns:
            True if message is appropriate
        """
        try:
            # Basic validation
            if not content or not content.strip():
                return False
            
            if len(content) > 10000:  # Too long
                return False
            
            # Add more sophisticated content filtering here
            # This could include checking for inappropriate content,
            # spam detection, etc.
            
            return True
            
        except Exception as e:
            logger.error(f"Message validation failed: {str(e)}")
            return False
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        return self.MODELS.get(model, {})
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models with their specifications"""
        return self.MODELS.copy()
    
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token on average
        return len(text) // 4
    
    async def check_rate_limits(self, user_id: str) -> Dict[str, Any]:
        """
        Check rate limits for a user (placeholder)
        
        Args:
            user_id: User ID to check limits for
            
        Returns:
            Rate limit status
        """
        # This would integrate with actual rate limiting logic
        return {
            "requests_remaining": 100,
            "tokens_remaining": 10000,
            "reset_time": "2024-01-01T00:00:00Z"
        }


# Global instance
llm_service = LLMService()