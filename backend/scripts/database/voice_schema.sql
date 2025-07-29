-- Voice chat functionality database schema updates
-- Add voice-related tables for Phase 3 implementation

-- Voice sessions table
CREATE TABLE IF NOT EXISTS voice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Session metadata
    total_audio_duration_input FLOAT DEFAULT 0,
    total_audio_duration_output FLOAT DEFAULT 0, 
    total_words_transcribed INTEGER DEFAULT 0,
    total_words_synthesized INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    
    -- Performance metrics
    average_stt_time FLOAT DEFAULT 0,
    average_llm_time FLOAT DEFAULT 0,
    average_tts_time FLOAT DEFAULT 0,
    
    -- Session configuration
    voice_config JSONB DEFAULT '{}'::jsonb
);

-- Voice configurations table
CREATE TABLE IF NOT EXISTS voice_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- TTS settings
    tts_voice VARCHAR(100) DEFAULT 'aura-asteria-en',
    tts_speed FLOAT DEFAULT 1.0 CHECK (tts_speed >= 0.5 AND tts_speed <= 2.0),
    tts_pitch FLOAT DEFAULT 0.0 CHECK (tts_pitch >= -2.0 AND tts_pitch <= 2.0),
    
    -- STT settings  
    stt_language VARCHAR(10) DEFAULT NULL,
    audio_format VARCHAR(20) DEFAULT 'webm',
    
    -- Additional settings
    settings JSONB DEFAULT '{}'::jsonb,
    
    -- Ensure one config per user-chatbot pair
    UNIQUE(user_id, chatbot_id)
);

-- Voice usage tracking table
CREATE TABLE IF NOT EXISTS voice_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Audio metrics
    audio_duration_input FLOAT NOT NULL,
    audio_duration_output FLOAT NOT NULL,
    text_length_transcribed INTEGER NOT NULL,
    text_length_synthesized INTEGER NOT NULL,
    
    -- Voice settings used
    voice_used VARCHAR(100) NOT NULL,
    audio_format_used VARCHAR(20) NOT NULL,
    
    -- Processing times
    stt_processing_time FLOAT,
    llm_processing_time FLOAT,
    tts_processing_time FLOAT,
    total_processing_time FLOAT,
    
    -- Quality metrics
    transcription_confidence FLOAT,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Voice errors tracking table
CREATE TABLE IF NOT EXISTS voice_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    chatbot_id UUID REFERENCES chatbots(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Error details
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    error_stage VARCHAR(50), -- stt, llm, tts, websocket
    
    -- Context
    audio_size INTEGER,
    audio_duration FLOAT,
    text_length INTEGER,
    voice_config JSONB,
    
    -- Additional details
    details JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_voice_sessions_user_id ON voice_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_chatbot_id ON voice_sessions(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_session_id ON voice_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_active ON voice_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_last_activity ON voice_sessions(last_activity_at);

CREATE INDEX IF NOT EXISTS idx_voice_configs_user_chatbot ON voice_configs(user_id, chatbot_id);

CREATE INDEX IF NOT EXISTS idx_voice_usage_user_id ON voice_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_usage_chatbot_id ON voice_usage(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_voice_usage_created_at ON voice_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_usage_session_id ON voice_usage(session_id);

CREATE INDEX IF NOT EXISTS idx_voice_errors_created_at ON voice_errors(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_errors_error_type ON voice_errors(error_type);
CREATE INDEX IF NOT EXISTS idx_voice_errors_user_id ON voice_errors(user_id);

-- Add voice-related columns to existing tables

-- Add voice capabilities to chatbots table
ALTER TABLE chatbots 
ADD COLUMN IF NOT EXISTS voice_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS voice_config JSONB DEFAULT '{}'::jsonb;

-- Add voice message indicators to messages table  
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS is_voice_message BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS voice_metadata JSONB DEFAULT '{}'::jsonb;

-- Add voice session reference to conversations table
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS voice_session_id VARCHAR(255);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to voice tables
CREATE TRIGGER update_voice_sessions_updated_at 
    BEFORE UPDATE ON voice_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_configs_updated_at 
    BEFORE UPDATE ON voice_configs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to update voice session activity
CREATE OR REPLACE FUNCTION update_voice_session_activity(p_session_id VARCHAR(255))
RETURNS VOID AS $$
BEGIN
    UPDATE voice_sessions 
    SET last_activity_at = NOW()
    WHERE session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to get voice session stats
CREATE OR REPLACE FUNCTION get_voice_session_stats(p_user_id UUID)
RETURNS TABLE(
    total_sessions BIGINT,
    active_sessions BIGINT,
    total_audio_minutes NUMERIC,
    total_messages BIGINT,
    avg_session_duration NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_sessions,
        COUNT(CASE WHEN is_active THEN 1 END)::BIGINT as active_sessions,
        ROUND(SUM(total_audio_duration_input + total_audio_duration_output) / 60.0, 2) as total_audio_minutes,
        SUM(message_count)::BIGINT as total_messages,
        ROUND(AVG(EXTRACT(EPOCH FROM (last_activity_at - created_at)) / 60.0), 2) as avg_session_duration
    FROM voice_sessions 
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to cleanup expired voice sessions
CREATE OR REPLACE FUNCTION cleanup_expired_voice_sessions(p_timeout_minutes INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    sessions_cleaned INTEGER;
BEGIN
    UPDATE voice_sessions 
    SET is_active = FALSE 
    WHERE is_active = TRUE 
    AND last_activity_at < NOW() - INTERVAL '1 minute' * p_timeout_minutes;
    
    GET DIAGNOSTICS sessions_cleaned = ROW_COUNT;
    
    RETURN sessions_cleaned;
END;
$$ LANGUAGE plpgsql;

-- Insert default voice configurations for existing chatbots
INSERT INTO voice_configs (user_id, chatbot_id, tts_voice, tts_speed, tts_pitch, stt_language, audio_format)
SELECT 
    user_id, 
    id as chatbot_id,
    'aura-asteria-en' as tts_voice,
    1.0 as tts_speed,
    0.0 as tts_pitch,
    NULL as stt_language,
    'webm' as audio_format
FROM chatbots 
WHERE NOT EXISTS (
    SELECT 1 FROM voice_configs vc 
    WHERE vc.user_id = chatbots.user_id 
    AND vc.chatbot_id = chatbots.id
);

-- Create view for voice analytics
CREATE OR REPLACE VIEW voice_analytics AS
SELECT 
    DATE_TRUNC('day', vu.created_at) as date,
    COUNT(*) as total_voice_messages,
    COUNT(DISTINCT vu.user_id) as unique_users,
    COUNT(DISTINCT vu.chatbot_id) as chatbots_used,
    ROUND(AVG(vu.audio_duration_input), 2) as avg_input_duration,
    ROUND(AVG(vu.audio_duration_output), 2) as avg_output_duration,
    ROUND(AVG(vu.transcription_confidence), 3) as avg_confidence,
    ROUND(AVG(vu.total_processing_time), 3) as avg_processing_time,
    MODE() WITHIN GROUP (ORDER BY vu.voice_used) as most_used_voice
FROM voice_usage vu
GROUP BY DATE_TRUNC('day', vu.created_at)
ORDER BY date DESC;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL ON voice_sessions TO your_app_user;  
-- GRANT ALL ON voice_configs TO your_app_user;
-- GRANT ALL ON voice_usage TO your_app_user;
-- GRANT ALL ON voice_errors TO your_app_user;

COMMENT ON TABLE voice_sessions IS 'Active WebSocket voice chat sessions';
COMMENT ON TABLE voice_configs IS 'Voice processing configurations per user/chatbot';
COMMENT ON TABLE voice_usage IS 'Voice chat usage tracking for analytics and billing';
COMMENT ON TABLE voice_errors IS 'Voice processing error tracking for monitoring';
COMMENT ON VIEW voice_analytics IS 'Daily voice chat analytics and metrics';