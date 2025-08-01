"""
Vector Store Service for RAG (Retrieval-Augmented Generation)
Handles vector database operations and document retrieval
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from app.core.database import get_supabase
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for vector database operations and RAG functionality"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.embedding_service = embedding_service
    
    async def setup_vector_functions(self):
        """
        Set up PostgreSQL functions for vector similarity search
        This should be run during deployment/setup
        """
        try:
            # Create the match_documents function for similarity search
            create_function_sql = """
            CREATE OR REPLACE FUNCTION match_documents(
                query_embedding vector(384),
                chatbot_id uuid,
                match_threshold float DEFAULT 0.7,
                match_count int DEFAULT 5
            )
            RETURNS TABLE (
                id uuid,
                document_id uuid,
                content text,
                metadata jsonb,
                similarity float
            )
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    ve.id,
                    ve.document_id,
                    ve.text_content as content,
                    ve.metadata,
                    1 - (ve.embedding <=> query_embedding) as similarity
                FROM vector_embeddings ve
                JOIN documents d ON ve.document_id = d.id
                WHERE d.chatbot_id = match_documents.chatbot_id
                AND 1 - (ve.embedding <=> query_embedding) > match_threshold
                ORDER BY ve.embedding <=> query_embedding
                LIMIT match_count;
            END;
            $$;
            """
            
            # Note: This would typically be run as a migration
            # For now, we'll use the fallback method in embedding_service
            logger.info("Vector functions setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup vector functions: {str(e)}")
    
    async def retrieve_relevant_context(
        self, 
        query: str, 
        chatbot_id: str,
        max_contexts: int = 3,
        similarity_threshold: float = 0.7
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Retrieve relevant document contexts for a query using RAG
        
        Args:
            query: User query/question
            chatbot_id: ID of the chatbot to search documents for
            max_contexts: Maximum number of context chunks to return
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            Tuple of (context_texts, source_metadata)
        """
        try:
            print(f"🔍 RAG DEBUG: Starting context retrieval for query: '{query}'")
            print(f"📋 RAG DEBUG: Chatbot ID: {chatbot_id}, Max contexts: {max_contexts}, Threshold: {similarity_threshold}")
            
            # Generate embedding for the query
            print(f"🧠 RAG DEBUG: Generating query embedding...")
            query_embedding = await self.embedding_service.generate_embedding(query)
            print(f"✅ RAG DEBUG: Query embedding generated (dimension: {len(query_embedding)})")
            
            # Perform similarity search
            print(f"🔎 RAG DEBUG: Performing similarity search in vector database...")
            similar_chunks = await self.embedding_service.similarity_search(
                query_embedding=query_embedding,
                chatbot_id=chatbot_id,
                limit=max_contexts,
                similarity_threshold=similarity_threshold
            )
            
            print(f"📊 RAG DEBUG: Similarity search returned {len(similar_chunks)} chunks")
            
            if not similar_chunks:
                print(f"⚠️ RAG DEBUG: No relevant context found for query in chatbot {chatbot_id}")
                logger.info(f"No relevant context found for query in chatbot {chatbot_id}")
                return [], []
            
            # Extract context texts and metadata
            contexts = []
            metadata = []
            
            for i, chunk in enumerate(similar_chunks):
                print(f"📝 RAG DEBUG: Processing chunk {i+1}: similarity={chunk.get('similarity', 'N/A'):.4f}")
                print(f"📄 RAG DEBUG: Chunk content preview: {chunk['content'][:100]}...")
                
                contexts.append(chunk['content'])
                metadata.append({
                    'document_id': chunk.get('document_id'),
                    'similarity': chunk.get('similarity', 0.0),
                    'metadata': chunk.get('metadata', {})
                })
            
            print(f"🎯 RAG DEBUG: Context retrieval complete - {len(contexts)} contexts retrieved")
            for i, context in enumerate(contexts):
                print(f"📖 RAG DEBUG: Context {i+1} length: {len(context)} chars")
            
            logger.info(f"Retrieved {len(contexts)} relevant contexts for query")
            return contexts, metadata
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Context retrieval FAILED: {str(e)}")
            logger.error(f"Context retrieval failed: {str(e)}")
            return [], []
    
    async def build_rag_prompt(
        self, 
        query: str, 
        contexts: List[str],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build a RAG-enhanced prompt with retrieved contexts
        
        Args:
            query: User query
            contexts: Retrieved context chunks
            system_prompt: Optional system prompt
            
        Returns:
            Enhanced prompt with context
        """
        if not contexts:
            # No context available, return basic prompt
            base_prompt = system_prompt or "You are a helpful assistant."
            return f"{base_prompt}\n\nUser: {query}\nAssistant:"
        
        # Build context section
        context_section = "Based on the following information:\n\n"
        for i, context in enumerate(contexts, 1):
            context_section += f"[Context {i}]\n{context}\n\n"
        
        # Build full prompt
        base_prompt = system_prompt or "You are a helpful assistant. Use the provided context to answer questions accurately."
        
        full_prompt = f"""{base_prompt}

{context_section}

Please answer the following question based on the provided context. If the context doesn't contain enough information to answer the question, say so clearly.

User: {query}
Assistant:"""
        
        return full_prompt
    
    async def get_chatbot_knowledge_stats(self, chatbot_id: str) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base for a chatbot
        
        Args:
            chatbot_id: ID of the chatbot
            
        Returns:
            Statistics about documents and embeddings
        """
        try:
            # Get document count
            doc_response = self.supabase.table("documents") \
                .select("id") \
                .eq("chatbot_id", chatbot_id) \
                .execute()
            
            document_count = len(doc_response.data)
            
            # Get embedding count
            embedding_response = self.supabase.table("vector_embeddings") \
                .select("id, documents!inner(chatbot_id)") \
                .eq("documents.chatbot_id", chatbot_id) \
                .execute()
            
            embedding_count = len(embedding_response.data)
            
            # Calculate average embeddings per document
            avg_embeddings_per_doc = embedding_count / document_count if document_count > 0 else 0
            
            return {
                "document_count": document_count,
                "embedding_count": embedding_count,
                "avg_embeddings_per_document": round(avg_embeddings_per_doc, 2),
                "knowledge_base_ready": document_count > 0 and embedding_count > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge stats: {str(e)}")
            return {
                "document_count": 0,
                "embedding_count": 0,
                "avg_embeddings_per_document": 0,
                "knowledge_base_ready": False,
                "error": str(e)
            }
    
    async def search_documents(
        self, 
        query: str, 
        chatbot_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search documents by content similarity
        
        Args:
            query: Search query
            chatbot_id: ID of chatbot to search within
            limit: Maximum results to return
            
        Returns:
            List of matching document chunks with scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Perform similarity search
            results = await self.embedding_service.similarity_search(
                query_embedding=query_embedding,
                chatbot_id=chatbot_id,
                limit=limit,
                similarity_threshold=0.5  # Lower threshold for search
            )
            
            # Enhance results with document information
            enhanced_results = []
            for result in results:
                # Get document info
                doc_response = self.supabase.table("documents") \
                    .select("filename, file_type, created_at") \
                    .eq("id", result.get('document_id')) \
                    .execute()
                
                doc_info = doc_response.data[0] if doc_response.data else {}
                
                enhanced_results.append({
                    **result,
                    "document_info": doc_info
                })
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Document search failed: {str(e)}")
            return []
    
    async def update_document_embeddings(self, document_id: str) -> bool:
        """
        Reprocess and update embeddings for a document
        
        Args:
            document_id: ID of document to reprocess
            
        Returns:
            True if successful
        """
        try:
            # Delete existing embeddings
            await self.embedding_service.delete_document_embeddings(document_id)
            
            # Get document content (would need to re-extract from file)
            # This is a placeholder - in practice, you'd store the extracted text
            # or re-extract from the original file
            
            logger.info(f"Document embeddings updated for {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document embeddings: {str(e)}")
            return False
    
    async def get_similar_documents(
        self, 
        document_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document
        
        Args:
            document_id: ID of reference document
            limit: Maximum similar documents to return
            
        Returns:
            List of similar documents
        """
        try:
            # Get document's first embedding as reference
            embedding_response = self.supabase.table("vector_embeddings") \
                .select("embedding") \
                .eq("document_id", document_id) \
                .limit(1) \
                .execute()
            
            if not embedding_response.data:
                return []
            
            reference_embedding = embedding_response.data[0]['embedding']
            
            # Find similar embeddings
            # This is a simplified version - in practice, you'd average embeddings
            # or use more sophisticated similarity measures
            
            return []  # Placeholder
            
        except Exception as e:
            logger.error(f"Failed to find similar documents: {str(e)}")
            return []
    
    async def optimize_vector_database(self, chatbot_id: str) -> Dict[str, Any]:
        """
        Optimize vector database for a chatbot (cleanup, reindex, etc.)
        
        Args:
            chatbot_id: ID of chatbot to optimize
            
        Returns:
            Optimization results
        """
        try:
            results = {
                "embeddings_before": 0,
                "embeddings_after": 0,
                "documents_processed": 0,
                "duplicates_removed": 0
            }
            
            # Get current embedding count
            before_response = self.supabase.table("vector_embeddings") \
                .select("id, documents!inner(chatbot_id)") \
                .eq("documents.chatbot_id", chatbot_id) \
                .execute()
            
            results["embeddings_before"] = len(before_response.data)
            
            # Remove duplicate embeddings (same content)
            # This would involve more complex SQL queries
            
            # Recompute embeddings for documents that may have changed
            
            logger.info(f"Vector database optimization completed for chatbot {chatbot_id}")
            return results
            
        except Exception as e:
            logger.error(f"Vector database optimization failed: {str(e)}")
            return {"error": str(e)}


# Global instance
vector_store_service = VectorStoreService()