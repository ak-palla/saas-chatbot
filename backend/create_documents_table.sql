-- Create documents table for RAG implementation
-- This is the basic schema that needs to exist before adding processing status columns

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('pdf', 'txt', 'docx', 'html', 'markdown')),
    file_size INTEGER NOT NULL,
    google_drive_id VARCHAR(255),
    content_hash VARCHAR(255) NOT NULL,
    extracted_text TEXT,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector embeddings table
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    text_content TEXT NOT NULL,
    embedding VECTOR(384), -- Sentence Transformer embedding dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_chatbot_id ON documents(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_document_id ON vector_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(processed);

-- Vector similarity search index
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_embedding ON vector_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if exists (PostgreSQL doesn't support IF NOT EXISTS for triggers)
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();