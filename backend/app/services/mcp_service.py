"""
MCP (Model Context Protocol) Service
Provides MCP-compatible interfaces for tool interoperability
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

from app.services.agent_service import agent_service
from app.services.vector_store_service import vector_store_service
from app.services.document_service import document_service

logger = logging.getLogger(__name__)


class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None
    
    
class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    
    
class MCPPrompt(BaseModel):
    """MCP Prompt definition"""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPRequest(BaseModel):
    """Generic MCP request"""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None


class MCPResponse(BaseModel):
    """Generic MCP response"""
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None


class MCPService:
    """Service implementing MCP protocol for tool and context management"""
    
    def __init__(self):
        self.server_info = {
            "name": "ChatBot RAG Server",
            "version": "1.0.0",
            "description": "MCP server providing RAG and document tools",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            }
        }
        
        # Register available tools
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    def _register_tools(self):
        """Register available MCP tools"""
        self.tools = {
            "document_search": MCPTool(
                name="document_search",
                description="Search through uploaded documents using RAG",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for finding relevant documents"
                        },
                        "chatbot_id": {
                            "type": "string",
                            "description": "ID of the chatbot to search documents for"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 5,
                            "description": "Maximum number of results to return"
                        },
                        "use_hybrid": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to use hybrid search (vector + keyword)"
                        }
                    },
                    "required": ["query", "chatbot_id"]
                }
            ),
            "document_upload": MCPTool(
                name="document_upload",
                description="Upload and process documents for RAG",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the document file"
                        },
                        "chatbot_id": {
                            "type": "string", 
                            "description": "ID of the chatbot to associate document with"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "ID of the user uploading the document"
                        }
                    },
                    "required": ["file_path", "chatbot_id", "user_id"]
                }
            ),
            "context_retrieval": MCPTool(
                name="context_retrieval",
                description="Retrieve relevant contexts with advanced reranking",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to find relevant contexts for"
                        },
                        "chatbot_id": {
                            "type": "string",
                            "description": "ID of the chatbot"
                        },
                        "max_contexts": {
                            "type": "integer",
                            "default": 3,
                            "description": "Maximum number of contexts to retrieve"
                        },
                        "use_reranking": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to apply context reranking"
                        },
                        "use_hybrid": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to use hybrid search"
                        }
                    },
                    "required": ["query", "chatbot_id"]
                }
            ),
            "embedding_generation": MCPTool(
                name="embedding_generation",
                description="Generate embeddings for text using optimized models",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to generate embeddings for"
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Embedding model to use (optional)"
                        }
                    },
                    "required": ["text"]
                }
            )
        }
    
    def _register_resources(self):
        """Register available MCP resources"""
        self.resources = {
            "documents": MCPResource(
                uri="chatbot://documents",
                name="Chatbot Documents",
                description="Access to uploaded documents and their contents",
                mimeType="application/json"
            ),
            "embeddings": MCPResource(
                uri="chatbot://embeddings", 
                name="Document Embeddings",
                description="Vector embeddings of document chunks",
                mimeType="application/json"
            ),
            "conversations": MCPResource(
                uri="chatbot://conversations",
                name="Chat Conversations",
                description="Access to chat conversation history",
                mimeType="application/json"
            )
        }
    
    def _register_prompts(self):
        """Register available MCP prompts"""
        self.prompts = {
            "rag_query": MCPPrompt(
                name="rag_query",
                description="Generate a RAG-enhanced response using retrieved contexts",
                arguments=[
                    {"name": "query", "description": "User question or query"},
                    {"name": "chatbot_id", "description": "ID of the chatbot"},
                    {"name": "max_contexts", "description": "Maximum contexts to retrieve"}
                ]
            ),
            "document_summary": MCPPrompt(
                name="document_summary", 
                description="Summarize uploaded documents",
                arguments=[
                    {"name": "document_id", "description": "ID of the document to summarize"},
                    {"name": "max_length", "description": "Maximum summary length"}
                ]
            )
        }
    
    async def handle_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle incoming MCP requests
        
        Args:
            request: MCP request object
            
        Returns:
            MCP response object
        """
        try:
            method = request.method
            params = request.params or {}
            
            logger.info(f"Handling MCP request: {method}")
            
            if method == "initialize":
                return MCPResponse(
                    result=self.server_info,
                    id=request.id
                )
            
            elif method == "tools/list":
                return MCPResponse(
                    result={"tools": list(self.tools.values())},
                    id=request.id
                )
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                result = await self._execute_tool(tool_name, tool_arguments)
                return MCPResponse(result=result, id=request.id)
            
            elif method == "resources/list":
                return MCPResponse(
                    result={"resources": list(self.resources.values())},
                    id=request.id
                )
            
            elif method == "resources/read":
                resource_uri = params.get("uri")
                result = await self._read_resource(resource_uri, params)
                return MCPResponse(result=result, id=request.id)
            
            elif method == "prompts/list":
                return MCPResponse(
                    result={"prompts": list(self.prompts.values())},
                    id=request.id
                )
            
            elif method == "prompts/get":
                prompt_name = params.get("name")
                result = await self._get_prompt(prompt_name, params)
                return MCPResponse(result=result, id=request.id)
            
            else:
                return MCPResponse(
                    error={
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    id=request.id
                )
        
        except Exception as e:
            logger.error(f"MCP request handling failed: {str(e)}")
            return MCPResponse(
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                id=request.id
            )
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute an MCP tool"""
        
        if tool_name == "document_search":
            query = arguments["query"]
            chatbot_id = arguments["chatbot_id"]
            limit = arguments.get("limit", 5)
            use_hybrid = arguments.get("use_hybrid", True)
            
            if use_hybrid:
                contexts, metadata = await vector_store_service.retrieve_relevant_contexts_hybrid(
                    query=query,
                    chatbot_id=chatbot_id,
                    max_contexts=limit
                )
            else:
                contexts, metadata = await vector_store_service.retrieve_relevant_context(
                    query=query,
                    chatbot_id=chatbot_id,
                    max_contexts=limit
                )
            
            return {
                "contexts": contexts,
                "metadata": metadata,
                "count": len(contexts)
            }
        
        elif tool_name == "context_retrieval":
            query = arguments["query"]
            chatbot_id = arguments["chatbot_id"]
            max_contexts = arguments.get("max_contexts", 3)
            use_reranking = arguments.get("use_reranking", True)
            use_hybrid = arguments.get("use_hybrid", True)
            
            if use_reranking:
                contexts, metadata = await vector_store_service.retrieve_contexts_with_reranking(
                    query=query,
                    chatbot_id=chatbot_id,
                    max_contexts=max_contexts,
                    use_hybrid=use_hybrid,
                    use_reranking=use_reranking
                )
            else:
                if use_hybrid:
                    contexts, metadata = await vector_store_service.retrieve_relevant_contexts_hybrid(
                        query=query,
                        chatbot_id=chatbot_id,
                        max_contexts=max_contexts
                    )
                else:
                    contexts, metadata = await vector_store_service.retrieve_relevant_context(
                        query=query,
                        chatbot_id=chatbot_id,
                        max_contexts=max_contexts
                    )
            
            return {
                "contexts": contexts,
                "metadata": metadata,
                "count": len(contexts),
                "reranking_applied": use_reranking,
                "hybrid_search": use_hybrid
            }
        
        elif tool_name == "embedding_generation":
            from app.services.embedding_service import embedding_service
            
            text = arguments["text"]
            model_name = arguments.get("model_name")
            
            embedding = await embedding_service.generate_embedding(text, model_name)
            
            return {
                "embedding": embedding,
                "dimension": len(embedding),
                "model": embedding_service.current_model_name
            }
        
        elif tool_name == "document_upload":
            # This would integrate with the document service
            # For now, return a placeholder
            return {
                "message": "Document upload not implemented in MCP interface yet",
                "status": "pending"
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource(self, uri: str, params: Dict[str, Any]) -> Any:
        """Read an MCP resource"""
        
        if uri == "chatbot://documents":
            # Return list of documents for a chatbot
            chatbot_id = params.get("chatbot_id")
            if not chatbot_id:
                raise ValueError("chatbot_id required for documents resource")
            
            # This would integrate with document service
            return {
                "resource_type": "documents",
                "chatbot_id": chatbot_id,
                "message": "Document listing not fully implemented yet"
            }
        
        elif uri == "chatbot://embeddings":
            # Return embedding statistics
            chatbot_id = params.get("chatbot_id")
            return {
                "resource_type": "embeddings",
                "chatbot_id": chatbot_id,
                "message": "Embeddings resource access not fully implemented yet"
            }
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    async def _get_prompt(self, prompt_name: str, params: Dict[str, Any]) -> Any:
        """Get an MCP prompt template"""
        
        if prompt_name == "rag_query":
            query = params.get("query", "")
            chatbot_id = params.get("chatbot_id", "")
            max_contexts = params.get("max_contexts", 3)
            
            return {
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a helpful AI assistant with access to relevant documents. Use the provided contexts to answer the user's question accurately and helpfully. Chatbot ID: {chatbot_id}"
                    },
                    {
                        "role": "user", 
                        "content": f"Please answer this question using the relevant document contexts: {query}"
                    }
                ],
                "context_limit": max_contexts
            }
        
        elif prompt_name == "document_summary":
            document_id = params.get("document_id", "")
            max_length = params.get("max_length", 200)
            
            return {
                "messages": [
                    {
                        "role": "system",
                        "content": f"Summarize the following document in no more than {max_length} words. Focus on key points and main ideas."
                    }
                ],
                "document_id": document_id,
                "max_length": max_length
            }
        
        else:
            raise ValueError(f"Unknown prompt: {prompt_name}")
    
    def get_server_capabilities(self) -> Dict[str, Any]:
        """Get MCP server capabilities"""
        return {
            "tools": {
                "listChanged": False
            },
            "resources": {
                "subscribe": False,
                "listChanged": False
            },
            "prompts": {
                "listChanged": False
            },
            "logging": {}
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """MCP server health check"""
        try:
            # Test basic functionality
            test_request = MCPRequest(method="initialize")
            response = await self.handle_mcp_request(test_request)
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "server_info": self.server_info,
                "tools_count": len(self.tools),
                "resources_count": len(self.resources),
                "prompts_count": len(self.prompts),
                "test_response": response.result is not None
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global instance
mcp_service = MCPService()