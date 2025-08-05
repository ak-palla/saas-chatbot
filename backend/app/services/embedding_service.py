"""
Enhanced Embedding Service with Multiple Provider Support
Handles text embeddings generation using HuggingFace models and external APIs
"""

import logging
import os
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from huggingface_hub import login
import httpx
import asyncio

from app.core.config import settings
from app.core.database import get_supabase

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Enhanced service for handling text embeddings with multiple providers"""
    
    # Available embedding models (ordered by preference)
    AVAILABLE_MODELS = {
        "all-MiniLM-L6-v2": {
            "dimension": 384,
            "max_seq_length": 256,
            "description": "Fast, lightweight model good for most tasks",
            "provider": "huggingface"
        },
        "all-mpnet-base-v2": {
            "dimension": 768,
            "max_seq_length": 384,
            "description": "High quality model with good performance",
            "provider": "huggingface"
        },
        "sentence-transformers/all-MiniLM-L12-v2": {
            "dimension": 384,
            "max_seq_length": 256,
            "description": "Slightly larger than L6, better quality",
            "provider": "huggingface"
        },
        "BAAI/bge-small-en-v1.5": {
            "dimension": 384,
            "max_seq_length": 512,
            "description": "State-of-the-art BGE model, excellent for RAG",
            "provider": "huggingface"
        },
        "BAAI/bge-base-en-v1.5": {
            "dimension": 768,
            "max_seq_length": 512,
            "description": "Larger BGE model, best quality for RAG applications",
            "provider": "huggingface"
        }
    }
    
    DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"  # Better for RAG applications
    FALLBACK_MODEL = "all-MiniLM-L6-v2"  # Fast fallback model
    
    def __init__(self):
        self.supabase = get_supabase()
        self.model = None
        self.current_model_name = None
        self.embedding_dimension = 384  # Default for MiniLM
        
        # Login to Hugging Face if token is provided
        if settings.HUGGINGFACE_API_TOKEN:
            try:
                login(token=settings.HUGGINGFACE_API_TOKEN)
                logger.info("Logged in to Hugging Face Hub")
            except Exception as e:
                logger.warning(f"Failed to login to Hugging Face: {e}")
        
        # Initialize best available model with fallback
        self._initialize_best_model()
    
    def _load_model(self, model_name: str) -> bool:
        """
        Load a sentence transformer model
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_model_name == model_name and self.model is not None:
                return True  # Model already loaded
            
            logger.info(f"Loading embedding model: {model_name}")
            
            # Check if CUDA is available
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {device}")
            
            # Load the model
            self.model = SentenceTransformer(model_name, device=device)
            self.current_model_name = model_name
            
            # Update embedding dimension
            if model_name in self.AVAILABLE_MODELS:
                self.embedding_dimension = self.AVAILABLE_MODELS[model_name]["dimension"]
            else:
                # Get dimension from model
                test_embedding = self.model.encode(["test"], show_progress_bar=False)
                self.embedding_dimension = len(test_embedding[0])
            
            logger.info(f"Model loaded successfully. Dimension: {self.embedding_dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            
            # Fallback to a simpler model or dummy embeddings
            if model_name != self.DEFAULT_MODEL:
                logger.info(f"Falling back to default model: {self.DEFAULT_MODEL}")
                return self._load_model(self.DEFAULT_MODEL)
            
            # If default model fails, use dummy embeddings
            logger.warning("Using dummy embeddings - model loading failed")
            self.model = None
            self.current_model_name = "dummy"
            self.embedding_dimension = 384
            return False
    
    def _initialize_best_model(self) -> None:
        """Initialize the best available embedding model with fallback"""
        try:
            # Try to load the best RAG model first
            if self._load_model(self.DEFAULT_MODEL):
                logger.info(f"Successfully loaded best RAG model: {self.DEFAULT_MODEL}")
                return
        except Exception as e:
            logger.warning(f"Failed to load best model {self.DEFAULT_MODEL}: {e}")
        
        # Fallback to the original reliable model
        try:
            if self._load_model(self.FALLBACK_MODEL):
                logger.info(f"Successfully loaded fallback model: {self.FALLBACK_MODEL}")
                return
        except Exception as e:
            logger.error(f"Failed to load fallback model {self.FALLBACK_MODEL}: {e}")
        
        # Last resort - dummy embeddings
        logger.warning("All model loading failed - using dummy embeddings")
    
    def get_model_recommendation(self, use_case: str = "rag") -> str:
        """Get the recommended model for a specific use case"""
        if use_case.lower() == "rag":
            return "BAAI/bge-small-en-v1.5"  # Best for RAG with 384D
        elif use_case.lower() == "speed":
            return "all-MiniLM-L6-v2"  # Fastest model
        elif use_case.lower() == "quality":
            return "BAAI/bge-base-en-v1.5"  # Best quality but 768D
        else:
            return self.DEFAULT_MODEL
    
    async def generate_embedding(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Generate embedding for a single text using Hugging Face model
        
        Args:
            text: Text to embed
            model_name: Optional model name (uses current model if None)
            
        Returns:
            List of float values representing the embedding vector
        """
        try:
            print(f"🧠 RAG DEBUG: Generating embedding for text (length: {len(text)} chars)")
            print(f"🔧 RAG DEBUG: Using model: {self.current_model_name}")
            
            # Clean and prepare text
            text = self._prepare_text(text)
            print(f"✂️ RAG DEBUG: Text prepared (cleaned length: {len(text)} chars)")
            
            # Switch model if requested
            if model_name and model_name != self.current_model_name:
                print(f"🔄 RAG DEBUG: Switching to model: {model_name}")
                self._load_model(model_name)
            
            # Generate embedding
            if self.model is not None:
                print(f"✅ RAG DEBUG: Using actual model for embedding generation")
                # Use actual model
                embedding = self.model.encode([text], show_progress_bar=False)[0]
                embedding = embedding.tolist()  # Convert numpy array to list
                print(f"🎯 RAG DEBUG: Real embedding generated - dimension: {len(embedding)}")
            else:
                print(f"⚠️ RAG DEBUG: Model not loaded, using dummy embedding")
                # Use dummy embedding
                embedding = self._generate_dummy_embedding(text)
                print(f"🎲 RAG DEBUG: Dummy embedding generated - dimension: {len(embedding)}")
            
            print(f"📊 RAG DEBUG: Embedding vector preview: [{embedding[0]:.4f}, {embedding[1]:.4f}, ..., {embedding[-1]:.4f}]")
            logger.info(f"Generated {self.embedding_dimension}D embedding for text (length: {len(text)} chars)")
            return embedding
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Embedding generation FAILED: {str(e)}")
            logger.error(f"Failed to generate embedding: {str(e)}")
            # Return dummy embedding instead of failing
            dummy_embedding = self._generate_dummy_embedding(text)
            print(f"🎲 RAG DEBUG: Fallback to dummy embedding - dimension: {len(dummy_embedding)}")
            return dummy_embedding
    
    async def generate_embeddings_batch(self, texts: List[str], model_name: Optional[str] = None) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            model_name: Optional model name
            
        Returns:
            List of embedding vectors
        """
        try:
            # Clean and prepare texts
            cleaned_texts = [self._prepare_text(text) for text in texts]
            
            # Switch model if requested
            if model_name and model_name != self.current_model_name:
                self._load_model(model_name)
            
            # Generate embeddings
            if self.model is not None:
                # Use actual model for batch processing
                embeddings = self.model.encode(cleaned_texts, show_progress_bar=False)
                embeddings = [emb.tolist() for emb in embeddings]  # Convert to lists
            else:
                # Use dummy embeddings
                embeddings = [self._generate_dummy_embedding(text) for text in cleaned_texts]
            
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            # Return dummy embeddings instead of failing
            return [self._generate_dummy_embedding(text) for text in texts]
    
    def _generate_dummy_embedding(self, text: str) -> List[float]:
        """
        Generate a dummy embedding based on text hash
        This ensures consistent embeddings for the same text
        """
        # Simple hash-based embedding for development/testing
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to numbers and normalize
        hash_nums = [int(text_hash[i:i+2], 16) for i in range(0, min(len(text_hash), 32), 2)]
        
        # Pad or truncate to match embedding dimension
        while len(hash_nums) < self.embedding_dimension:
            hash_nums.extend(hash_nums[:min(len(hash_nums), self.embedding_dimension - len(hash_nums))])
        
        hash_nums = hash_nums[:self.embedding_dimension]
        
        # Normalize to [-1, 1] range
        embedding = [(x - 127.5) / 127.5 for x in hash_nums]
        
        return embedding
    
    async def store_document_embedding(
        self, 
        document_id: str, 
        text_chunk: str, 
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store document embedding in Supabase vector database
        
        Args:
            document_id: ID of the source document
            text_chunk: Original text chunk
            embedding: Vector embedding
            metadata: Additional metadata
            
        Returns:
            ID of the stored embedding record
        """
        try:
            print(f"💾 RAG DEBUG: Storing embedding in Supabase vector_embeddings table")
            print(f"📄 RAG DEBUG: Document ID: {document_id}")
            print(f"📝 RAG DEBUG: Text chunk length: {len(text_chunk)} chars")
            print(f"🔢 RAG DEBUG: Embedding dimension: {len(embedding)}")
            print(f"📊 RAG DEBUG: Metadata: {metadata}")
            
            embedding_data = {
                "document_id": document_id,
                "text_content": text_chunk,
                "embedding": embedding,
                "chunk_index": metadata.get("chunk_index", 0) if metadata else 0,
                "metadata": metadata or {}
            }
            
            print(f"🚀 RAG DEBUG: Inserting embedding data into Supabase...")
            response = self.supabase.table("vector_embeddings").insert(embedding_data).execute()
            
            if not response.data:
                print(f"💥 RAG DEBUG: Supabase insert returned empty data!")
                raise Exception("Supabase insert returned empty response")
            
            embedding_id = response.data[0]["id"]
            print(f"✅ RAG DEBUG: Embedding stored successfully with ID: {embedding_id}")
            logger.info(f"Stored embedding for document {document_id}: {embedding_id}")
            return embedding_id
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Failed to store embedding in Supabase: {str(e)}")
            print(f"🔍 RAG DEBUG: Error details - Document: {document_id}, Text length: {len(text_chunk)}, Embedding dim: {len(embedding)}")
            logger.error(f"Failed to store embedding: {str(e)}")
            raise Exception(f"Failed to store embedding: {str(e)}")
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        chatbot_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in vector database
        
        Args:
            query_embedding: Query vector
            chatbot_id: ID of chatbot to search documents for
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar document chunks with metadata
        """
        try:
            # Use Supabase's vector similarity search if available
            response = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "chatbot_id": chatbot_id,
                    "match_threshold": similarity_threshold,
                    "match_count": limit
                }
            ).execute()
            
            results = response.data
            logger.info(f"Found {len(results)} similar documents for chatbot {chatbot_id}")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            # Fallback to basic query
            return await self._fallback_similarity_search(query_embedding, chatbot_id, limit)
    
    async def hybrid_search(
        self,
        query_text: str,
        chatbot_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.7,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining BM25 keyword search with vector similarity
        
        Args:
            query_text: Original query text
            chatbot_id: ID of chatbot to search documents for
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score for vector search
            bm25_weight: Weight for BM25 scores (0-1)
            vector_weight: Weight for vector similarity scores (0-1)
            
        Returns:
            List of document chunks ranked by hybrid score
        """
        try:
            # Generate embedding for vector search
            query_embedding = await self.generate_embedding(query_text)
            
            # Run both searches in parallel
            import asyncio
            vector_results, keyword_results = await asyncio.gather(
                self._vector_search(query_embedding, chatbot_id, limit * 2, similarity_threshold),
                self._keyword_search(query_text, chatbot_id, limit * 2),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(vector_results, Exception):
                logger.error(f"Vector search failed: {vector_results}")
                vector_results = []
            if isinstance(keyword_results, Exception):
                logger.error(f"Keyword search failed: {keyword_results}")
                keyword_results = []
            
            # Combine and rank results
            hybrid_results = self._combine_search_results(
                vector_results, keyword_results, bm25_weight, vector_weight
            )
            
            # Return top results
            return hybrid_results[:limit]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            # Fallback to vector search only
            query_embedding = await self.generate_embedding(query_text)
            return await self.similarity_search(query_embedding, chatbot_id, limit, similarity_threshold)
    
    async def _vector_search(
        self,
        query_embedding: List[float],
        chatbot_id: str,
        limit: int,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        return await self.similarity_search(query_embedding, chatbot_id, limit, similarity_threshold)
    
    async def _keyword_search(
        self,
        query_text: str,
        chatbot_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Perform keyword search using PostgreSQL full-text search"""
        try:
            # Use PostgreSQL's full-text search capabilities
            search_sql = """
            SELECT 
                ve.id,
                ve.document_id,
                ve.text_content as content,
                ve.metadata,
                ts_rank_cd(to_tsvector('english', ve.text_content), plainto_tsquery('english', %s)) as rank
            FROM vector_embeddings ve
            JOIN documents d ON ve.document_id = d.id
            WHERE d.chatbot_id = %s
            AND to_tsvector('english', ve.text_content) @@ plainto_tsquery('english', %s)
            ORDER BY ts_rank_cd(to_tsvector('english', ve.text_content), plainto_tsquery('english', %s)) DESC
            LIMIT %s;
            """
            
            # Execute the query using Supabase's raw SQL capability
            response = self.supabase.rpc(
                "execute_sql",
                {
                    "sql_query": search_sql,
                    "params": [query_text, chatbot_id, query_text, query_text, limit]
                }
            ).execute()
            
            results = response.data if response.data else []
            logger.info(f"Keyword search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.warning(f"Keyword search failed, using fallback: {str(e)}")
            # Fallback to simple ILIKE search
            return await self._simple_keyword_search(query_text, chatbot_id, limit)
    
    async def _simple_keyword_search(
        self,
        query_text: str,
        chatbot_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Simple keyword search using ILIKE as fallback"""
        try:
            # Split query into keywords
            keywords = query_text.lower().split()
            
            # Build query for documents containing keywords
            query = self.supabase.table("vector_embeddings") \
                .select("id, document_id, text_content, metadata") \
                .eq("documents.chatbot_id", chatbot_id)
            
            # Add keyword filters
            for keyword in keywords:
                query = query.ilike("text_content", f"%{keyword}%")
            
            response = query.limit(limit).execute()
            results = response.data if response.data else []
            
            # Add simple keyword match score
            for result in results:
                content = result.get('text_content', '').lower()
                score = sum(1 for keyword in keywords if keyword in content) / len(keywords)
                result['rank'] = score
            
            return results
            
        except Exception as e:
            logger.error(f"Simple keyword search failed: {str(e)}")
            return []
    
    def _combine_search_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        bm25_weight: float,
        vector_weight: float
    ) -> List[Dict[str, Any]]:
        """Combine and rank results from vector and keyword searches"""
        
        # Normalize scores and create combined results
        combined_results = {}
        
        # Process vector results
        valid_vector_scores = [r.get('similarity', 0) for r in vector_results if r.get('similarity') is not None]
        max_vector_score = max(valid_vector_scores, default=1.0)
        for result in vector_results:
            doc_id = result['id']
            similarity = result.get('similarity', 0)
            if similarity is None:
                similarity = 0.0
            normalized_vector_score = similarity / max_vector_score
            combined_results[doc_id] = {
                **result,
                'vector_score': normalized_vector_score,
                'keyword_score': 0.0,
                'hybrid_score': normalized_vector_score * vector_weight
            }
        
        # Process keyword results
        valid_keyword_scores = [r.get('rank', 0) for r in keyword_results if r.get('rank') is not None]
        max_keyword_score = max(valid_keyword_scores, default=1.0)
        for result in keyword_results:
            doc_id = result['id']
            rank = result.get('rank', 0)
            if rank is None:
                rank = 0.0
            normalized_keyword_score = rank / max_keyword_score
            
            if doc_id in combined_results:
                # Update existing result
                combined_results[doc_id]['keyword_score'] = normalized_keyword_score
                combined_results[doc_id]['hybrid_score'] = (
                    combined_results[doc_id]['vector_score'] * vector_weight +
                    normalized_keyword_score * bm25_weight
                )
            else:
                # Add new result (keyword-only)
                combined_results[doc_id] = {
                    **result,
                    'vector_score': 0.0,
                    'keyword_score': normalized_keyword_score,
                    'hybrid_score': normalized_keyword_score * bm25_weight,
                    'similarity': 0.0  # Add missing similarity field
                }
        
        # Sort by hybrid score and return
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )
        
        logger.info(f"Hybrid search combined {len(vector_results)} vector + {len(keyword_results)} keyword results")
        return sorted_results
    
    async def _fallback_similarity_search(
        self, 
        query_embedding: List[float], 
        chatbot_id: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback similarity search when RPC function is not available
        """
        try:
            # Get all embeddings for the chatbot's documents
            response = self.supabase.table("vector_embeddings") \
                .select("*, documents!inner(chatbot_id)") \
                .eq("documents.chatbot_id", chatbot_id) \
                .execute()
            
            embeddings = response.data
            
            # Calculate cosine similarities
            results = []
            for emb in embeddings:
                try:
                    stored_embedding = emb["embedding"]
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    
                    results.append({
                        "id": emb["id"],
                        "content": emb["text_content"],  # Fixed field name
                        "metadata": emb["metadata"],
                        "similarity": similarity,
                        "document_id": emb["document_id"]
                    })
                except Exception:
                    continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Fallback similarity search failed: {str(e)}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception:
            return 0.0
    
    def _prepare_text(self, text: str) -> str:
        """
        Clean and prepare text for embedding generation
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.strip()
        text = " ".join(text.split())  # Normalize whitespace
        
        # Get max sequence length for current model
        max_length = 256  # Default
        if self.current_model_name in self.AVAILABLE_MODELS:
            max_length = self.AVAILABLE_MODELS[self.current_model_name]["max_seq_length"]
        
        # Truncate if too long (approximate token counting)
        max_chars = max_length * 4  # Rough approximation
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} characters")
        
        return text
    
    async def delete_document_embeddings(self, document_id: str) -> bool:
        """
        Delete all embeddings for a document
        
        Args:
            document_id: ID of document to delete embeddings for
            
        Returns:
            True if successful
        """
        try:
            response = self.supabase.table("vector_embeddings") \
                .delete() \
                .eq("document_id", document_id) \
                .execute()
            
            logger.info(f"Deleted embeddings for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document embeddings: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "model_name": self.current_model_name,
            "embedding_dimension": self.embedding_dimension,
            "available_models": self.AVAILABLE_MODELS,
            "device": getattr(self.model, 'device', 'cpu') if self.model else 'cpu'
        }
    
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different embedding model
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            True if successful
        """
        return self._load_model(model_name)


# Global instance
embedding_service = EmbeddingService()