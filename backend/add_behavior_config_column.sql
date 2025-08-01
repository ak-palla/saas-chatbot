-- Add behavior_config column to chatbots table for voice chat and other behavioral settings
-- This allows storing voice settings, typing indicators, etc.

ALTER TABLE chatbots 
ADD COLUMN IF NOT EXISTS behavior_config JSONB DEFAULT '{}';

-- Add model column if it doesn't exist (should already exist but ensuring)
ALTER TABLE chatbots 
ADD COLUMN IF NOT EXISTS model VARCHAR(100) DEFAULT 'llama-3.1-8b-instant';

-- Update existing chatbots to have default behavior config with voice disabled
UPDATE chatbots 
SET behavior_config = '{
  "enableVoice": false,
  "enableTypingIndicator": true,
  "enableEmoji": true,
  "maxTokens": 1000,
  "temperature": 0.7
}'::jsonb
WHERE behavior_config IS NULL OR behavior_config = '{}'::jsonb;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chatbots_behavior_config ON chatbots USING gin(behavior_config);
CREATE INDEX IF NOT EXISTS idx_chatbots_model ON chatbots(model);