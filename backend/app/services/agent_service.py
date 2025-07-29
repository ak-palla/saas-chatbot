"""
LangChain Agent Service with Tool Calling
Implements AI agents with custom tools and capabilities
"""

import logging
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool, StructuredTool
from langchain.schema import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.vector_store_service import vector_store_service

logger = logging.getLogger(__name__)


class DocumentSearchInput(BaseModel):
    """Input for document search tool"""
    query: str = Field(description="Search query for documents")
    limit: int = Field(default=5, description="Maximum number of results")


class CalculatorInput(BaseModel):
    """Input for calculator tool"""
    expression: str = Field(description="Mathematical expression to evaluate")


class AgentService:
    """Service for LangChain agents with custom tools"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.1  # Lower temperature for tool use
        )
        self.agents_cache = {}  # Cache agents per chatbot
    
    def create_document_search_tool(self, chatbot_id: str) -> BaseTool:
        """
        Create a document search tool for a specific chatbot
        
        Args:
            chatbot_id: ID of chatbot to search documents for
            
        Returns:
            Document search tool
        """
        async def search_documents(query: str, limit: int = 5) -> str:
            """Search through the chatbot's knowledge base"""
            try:
                results = await vector_store_service.search_documents(
                    query=query,
                    chatbot_id=chatbot_id,
                    limit=limit
                )
                
                if not results:
                    return "No relevant documents found for your query."
                
                # Format results
                formatted_results = []
                for i, result in enumerate(results, 1):
                    doc_info = result.get('document_info', {})
                    filename = doc_info.get('filename', 'Unknown')
                    content = result.get('content', '')[:200] + '...'  # Truncate
                    
                    formatted_results.append(
                        f"{i}. From '{filename}':\n{content}"
                    )
                
                return "\n\n".join(formatted_results)
                
            except Exception as e:
                logger.error(f"Document search tool error: {str(e)}")
                return f"Error searching documents: {str(e)}"
        
        return StructuredTool(
            name="document_search",
            description="Search through uploaded documents and knowledge base to find relevant information",
            args_schema=DocumentSearchInput,
            func=search_documents,
            coroutine=search_documents
        )
    
    def create_calculator_tool(self) -> BaseTool:
        """
        Create a calculator tool for mathematical operations
        
        Returns:
            Calculator tool
        """
        def calculate(expression: str) -> str:
            """Perform mathematical calculations"""
            try:
                # Basic safety check
                allowed_chars = set('0123456789+-*/()., ')
                if not all(c in allowed_chars for c in expression):
                    return "Error: Only basic mathematical operations are allowed"
                
                # Evaluate expression safely
                result = eval(expression)
                return f"Result: {result}"
                
            except ZeroDivisionError:
                return "Error: Division by zero"
            except Exception as e:
                return f"Error: Invalid mathematical expression - {str(e)}"
        
        return StructuredTool(
            name="calculator",
            description="Perform mathematical calculations and solve equations",
            args_schema=CalculatorInput,
            func=calculate
        )
    
    def create_datetime_tool(self) -> BaseTool:
        """
        Create a tool for date/time operations
        
        Returns:
            DateTime tool
        """
        def get_datetime_info(query: str = "current") -> str:
            """Get current date and time information"""
            try:
                now = datetime.now()
                
                if "date" in query.lower():
                    return f"Current date: {now.strftime('%Y-%m-%d')}"
                elif "time" in query.lower():
                    return f"Current time: {now.strftime('%H:%M:%S')}"
                else:
                    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                    
            except Exception as e:
                return f"Error getting date/time: {str(e)}"
        
        return StructuredTool(
            name="datetime",
            description="Get current date and time information",
            func=get_datetime_info
        )
    
    def create_knowledge_stats_tool(self, chatbot_id: str) -> BaseTool:
        """
        Create a tool to get knowledge base statistics
        
        Args:
            chatbot_id: ID of chatbot
            
        Returns:
            Knowledge stats tool
        """
        async def get_knowledge_stats() -> str:
            """Get statistics about the chatbot's knowledge base"""
            try:
                stats = await vector_store_service.get_chatbot_knowledge_stats(chatbot_id)
                
                return f"""Knowledge Base Statistics:
- Documents: {stats['document_count']}
- Text chunks: {stats['embedding_count']}
- Average chunks per document: {stats['avg_embeddings_per_document']}
- Knowledge base ready: {'Yes' if stats['knowledge_base_ready'] else 'No'}"""
                
            except Exception as e:
                return f"Error getting knowledge stats: {str(e)}"
        
        return StructuredTool(
            name="knowledge_stats",
            description="Get statistics about the chatbot's knowledge base and uploaded documents",
            func=get_knowledge_stats,
            coroutine=get_knowledge_stats
        )
    
    def get_default_tools(self, chatbot_id: str) -> List[BaseTool]:
        """
        Get default tools for a chatbot agent
        
        Args:
            chatbot_id: ID of chatbot
            
        Returns:
            List of default tools
        """
        return [
            self.create_document_search_tool(chatbot_id),
            self.create_calculator_tool(),
            self.create_datetime_tool(),
            self.create_knowledge_stats_tool(chatbot_id)
        ]
    
    def create_agent_prompt(self, system_prompt: Optional[str] = None) -> ChatPromptTemplate:
        """
        Create a prompt template for the agent
        
        Args:
            system_prompt: Custom system prompt
            
        Returns:
            Configured prompt template
        """
        base_system = system_prompt or """You are a helpful AI assistant with access to various tools. 
Use the tools available to you to provide accurate and helpful responses.

Guidelines:
1. Always use the document_search tool when users ask questions that might be answered by uploaded documents
2. Use the calculator tool for any mathematical calculations
3. Use the datetime tool when users ask about current date or time
4. Be clear about what information comes from documents vs your general knowledge
5. If you can't find relevant information in the documents, say so clearly"""
        
        return ChatPromptTemplate.from_messages([
            ("system", base_system),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def create_agent(
        self, 
        chatbot_id: str,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None
    ) -> AgentExecutor:
        """
        Create a LangChain agent for a chatbot
        
        Args:
            chatbot_id: ID of chatbot
            tools: Custom tools (uses defaults if None)
            system_prompt: Custom system prompt
            
        Returns:
            Configured agent executor
        """
        try:
            # Use provided tools or defaults
            agent_tools = tools or self.get_default_tools(chatbot_id)
            
            # Create prompt
            prompt = self.create_agent_prompt(system_prompt)
            
            # Create agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=agent_tools,
                prompt=prompt
            )
            
            # Create executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=agent_tools,
                verbose=True,  # Enable logging
                handle_parsing_errors=True,
                max_iterations=5,  # Prevent infinite loops
                max_execution_time=30  # 30 second timeout
            )
            
            logger.info(f"Created agent for chatbot {chatbot_id} with {len(agent_tools)} tools")
            return agent_executor
            
        except Exception as e:
            logger.error(f"Agent creation failed: {str(e)}")
            raise Exception(f"Failed to create agent: {str(e)}")
    
    def get_cached_agent(
        self, 
        chatbot_id: str,
        system_prompt: Optional[str] = None
    ) -> AgentExecutor:
        """
        Get cached agent or create new one
        
        Args:
            chatbot_id: ID of chatbot
            system_prompt: System prompt (affects caching)
            
        Returns:
            Agent executor
        """
        cache_key = f"{chatbot_id}_{hash(system_prompt or '')}"
        
        if cache_key not in self.agents_cache:
            self.agents_cache[cache_key] = self.create_agent(
                chatbot_id=chatbot_id,
                system_prompt=system_prompt
            )
        
        return self.agents_cache[cache_key]
    
    async def run_agent(
        self,
        chatbot_id: str,
        message: str,
        chat_history: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run agent with a user message
        
        Args:
            chatbot_id: ID of chatbot
            message: User message
            chat_history: Previous conversation history
            system_prompt: System prompt for the agent
            
        Returns:
            Agent response with metadata
        """
        try:
            # Get or create agent
            agent = self.get_cached_agent(chatbot_id, system_prompt)
            
            # Format chat history for LangChain
            formatted_history = []
            if chat_history:
                for msg in chat_history[-10:]:  # Keep last 10 messages
                    if msg["role"] == "user":
                        formatted_history.append(("human", msg["content"]))
                    elif msg["role"] == "assistant":
                        formatted_history.append(("ai", msg["content"]))
            
            # Run agent
            start_time = datetime.now()
            
            response = await agent.ainvoke({
                "input": message,
                "chat_history": formatted_history
            })
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract response data
            output = response.get("output", "")
            intermediate_steps = response.get("intermediate_steps", [])
            
            # Format tool usage information
            tools_used = []
            for step in intermediate_steps:
                if hasattr(step, 'tool') and hasattr(step, 'tool_input'):
                    tools_used.append({
                        "tool": step.tool,
                        "input": step.tool_input
                    })
            
            logger.info(f"Agent completed in {execution_time:.2f}s using {len(tools_used)} tools")
            
            return {
                "content": output,
                "tools_used": tools_used,
                "execution_time": execution_time,
                "intermediate_steps": len(intermediate_steps)
            }
            
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            return {
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "error": str(e),
                "tools_used": [],
                "execution_time": 0
            }
    
    def add_custom_tool(
        self, 
        chatbot_id: str, 
        tool: BaseTool
    ) -> bool:
        """
        Add a custom tool to a chatbot's agent
        
        Args:
            chatbot_id: ID of chatbot
            tool: Custom tool to add
            
        Returns:
            True if successful
        """
        try:
            # Remove cached agent to force recreation with new tool
            cache_keys_to_remove = [
                key for key in self.agents_cache.keys() 
                if key.startswith(f"{chatbot_id}_")
            ]
            
            for key in cache_keys_to_remove:
                del self.agents_cache[key]
            
            logger.info(f"Added custom tool '{tool.name}' to chatbot {chatbot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom tool: {str(e)}")
            return False
    
    def list_available_tools(self, chatbot_id: str) -> List[Dict[str, str]]:
        """
        List all available tools for a chatbot
        
        Args:
            chatbot_id: ID of chatbot
            
        Returns:
            List of tool descriptions
        """
        try:
            tools = self.get_default_tools(chatbot_id)
            
            return [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in tools
            ]
        except Exception as e:
            logger.error(f"Failed to list tools: {str(e)}")
            return [
                {
                    "name": "document_search",
                    "description": "Search through uploaded documents and knowledge base"
                },
                {
                    "name": "calculator", 
                    "description": "Perform mathematical calculations"
                },
                {
                    "name": "datetime",
                    "description": "Get current date and time information"
                }
            ]
    
    def clear_agent_cache(self, chatbot_id: Optional[str] = None):
        """
        Clear agent cache
        
        Args:
            chatbot_id: Specific chatbot ID to clear (clears all if None)
        """
        if chatbot_id:
            cache_keys_to_remove = [
                key for key in self.agents_cache.keys() 
                if key.startswith(f"{chatbot_id}_")
            ]
            for key in cache_keys_to_remove:
                del self.agents_cache[key]
        else:
            self.agents_cache.clear()
        
        logger.info(f"Cleared agent cache for {'all chatbots' if not chatbot_id else chatbot_id}")


# Global instance
agent_service = AgentService()