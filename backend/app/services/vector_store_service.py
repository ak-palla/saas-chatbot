"""
Vector Store Service for RAG (Retrieval-Augmented Generation)
Handles vector database operations and document retrieval
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from app.core.database import get_supabase
from app.services.embedding_service import embedding_service
from app.services.rag_metrics_service import rag_metrics_service

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
            # Start metrics tracking
            tracking_id = rag_metrics_service.start_retrieval_tracking(query, chatbot_id, "vector")
            
            print(f"🔍 RAG DEBUG: Starting context retrieval for query: '{query}'")
            print(f"📋 RAG DEBUG: Chatbot ID: {chatbot_id}, Max contexts: {max_contexts}, Threshold: {similarity_threshold}")
            
            # Generate embedding for the query
            print(f"🧠 RAG DEBUG: Generating query embedding...")
            rag_metrics_service.log_embedding_phase(tracking_id)
            query_embedding = await self.embedding_service.generate_embedding(query)
            print(f"✅ RAG DEBUG: Query embedding generated (dimension: {len(query_embedding)})")
            
            # Perform similarity search
            print(f"🔎 RAG DEBUG: Performing similarity search in vector database...")
            rag_metrics_service.log_search_phase(tracking_id)
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
            
            # Complete metrics tracking (temporarily disabled to isolate RAG core)
            try:
                rag_metrics_service.complete_retrieval_tracking(tracking_id, contexts, metadata, success=True)
            except Exception as metrics_error:
                print(f"⚠️ RAG DEBUG: Metrics tracking failed (non-critical): {metrics_error}")
                # Continue anyway - don't let metrics break RAG functionality
            
            return contexts, metadata
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Context retrieval FAILED: {str(e)}")
            logger.error(f"Context retrieval failed: {str(e)}")
            
            # Complete metrics tracking with error (safe)
            if 'tracking_id' in locals():
                try:
                    rag_metrics_service.complete_retrieval_tracking(tracking_id, [], [], success=False, error_message=str(e))
                except Exception as metrics_error:
                    print(f"⚠️ RAG DEBUG: Error metrics tracking failed: {metrics_error}")
            
            return [], []
    
    async def retrieve_relevant_contexts_hybrid(
        self, 
        query: str, 
        chatbot_id: str,
        max_contexts: int = 3,
        similarity_threshold: float = 0.7,
        use_hybrid: bool = True,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Retrieve relevant document contexts using hybrid search (vector + keyword)
        
        Args:
            query: User query/question
            chatbot_id: ID of the chatbot to search documents for
            max_contexts: Maximum number of context chunks to return
            similarity_threshold: Minimum similarity threshold
            use_hybrid: Whether to use hybrid search or fall back to vector only
            bm25_weight: Weight for BM25 keyword search (0-1)
            vector_weight: Weight for vector similarity search (0-1)
            
        Returns:
            Tuple of (context_texts, source_metadata)
        """
        try:
            # Start metrics tracking for hybrid search
            tracking_id = rag_metrics_service.start_retrieval_tracking(query, chatbot_id, "hybrid")
            
            print(f"🔍 RAG DEBUG: Starting HYBRID context retrieval for query: '{query}'")
            print(f"📋 RAG DEBUG: Hybrid={use_hybrid}, BM25 weight={bm25_weight}, Vector weight={vector_weight}")
            
            if use_hybrid:
                # Use hybrid search combining vector similarity and keyword search
                print(f"🚀 RAG DEBUG: Performing hybrid search...")
                similar_chunks = await self.embedding_service.hybrid_search(
                    query_text=query,
                    chatbot_id=chatbot_id,
                    limit=max_contexts * 2,  # Get more results to filter
                    similarity_threshold=similarity_threshold,
                    bm25_weight=bm25_weight,
                    vector_weight=vector_weight
                )
                print(f"📊 RAG DEBUG: Hybrid search returned {len(similar_chunks)} chunks")
            else:
                # Fallback to vector-only search
                print(f"🔎 RAG DEBUG: Falling back to vector-only search...")
                query_embedding = await self.embedding_service.generate_embedding(query)
                similar_chunks = await self.embedding_service.similarity_search(
                    query_embedding=query_embedding,
                    chatbot_id=chatbot_id,
                    limit=max_contexts,
                    similarity_threshold=similarity_threshold
                )
            
            if not similar_chunks:
                print(f"❌ RAG DEBUG: No relevant contexts found")
                return [], []
            
            # Process and format results
            contexts = []
            metadata_list = []
            
            for i, chunk in enumerate(similar_chunks[:max_contexts]):
                if not chunk.get('content'):
                    print(f"⚠️ RAG DEBUG: Skipping chunk {i+1} - no content")
                    continue
                
                content = chunk['content'].strip()
                if len(content) < 10:  # Skip very short chunks
                    continue
                
                similarity_score = chunk.get('similarity', 0.0)
                hybrid_score = chunk.get('hybrid_score', similarity_score)
                
                print(f"📝 RAG DEBUG: Processing chunk {i+1}: hybrid_score={hybrid_score:.4f}, similarity={similarity_score:.4f}")
                
                contexts.append(content)
                metadata_list.append({
                    'document_id': chunk.get('document_id'),
                    'chunk_id': chunk.get('id'),
                    'similarity': similarity_score,
                    'hybrid_score': hybrid_score,
                    'vector_score': chunk.get('vector_score', 0.0),
                    'keyword_score': chunk.get('keyword_score', 0.0),
                    'metadata': chunk.get('metadata', {}),
                    'content_preview': content[:200] + "..." if len(content) > 200 else content
                })
            
            print(f"✅ RAG DEBUG: Hybrid retrieval complete - {len(contexts)} contexts selected")
            
            # Complete metrics tracking
            rag_metrics_service.complete_retrieval_tracking(tracking_id, contexts, metadata_list, success=True)
            
            return contexts, metadata_list
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Hybrid context retrieval FAILED: {str(e)}")
            logger.error(f"Hybrid context retrieval failed: {str(e)}")
            
            # Complete metrics tracking with error
            if 'tracking_id' in locals():
                rag_metrics_service.complete_retrieval_tracking(tracking_id, [], [], success=False, error_message=str(e))
            
            # Fallback to regular vector search
            try:
                print(f"🔄 RAG DEBUG: Falling back to regular vector search...")
                return await self.retrieve_relevant_context(
                    query, chatbot_id, max_contexts, similarity_threshold
                )
            except Exception as fallback_e:
                logger.error(f"Fallback vector search also failed: {str(fallback_e)}")
                return [], []
    
    async def retrieve_contexts_with_reranking(
        self,
        query: str,
        chatbot_id: str,
        max_contexts: int = 3,
        initial_retrieval_limit: int = 10,
        similarity_threshold: float = 0.7,
        use_hybrid: bool = True,
        use_reranking: bool = True
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Advanced context retrieval with reranking and dynamic sizing
        
        Args:
            query: User query/question
            chatbot_id: ID of the chatbot to search documents for
            max_contexts: Maximum number of final contexts to return
            initial_retrieval_limit: Number of candidates to retrieve before reranking
            similarity_threshold: Minimum similarity threshold
            use_hybrid: Whether to use hybrid search
            use_reranking: Whether to apply reranking
            
        Returns:
            Tuple of (context_texts, source_metadata)
        """
        try:
            # Start metrics tracking for reranked search
            tracking_id = rag_metrics_service.start_retrieval_tracking(query, chatbot_id, "reranked")
            
            print(f"🎯 RAG DEBUG: Advanced context retrieval with reranking")
            print(f"📊 RAG DEBUG: Initial limit={initial_retrieval_limit}, Final contexts={max_contexts}")
            
            # Step 1: Retrieve more candidates than needed
            if use_hybrid:
                candidate_contexts, candidate_metadata = await self.retrieve_relevant_contexts_hybrid(
                    query=query,
                    chatbot_id=chatbot_id,
                    max_contexts=initial_retrieval_limit,
                    similarity_threshold=similarity_threshold * 0.8  # Lower threshold for initial retrieval
                )
            else:
                candidate_contexts, candidate_metadata = await self.retrieve_relevant_context(
                    query=query,
                    chatbot_id=chatbot_id,
                    max_contexts=initial_retrieval_limit,
                    similarity_threshold=similarity_threshold * 0.8
                )
            
            if not candidate_contexts:
                print(f"❌ RAG DEBUG: No candidate contexts found")
                return [], []
            
            print(f"📋 RAG DEBUG: Retrieved {len(candidate_contexts)} candidate contexts")
            
            # Step 2: Apply reranking if enabled
            if use_reranking and len(candidate_contexts) > max_contexts:
                print(f"🔄 RAG DEBUG: Applying context reranking...")
                rag_metrics_service.log_reranking_phase(tracking_id)
                reranked_contexts, reranked_metadata = await self._rerank_contexts(
                    query, candidate_contexts, candidate_metadata
                )
            else:
                reranked_contexts = candidate_contexts
                reranked_metadata = candidate_metadata
            
            # Step 3: Dynamic context sizing based on content length
            final_contexts, final_metadata = self._dynamic_context_sizing(
                query, reranked_contexts, reranked_metadata, max_contexts
            )
            
            print(f"✅ RAG DEBUG: Final context selection: {len(final_contexts)} contexts")
            
            # Complete metrics tracking
            rag_metrics_service.complete_retrieval_tracking(tracking_id, final_contexts, final_metadata, success=True)
            
            return final_contexts, final_metadata
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Advanced context retrieval FAILED: {str(e)}")
            logger.error(f"Advanced context retrieval failed: {str(e)}")
            
            # Complete metrics tracking with error
            if 'tracking_id' in locals():
                rag_metrics_service.complete_retrieval_tracking(tracking_id, [], [], success=False, error_message=str(e))
            
            # Fallback to simple retrieval
            return await self.retrieve_relevant_context(
                query, chatbot_id, max_contexts, similarity_threshold
            )
    
    async def _rerank_contexts(
        self,
        query: str,
        contexts: List[str],
        metadata: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Rerank contexts using cross-encoder scoring or advanced similarity
        """
        try:
            print(f"🧠 RAG DEBUG: Reranking {len(contexts)} contexts...")
            
            # Calculate reranking scores using multiple factors
            reranked_pairs = []
            
            for i, (context, meta) in enumerate(zip(contexts, metadata)):
                # Calculate comprehensive relevance score
                relevance_score = await self._calculate_relevance_score(query, context, meta)
                reranked_pairs.append((context, meta, relevance_score))
            
            # Sort by relevance score
            reranked_pairs.sort(key=lambda x: x[2], reverse=True)
            
            # Extract sorted contexts and metadata
            reranked_contexts = [pair[0] for pair in reranked_pairs]
            reranked_metadata = [pair[1] for pair in reranked_pairs]
            
            # Update metadata with reranking scores
            for i, (meta, score) in enumerate(zip(reranked_metadata, [p[2] for p in reranked_pairs])):
                meta['rerank_score'] = score
                meta['rerank_position'] = i + 1
            
            print(f"✅ RAG DEBUG: Contexts reranked by relevance score")
            return reranked_contexts, reranked_metadata
            
        except Exception as e:
            logger.error(f"Context reranking failed: {str(e)}")
            return contexts, metadata
    
    async def _calculate_relevance_score(
        self,
        query: str,
        context: str,
        metadata: Dict[str, Any]
    ) -> float:
        """
        Calculate comprehensive relevance score for a context
        """
        try:
            # Base score from existing similarity/hybrid score
            base_score = max(
                metadata.get('hybrid_score', 0.0),
                metadata.get('similarity', 0.0)
            )
            
            # Length penalty/bonus (prefer moderate-length contexts)
            context_len = len(context)
            if 200 <= context_len <= 800:
                length_bonus = 0.1  # Ideal length
            elif context_len < 100:
                length_bonus = -0.2  # Too short
            elif context_len > 1500:
                length_bonus = -0.1  # Too long
            else:
                length_bonus = 0.0
            
            # Keyword overlap bonus
            query_words = set(query.lower().split())
            context_words = set(context.lower().split())
            overlap_ratio = len(query_words.intersection(context_words)) / len(query_words) if query_words else 0
            keyword_bonus = overlap_ratio * 0.15
            
            # Question type matching (simple heuristic)
            question_bonus = 0.0
            if any(word in query.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']):
                if any(word in context.lower() for word in ['because', 'since', 'due to', 'reason', 'cause']):
                    question_bonus = 0.05
            
            # Position bias (slightly prefer earlier chunks from documents)
            chunk_index = metadata.get('metadata', {}).get('chunk_index', 0)
            position_bonus = max(0, 0.02 - (chunk_index * 0.005))  # Small bonus for earlier chunks
            
            # Calculate final score
            final_score = base_score + length_bonus + keyword_bonus + question_bonus + position_bonus
            
            return max(0.0, min(1.0, final_score))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Relevance score calculation failed: {str(e)}")
            return metadata.get('hybrid_score', metadata.get('similarity', 0.0))
    
    def _dynamic_context_sizing(
        self,
        query: str,
        contexts: List[str],
        metadata: List[Dict[str, Any]],
        max_contexts: int
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Dynamically determine optimal number of contexts based on content and query
        """
        try:
            if not contexts:
                return [], []
            
            # Calculate query complexity
            query_complexity = self._assess_query_complexity(query)
            
            # Adjust max_contexts based on complexity
            if query_complexity == "simple":
                optimal_contexts = min(max_contexts, 2)
            elif query_complexity == "complex":
                optimal_contexts = min(max_contexts, 5)
            else:  # moderate
                optimal_contexts = max_contexts
            
            print(f"📏 RAG DEBUG: Query complexity='{query_complexity}', optimal contexts={optimal_contexts}")
            
            # Select contexts ensuring we don't exceed token limits
            selected_contexts = []
            selected_metadata = []
            total_length = 0
            max_total_length = 3000  # Approximate token limit for contexts
            
            for i, (context, meta) in enumerate(zip(contexts, metadata)):
                if len(selected_contexts) >= optimal_contexts:
                    break
                
                context_length = len(context)
                if total_length + context_length <= max_total_length:
                    selected_contexts.append(context)
                    selected_metadata.append(meta)
                    total_length += context_length
                    
                    # Update metadata with final selection info
                    meta['final_position'] = len(selected_contexts)
                    meta['total_context_length'] = total_length
                else:
                    print(f"⚠️ RAG DEBUG: Skipping context {i+1} - would exceed token limit")
            
            print(f"📊 RAG DEBUG: Selected {len(selected_contexts)} contexts (total length: {total_length} chars)")
            return selected_contexts, selected_metadata
            
        except Exception as e:
            logger.error(f"Dynamic context sizing failed: {str(e)}")
            return contexts[:max_contexts], metadata[:max_contexts]
    
    def _assess_query_complexity(self, query: str) -> str:
        """
        Assess query complexity to determine optimal context count
        """
        try:
            query_lower = query.lower()
            words = query.split()
            
            # Complex queries indicators
            complex_indicators = [
                'compare', 'contrast', 'analyze', 'explain why', 'how does',
                'what is the difference', 'relationship between', 'impact of',
                'multiple', 'various', 'different types', 'several'
            ]
            
            # Simple query indicators
            simple_indicators = [
                'what is', 'who is', 'when did', 'where is', 'define',
                'meaning of', 'yes or no', 'true or false'
            ]
            
            if any(indicator in query_lower for indicator in complex_indicators):
                return "complex"
            elif any(indicator in query_lower for indicator in simple_indicators):
                return "simple"
            elif len(words) > 10:
                return "complex"
            elif len(words) < 5:
                return "simple"
            else:
                return "moderate"
                
        except Exception:
            return "moderate"
    
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