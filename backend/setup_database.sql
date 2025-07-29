-- Chatbot SaaS Platform Database Schema
-- Execute this script in your Supabase SQL Editor

-- Enable necessary extensions (with error handling)
DO $$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    RAISE NOTICE 'Extension uuid-ossp enabled';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'uuid-ossp extension already exists or could not be created: %', SQLERRM;
END $$;

DO $$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS vector;
    RAISE NOTICE 'Extension vector enabled';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'vector extension already exists or could not be created: %', SQLERRM;
END $$;

-- Drop existing tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS usage_records CASCADE;
DROP TABLE IF EXISTS vector_embeddings CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS chatbots CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chatbots table
CREATE TABLE chatbots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_prompt TEXT,
    appearance_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    title VARCHAR(255),
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('pdf', 'txt', 'docx', 'html', 'markdown')),
    file_size INTEGER NOT NULL,
    google_drive_id VARCHAR(255),
    content_hash VARCHAR(255) NOT NULL,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector embeddings table (for Phase 2)
CREATE TABLE vector_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text_content TEXT NOT NULL,
    embedding VECTOR(1024), -- Groq embedding dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage tracking table
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chatbot_id UUID REFERENCES chatbots(id) ON DELETE SET NULL,
    usage_type VARCHAR(50) NOT NULL CHECK (usage_type IN ('text_chat', 'voice_chat', 'document_upload', 'embedding_generation', 'stt_processing', 'tts_processing')),
    tokens_used INTEGER,
    audio_seconds FLOAT,
    api_endpoint VARCHAR(255) NOT NULL,
    cost DECIMAL(10, 6),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_chatbots_user_id ON chatbots(user_id);
CREATE INDEX idx_conversations_chatbot_id ON conversations(chatbot_id);
CREATE INDEX idx_documents_chatbot_id ON documents(chatbot_id);
CREATE INDEX idx_vector_embeddings_document_id ON vector_embeddings(document_id);
CREATE INDEX idx_usage_records_user_id ON usage_records(user_id);
CREATE INDEX idx_usage_records_created_at ON usage_records(created_at);

-- Vector similarity search index (for Phase 2)
DO $$ 
BEGIN
    CREATE INDEX ON vector_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    RAISE NOTICE 'Vector similarity index created';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Vector index could not be created (vector extension may not be available): %', SQLERRM;
END $$;

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chatbots_updated_at BEFORE UPDATE ON chatbots FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert a test user (optional - for testing)
DO $$
BEGIN
    INSERT INTO users (email, hashed_password, full_name, subscription_tier) 
    VALUES ('admin@example.com', '$2b$12$dummy.hash.for.testing', 'Admin User', 'enterprise')
    ON CONFLICT (email) DO NOTHING;
    RAISE NOTICE 'Test admin user created (if not exists)';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not create test user: %', SQLERRM;
END $$;

-- Final verification
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('users', 'chatbots', 'conversations', 'documents', 'vector_embeddings', 'usage_records');
    
    RAISE NOTICE 'Database setup completed! Created % tables', table_count;
    
    IF table_count = 6 THEN
        RAISE NOTICE '✅ All required tables created successfully!';
    ELSE
        RAISE NOTICE '⚠️ Expected 6 tables but found %. Please check for errors above.', table_count;
    END IF;
END $$;