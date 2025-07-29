"""
Embedding Service with Hugging Face Models
Handles text embeddings generation using local/remote HF models
"""

import logging
import os
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from huggingface_hub import login

from app.core.config import settings
from app.core.database import get_supabase

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for handling text embeddings using Hugging Face models"""
    
    # Available embedding models (ordered by preference)
    AVAILABLE_MODELS = {
        "all-MiniLM-L6-v2": {
            "dimension": 384,
            "max_seq_length": 256,
            "description": "Fast, lightweight model good for most tasks"
        },
        "all-mpnet-base-v2": {
            "dimension": 768,
            "max_seq_length": 384,
            "description": "High quality model with good performance"
        },
        "sentence-transformers/all-MiniLM-L12-v2": {
            "dimension": 384,
            "max_seq_length": 256,
            "description": "Slightly larger than L6, better quality"
        }
    }
    
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
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
        
        # Initialize default model
        self._load_model(self.DEFAULT_MODEL)
    
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
            # Clean and prepare text
            text = self._prepare_text(text)
            
            # Switch model if requested
            if model_name and model_name != self.current_model_name:
                self._load_model(model_name)
            
            # Generate embedding
            if self.model is not None:
                # Use actual model
                embedding = self.model.encode([text], show_progress_bar=False)[0]
                embedding = embedding.tolist()  # Convert numpy array to list
            else:
                # Use dummy embedding
                embedding = self._generate_dummy_embedding(text)
            
            logger.info(f"Generated {self.embedding_dimension}D embedding for text (length: {len(text)} chars)")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            # Return dummy embedding instead of failing
            return self._generate_dummy_embedding(text)
    
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
            embedding_data = {
                "document_id": document_id,
                "text_content": text_chunk,
                "embedding": embedding,
                "chunk_index": metadata.get("chunk_index", 0) if metadata else 0,
                "metadata": metadata or {}
            }
            
            response = self.supabase.table("vector_embeddings").insert(embedding_data).execute()
            
            embedding_id = response.data[0]["id"]
            logger.info(f"Stored embedding for document {document_id}: {embedding_id}")
            return embedding_id
            
        except Exception as e:
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
                        "content": emb["content"],
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