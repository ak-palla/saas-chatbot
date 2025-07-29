-- Vector Database Setup for Phase 2
-- This file contains SQL commands to set up vector search capabilities

-- Enable necessary extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create function for document similarity search
-- Note: Updated for HuggingFace embeddings (384D) instead of OpenAI (1536D)
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
        ve.content,
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

-- Create index for better vector search performance
CREATE INDEX IF NOT EXISTS vector_embeddings_embedding_idx 
ON vector_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for document lookups
CREATE INDEX IF NOT EXISTS vector_embeddings_document_id_idx 
ON vector_embeddings (document_id);

-- Create index for chatbot document lookups
CREATE INDEX IF NOT EXISTS documents_chatbot_id_idx 
ON documents (chatbot_id);

-- Create function to delete document embeddings
CREATE OR REPLACE FUNCTION delete_document_embeddings(doc_id uuid)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM vector_embeddings WHERE document_id = doc_id;
END;
$$;

-- Create function to get chatbot knowledge stats
CREATE OR REPLACE FUNCTION get_chatbot_knowledge_stats(bot_id uuid)
RETURNS TABLE (
    document_count bigint,
    embedding_count bigint,
    avg_embeddings_per_document numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT d.id) as document_count,
        COUNT(ve.id) as embedding_count,
        CASE 
            WHEN COUNT(DISTINCT d.id) > 0 
            THEN ROUND(COUNT(ve.id)::numeric / COUNT(DISTINCT d.id)::numeric, 2)
            ELSE 0
        END as avg_embeddings_per_document
    FROM documents d
    LEFT JOIN vector_embeddings ve ON d.id = ve.document_id
    WHERE d.chatbot_id = bot_id;
END;
$$;

-- Add any missing columns to existing tables (safe to run multiple times)
DO $$
BEGIN
    -- Add processed column to documents if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'documents' AND column_name = 'processed'
    ) THEN
        ALTER TABLE documents ADD COLUMN processed BOOLEAN DEFAULT false;
    END IF;
    
    -- Add content_hash column to documents if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'documents' AND column_name = 'content_hash'
    ) THEN
        ALTER TABLE documents ADD COLUMN content_hash VARCHAR(255);
    END IF;
END
$$;

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT USAGE ON SCHEMA public TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

COMMENT ON FUNCTION match_documents IS 'Performs vector similarity search for documents belonging to a specific chatbot';
COMMENT ON FUNCTION delete_document_embeddings IS 'Deletes all embeddings for a specific document';
COMMENT ON FUNCTION get_chatbot_knowledge_stats IS 'Returns statistics about a chatbots knowledge base';