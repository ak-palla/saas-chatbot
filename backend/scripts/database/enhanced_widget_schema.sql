-- Enhanced Widget Management Schema Extensions
-- This file extends the existing database schema with widget-specific tables

-- Widget Templates table - Pre-built styling templates
CREATE TABLE widget_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- 'corporate', 'startup', 'ecommerce', 'healthcare', etc.
    preview_image_url TEXT,
    css_template TEXT NOT NULL,
    config_template JSONB DEFAULT '{}',
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_by UUID, -- Optional: for user-created templates
    downloads_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widget Configurations table - Store widget-specific settings separate from chatbot config
CREATE TABLE widget_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    template_id UUID REFERENCES widget_templates(id) ON DELETE SET NULL,
    config_name VARCHAR(255) DEFAULT 'Default Configuration',
    config_version INTEGER DEFAULT 1,
    
    -- Widget Appearance Settings
    custom_css TEXT,
    theme VARCHAR(20) DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'auto')),
    position VARCHAR(20) DEFAULT 'bottom-right' CHECK (position IN ('bottom-right', 'bottom-left', 'top-right', 'top-left')),
    primary_color VARCHAR(7) DEFAULT '#3b82f6',
    secondary_color VARCHAR(7) DEFAULT '#1f2937',
    border_radius INTEGER DEFAULT 12,
    box_shadow VARCHAR(255) DEFAULT '0 8px 32px rgba(0,0,0,0.15)',
    
    -- Widget Behavior Settings
    auto_open BOOLEAN DEFAULT false,
    auto_open_delay INTEGER DEFAULT 3000, -- milliseconds
    show_avatar BOOLEAN DEFAULT true,
    enable_sound BOOLEAN DEFAULT true,
    enable_typing_indicator BOOLEAN DEFAULT true,
    enable_file_upload BOOLEAN DEFAULT false,
    max_file_size_mb INTEGER DEFAULT 10,
    
    -- Widget Size Settings
    max_width INTEGER DEFAULT 400,
    max_height INTEGER DEFAULT 600,
    mobile_full_screen BOOLEAN DEFAULT true,
    z_index INTEGER DEFAULT 999999,
    
    -- Advanced Settings
    custom_branding JSONB DEFAULT '{}', -- Logo, company name, etc.
    conversation_starters JSONB DEFAULT '[]', -- Pre-defined quick actions
    operating_hours JSONB DEFAULT '{}', -- When widget is active
    language_settings JSONB DEFAULT '{}', -- Multi-language support
    gdpr_compliance JSONB DEFAULT '{}', -- Privacy settings
    
    -- A/B Testing
    is_variant BOOLEAN DEFAULT false,
    variant_name VARCHAR(100),
    variant_traffic_percentage DECIMAL(5,2) DEFAULT 100.0,
    
    -- Deployment Settings
    allowed_domains JSONB DEFAULT '[]', -- Domain restrictions
    blocked_domains JSONB DEFAULT '[]',
    deployment_status VARCHAR(20) DEFAULT 'draft' CHECK (deployment_status IN ('draft', 'active', 'paused', 'archived')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widget Deployments table - Track where widgets are deployed
CREATE TABLE widget_deployments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_config_id UUID NOT NULL REFERENCES widget_configurations(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    
    -- Deployment Information
    domain VARCHAR(255) NOT NULL,
    page_url TEXT,
    deployment_method VARCHAR(50) NOT NULL, -- 'script_tag', 'npm', 'manual', 'wordpress', 'shopify'
    embed_code_version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Status Tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'inactive', 'error')),
    last_verified_at TIMESTAMPTZ,
    last_error TEXT,
    
    -- Deployment Metadata
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    deployment_metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widget Analytics table - Track widget performance metrics
CREATE TABLE widget_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_config_id UUID NOT NULL REFERENCES widget_configurations(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    deployment_id UUID REFERENCES widget_deployments(id) ON DELETE SET NULL,
    
    -- Session Information
    session_id VARCHAR(255) NOT NULL,
    user_fingerprint VARCHAR(255), -- Anonymous user identification
    
    -- Performance Metrics
    load_time_ms INTEGER,
    first_paint_ms INTEGER,
    time_to_interactive_ms INTEGER,
    bundle_size_kb INTEGER,
    
    -- Engagement Metrics
    widget_opened BOOLEAN DEFAULT false,
    messages_sent INTEGER DEFAULT 0,
    messages_received INTEGER DEFAULT 0,
    session_duration_seconds INTEGER DEFAULT 0,
    bounce_rate BOOLEAN DEFAULT true, -- true if no interaction
    
    -- Technical Information
    domain VARCHAR(255),
    page_url TEXT,
    page_title TEXT,
    user_agent TEXT,
    browser_name VARCHAR(100),
    browser_version VARCHAR(50),
    device_type VARCHAR(50), -- 'desktop', 'mobile', 'tablet'
    screen_resolution VARCHAR(20),
    
    -- Geographic Information
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    timezone VARCHAR(50),
    
    -- Timestamps
    widget_loaded_at TIMESTAMPTZ DEFAULT NOW(),
    first_interaction_at TIMESTAMPTZ,
    last_interaction_at TIMESTAMPTZ,
    session_ended_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widget Interactions table - Log detailed user interactions
CREATE TABLE widget_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analytics_session_id UUID NOT NULL REFERENCES widget_analytics(id) ON DELETE CASCADE,
    widget_config_id UUID NOT NULL REFERENCES widget_configurations(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    
    -- Interaction Details
    interaction_type VARCHAR(50) NOT NULL, -- 'open', 'close', 'message_sent', 'message_received', 'voice_start', 'voice_end', 'file_upload', 'quick_action'
    interaction_data JSONB DEFAULT '{}', -- Specific data for each interaction type
    
    -- Message Information (if applicable)
    message_id UUID,
    message_content TEXT,
    message_type VARCHAR(20), -- 'text', 'voice', 'file'
    
    -- Performance Tracking
    response_time_ms INTEGER, -- Time to get response from backend
    rag_enabled BOOLEAN DEFAULT false,
    rag_context_count INTEGER DEFAULT 0,
    
    -- User Context
    page_url TEXT,
    user_scroll_position INTEGER,
    viewport_width INTEGER,
    viewport_height INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widget Sessions table - Aggregate session data for reporting
CREATE TABLE widget_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_config_id UUID NOT NULL REFERENCES widget_configurations(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    analytics_id UUID NOT NULL REFERENCES widget_analytics(id) ON DELETE CASCADE,
    
    -- Session Summary
    session_id VARCHAR(255) NOT NULL,
    total_interactions INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    session_duration_seconds INTEGER DEFAULT 0,
    pages_visited INTEGER DEFAULT 1,
    
    -- Conversion Tracking
    goal_completed BOOLEAN DEFAULT false,
    goal_type VARCHAR(100), -- 'contact_form', 'purchase', 'signup', 'custom'
    goal_value DECIMAL(10,2),
    
    -- Session Quality Metrics
    engagement_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100 based on interactions
    satisfaction_rating INTEGER, -- 1-5 if user provides feedback
    issue_resolved BOOLEAN,
    
    -- Session Metadata
    entry_page TEXT,
    exit_page TEXT,
    traffic_source VARCHAR(100), -- 'direct', 'search', 'social', 'referral'
    campaign_data JSONB DEFAULT '{}',
    
    session_start_at TIMESTAMPTZ DEFAULT NOW(),
    session_end_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widget A/B Test Results table - Track A/B testing performance
CREATE TABLE widget_ab_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_config_id UUID NOT NULL REFERENCES widget_configurations(id) ON DELETE CASCADE,
    chatbot_id UUID NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    
    -- Test Information
    test_name VARCHAR(255) NOT NULL,
    variant_name VARCHAR(100) NOT NULL,
    
    -- Performance Metrics
    impressions INTEGER DEFAULT 0,
    interactions INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    bounce_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_session_duration DECIMAL(10,2) DEFAULT 0.0,
    
    -- Statistical Data
    confidence_level DECIMAL(5,2) DEFAULT 0.0,
    statistical_significance BOOLEAN DEFAULT false,
    
    -- Test Period
    test_start_date TIMESTAMPTZ DEFAULT NOW(),
    test_end_date TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX idx_widget_configurations_chatbot_id ON widget_configurations(chatbot_id);
CREATE INDEX idx_widget_configurations_template_id ON widget_configurations(template_id);
CREATE INDEX idx_widget_configurations_status ON widget_configurations(deployment_status);

CREATE INDEX idx_widget_templates_category ON widget_templates(category);
CREATE INDEX idx_widget_templates_active ON widget_templates(is_active);

CREATE INDEX idx_widget_deployments_chatbot_id ON widget_deployments(chatbot_id);
CREATE INDEX idx_widget_deployments_domain ON widget_deployments(domain);
CREATE INDEX idx_widget_deployments_status ON widget_deployments(status);

CREATE INDEX idx_widget_analytics_chatbot_id ON widget_analytics(chatbot_id);
CREATE INDEX idx_widget_analytics_session_id ON widget_analytics(session_id);
CREATE INDEX idx_widget_analytics_domain ON widget_analytics(domain);
CREATE INDEX idx_widget_analytics_created_at ON widget_analytics(created_at);

CREATE INDEX idx_widget_interactions_analytics_session ON widget_interactions(analytics_session_id);
CREATE INDEX idx_widget_interactions_type ON widget_interactions(interaction_type);
CREATE INDEX idx_widget_interactions_created_at ON widget_interactions(created_at);

CREATE INDEX idx_widget_sessions_chatbot_id ON widget_sessions(chatbot_id);
CREATE INDEX idx_widget_sessions_session_id ON widget_sessions(session_id);
CREATE INDEX idx_widget_sessions_created_at ON widget_sessions(created_at);

CREATE INDEX idx_widget_ab_results_config_id ON widget_ab_test_results(widget_config_id);
CREATE INDEX idx_widget_ab_results_test_name ON widget_ab_test_results(test_name);

-- Update timestamp triggers
CREATE TRIGGER update_widget_templates_updated_at 
    BEFORE UPDATE ON widget_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_widget_configurations_updated_at 
    BEFORE UPDATE ON widget_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_widget_deployments_updated_at 
    BEFORE UPDATE ON widget_deployments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_widget_ab_results_updated_at 
    BEFORE UPDATE ON widget_ab_test_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default widget templates
INSERT INTO widget_templates (name, description, category, css_template, config_template) VALUES
('Corporate Professional', 'Clean, professional design suitable for business websites', 'corporate', 
 '.chatbot-widget-container { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; } .chatbot-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }', 
 '{"primaryColor": "#667eea", "secondaryColor": "#764ba2", "borderRadius": 8}'),

('Startup Modern', 'Bold, modern design perfect for startups and tech companies', 'startup',
 '.chatbot-widget-container { font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif; } .chatbot-header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }',
 '{"primaryColor": "#f5576c", "secondaryColor": "#f093fb", "borderRadius": 16}'),

('E-commerce Friendly', 'Conversion-focused design for online stores', 'ecommerce',
 '.chatbot-widget-container { font-family: "Roboto", Arial, sans-serif; } .chatbot-header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }',
 '{"primaryColor": "#4facfe", "secondaryColor": "#00f2fe", "borderRadius": 12}'),

('Healthcare Trust', 'Trustworthy, calming design for healthcare providers', 'healthcare',
 '.chatbot-widget-container { font-family: "Source Sans Pro", Arial, sans-serif; } .chatbot-header { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }',
 '{"primaryColor": "#a8edea", "secondaryColor": "#fed6e3", "borderRadius": 20}'),

('Minimalist Clean', 'Ultra-clean, minimalist design', 'minimal',
 '.chatbot-widget-container { font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif; } .chatbot-header { background: #ffffff; color: #333333; border-bottom: 1px solid #e5e7eb; }',
 '{"primaryColor": "#ffffff", "secondaryColor": "#333333", "borderRadius": 4}');

-- Insert default widget configuration for existing chatbots
INSERT INTO widget_configurations (chatbot_id, config_name)
SELECT id, 'Default Configuration'
FROM chatbots
WHERE id NOT IN (SELECT DISTINCT chatbot_id FROM widget_configurations WHERE chatbot_id IS NOT NULL);