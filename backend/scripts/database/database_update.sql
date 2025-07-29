-- Update database schema to fix embedding issues
-- Run this SQL in your Supabase database

-- 1. Update vector_embeddings table dimension for HuggingFace embeddings
-- First, check if we need to modify the embedding column
DO $$
BEGIN
    -- Update the embedding column to 384 dimensions for HuggingFace models
    ALTER TABLE vector_embeddings ALTER COLUMN embedding TYPE VECTOR(384);
    
    -- Add chunk_index column if it doesn't exist (for document chunking)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'vector_embeddings' AND column_name = 'chunk_index'
    ) THEN
        ALTER TABLE vector_embeddings ADD COLUMN chunk_index INTEGER DEFAULT 0;
    END IF;
    
    RAISE NOTICE 'Updated vector_embeddings table for HuggingFace embeddings (384D)';
END
$$;

-- 2. Update the match_documents function for new dimension
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
        ve.text_content as content,  -- Map text_content to content for compatibility
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

-- 3. Update the vector index for better performance
DROP INDEX IF EXISTS vector_embeddings_embedding_idx;
CREATE INDEX vector_embeddings_embedding_idx 
ON vector_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Add metadata to track embedding model used
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'vector_embeddings' AND column_name = 'model_name'
    ) THEN
        ALTER TABLE vector_embeddings ADD COLUMN model_name VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2';
    END IF;
END
$$;

-- 5. Add helper function to get embedding dimension
CREATE OR REPLACE FUNCTION get_embedding_dimension()
RETURNS integer
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN 384;  -- HuggingFace default model dimension
END;
$$;

COMMENT ON FUNCTION match_documents IS 'Updated for HuggingFace embeddings (384D) with text_content->content mapping';
COMMENT ON FUNCTION get_embedding_dimension IS 'Returns the current embedding dimension (384 for HuggingFace models)';