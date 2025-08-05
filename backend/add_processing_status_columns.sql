-- Add processing status columns to documents table for enhanced RAG implementation
-- This enables real-time progress tracking and error recovery

-- Add processing status column
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'pending' 
CHECK (processing_status IN ('pending', 'uploading', 'extracting', 'embedding', 'completed', 'failed'));

-- Add progress tracking columns
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS processing_progress INTEGER DEFAULT 0;

ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS total_chunks INTEGER DEFAULT 0;

ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS processed_chunks INTEGER DEFAULT 0;

-- Add error tracking column
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_chatbot_processing ON documents(chatbot_id, processing_status);

-- Update existing documents to have proper status
UPDATE documents 
SET processing_status = CASE 
    WHEN processed = true THEN 'completed'
    WHEN extracted_text IS NOT NULL THEN 'extracting'
    ELSE 'pending'
END
WHERE processing_status IS NULL; 