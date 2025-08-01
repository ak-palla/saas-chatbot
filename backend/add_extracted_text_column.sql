-- Add extracted_text column to documents table for storing text content before processing
-- This allows us to defer embedding generation until settings are saved

ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS extracted_text TEXT;

-- Add index for better performance on processed column queries
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(processed);
CREATE INDEX IF NOT EXISTS idx_documents_chatbot_processed ON documents(chatbot_id, processed);

-- Update existing documents to mark them as needing processing if they don't have extracted_text
UPDATE documents 
SET processed = false 
WHERE extracted_text IS NULL AND processed = true;