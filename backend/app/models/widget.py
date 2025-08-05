from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Enums for widget configuration
class WidgetTheme(str, Enum):
    light = "light"
    dark = "dark"
    auto = "auto"

class WidgetPosition(str, Enum):
    bottom_right = "bottom-right"
    bottom_left = "bottom-left"
    top_right = "top-right"
    top_left = "top-left"

class DeploymentStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    archived = "archived"

class DeploymentMethod(str, Enum):
    script_tag = "script_tag"
    npm = "npm"
    manual = "manual"
    wordpress = "wordpress"
    shopify = "shopify"

class InteractionType(str, Enum):
    open = "open"
    close = "close"
    message_sent = "message_sent"
    message_received = "message_received"
    voice_start = "voice_start"
    voice_end = "voice_end"
    file_upload = "file_upload"
    quick_action = "quick_action"

# Widget Template Models
class WidgetTemplateBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    preview_image_url: Optional[str] = None
    css_template: str
    config_template: Dict[str, Any] = Field(default_factory=dict)
    is_premium: bool = False
    is_active: bool = True

class WidgetTemplateCreate(WidgetTemplateBase):
    created_by: Optional[str] = None

class WidgetTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    preview_image_url: Optional[str] = None
    css_template: Optional[str] = None
    config_template: Optional[Dict[str, Any]] = None
    is_premium: Optional[bool] = None
    is_active: Optional[bool] = None

class WidgetTemplate(WidgetTemplateBase):
    id: str
    created_by: Optional[str] = None
    downloads_count: int = 0
    rating: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Widget Configuration Models
class WidgetConfigurationBase(BaseModel):
    config_name: str = Field(default="Default Configuration", max_length=255)
    template_id: Optional[str] = None
    
    # Appearance Settings
    custom_css: Optional[str] = None
    theme: WidgetTheme = WidgetTheme.light
    position: WidgetPosition = WidgetPosition.bottom_right
    primary_color: str = Field(default="#3b82f6", max_length=7)
    secondary_color: str = Field(default="#1f2937", max_length=7)
    border_radius: int = Field(default=12, ge=0, le=50)
    box_shadow: str = Field(default="0 8px 32px rgba(0,0,0,0.15)", max_length=255)
    
    # Behavior Settings
    auto_open: bool = False
    auto_open_delay: int = Field(default=3000, ge=0, le=60000)
    show_avatar: bool = True
    enable_sound: bool = True
    enable_typing_indicator: bool = True
    enable_file_upload: bool = False
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    
    # Size Settings
    max_width: int = Field(default=400, ge=300, le=800)
    max_height: int = Field(default=600, ge=400, le=1000)
    mobile_full_screen: bool = True
    z_index: int = Field(default=999999, ge=1, le=2147483647)
    
    # Advanced Settings
    custom_branding: Dict[str, Any] = Field(default_factory=dict)
    conversation_starters: List[str] = Field(default_factory=list)
    operating_hours: Dict[str, Any] = Field(default_factory=dict)
    language_settings: Dict[str, Any] = Field(default_factory=dict)
    gdpr_compliance: Dict[str, Any] = Field(default_factory=dict)
    
    # A/B Testing
    is_variant: bool = False
    variant_name: Optional[str] = Field(None, max_length=100)
    variant_traffic_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    
    # Deployment Settings
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_domains: List[str] = Field(default_factory=list)
    deployment_status: DeploymentStatus = DeploymentStatus.draft

    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v

class WidgetConfigurationCreate(WidgetConfigurationBase):
    chatbot_id: str

class WidgetConfigurationUpdate(BaseModel):
    config_name: Optional[str] = Field(None, max_length=255)
    template_id: Optional[str] = None
    custom_css: Optional[str] = None
    theme: Optional[WidgetTheme] = None
    position: Optional[WidgetPosition] = None
    primary_color: Optional[str] = Field(None, max_length=7)
    secondary_color: Optional[str] = Field(None, max_length=7)
    border_radius: Optional[int] = Field(None, ge=0, le=50)
    box_shadow: Optional[str] = Field(None, max_length=255)
    auto_open: Optional[bool] = None
    auto_open_delay: Optional[int] = Field(None, ge=0, le=60000)
    show_avatar: Optional[bool] = None
    enable_sound: Optional[bool] = None
    enable_typing_indicator: Optional[bool] = None
    enable_file_upload: Optional[bool] = None
    max_file_size_mb: Optional[int] = Field(None, ge=1, le=100)
    max_width: Optional[int] = Field(None, ge=300, le=800)
    max_height: Optional[int] = Field(None, ge=400, le=1000)
    mobile_full_screen: Optional[bool] = None
    z_index: Optional[int] = Field(None, ge=1, le=2147483647)
    custom_branding: Optional[Dict[str, Any]] = None
    conversation_starters: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    language_settings: Optional[Dict[str, Any]] = None
    gdpr_compliance: Optional[Dict[str, Any]] = None
    is_variant: Optional[bool] = None
    variant_name: Optional[str] = Field(None, max_length=100)
    variant_traffic_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    deployment_status: Optional[DeploymentStatus] = None

class WidgetConfiguration(WidgetConfigurationBase):
    id: str
    chatbot_id: str
    config_version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Widget Deployment Models
class WidgetDeploymentBase(BaseModel):
    domain: str = Field(..., max_length=255)
    page_url: Optional[str] = None
    deployment_method: DeploymentMethod
    embed_code_version: str = Field(default="1.0.0", max_length=20)
    status: str = Field(default="pending")
    deployment_metadata: Dict[str, Any] = Field(default_factory=dict)

class WidgetDeploymentCreate(WidgetDeploymentBase):
    widget_config_id: str
    chatbot_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

class WidgetDeploymentUpdate(BaseModel):
    status: Optional[str] = None
    last_error: Optional[str] = None
    deployment_metadata: Optional[Dict[str, Any]] = None

class WidgetDeployment(WidgetDeploymentBase):
    id: str
    widget_config_id: str
    chatbot_id: str
    last_verified_at: Optional[datetime] = None
    last_error: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Widget Analytics Models
class WidgetAnalyticsBase(BaseModel):
    session_id: str = Field(..., max_length=255)
    user_fingerprint: Optional[str] = Field(None, max_length=255)
    
    # Performance Metrics
    load_time_ms: Optional[int] = None
    first_paint_ms: Optional[int] = None
    time_to_interactive_ms: Optional[int] = None
    bundle_size_kb: Optional[int] = None
    
    # Engagement Metrics
    widget_opened: bool = False
    messages_sent: int = 0
    messages_received: int = 0
    session_duration_seconds: int = 0
    bounce_rate: bool = True
    
    # Technical Information
    domain: Optional[str] = Field(None, max_length=255)
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    user_agent: Optional[str] = None
    browser_name: Optional[str] = Field(None, max_length=100)
    browser_version: Optional[str] = Field(None, max_length=50)
    device_type: Optional[str] = Field(None, max_length=50)
    screen_resolution: Optional[str] = Field(None, max_length=20)
    
    # Geographic Information
    country_code: Optional[str] = Field(None, max_length=2)
    region: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)

class WidgetAnalyticsCreate(WidgetAnalyticsBase):
    widget_config_id: str
    chatbot_id: str
    deployment_id: Optional[str] = None

class WidgetAnalyticsUpdate(BaseModel):
    widget_opened: Optional[bool] = None
    messages_sent: Optional[int] = None
    messages_received: Optional[int] = None
    session_duration_seconds: Optional[int] = None
    bounce_rate: Optional[bool] = None
    first_interaction_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None
    session_ended_at: Optional[datetime] = None

class WidgetAnalytics(WidgetAnalyticsBase):
    id: str
    widget_config_id: str
    chatbot_id: str
    deployment_id: Optional[str] = None
    widget_loaded_at: datetime
    first_interaction_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None
    session_ended_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Widget Interaction Models
class WidgetInteractionBase(BaseModel):
    interaction_type: InteractionType
    interaction_data: Dict[str, Any] = Field(default_factory=dict)
    message_id: Optional[str] = None
    message_content: Optional[str] = None
    message_type: Optional[str] = Field(None, max_length=20)
    response_time_ms: Optional[int] = None
    rag_enabled: bool = False
    rag_context_count: int = 0
    page_url: Optional[str] = None
    user_scroll_position: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None

class WidgetInteractionCreate(WidgetInteractionBase):
    analytics_session_id: str
    widget_config_id: str
    chatbot_id: str

class WidgetInteraction(WidgetInteractionBase):
    id: str
    analytics_session_id: str
    widget_config_id: str
    chatbot_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Widget Session Models
class WidgetSessionBase(BaseModel):
    session_id: str = Field(..., max_length=255)
    total_interactions: int = 0
    total_messages: int = 0
    session_duration_seconds: int = 0
    pages_visited: int = 1
    
    # Conversion Tracking
    goal_completed: bool = False
    goal_type: Optional[str] = Field(None, max_length=100)
    goal_value: Optional[float] = None
    
    # Session Quality Metrics
    engagement_score: float = Field(default=0.0, ge=0.0, le=100.0)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    issue_resolved: Optional[bool] = None
    
    # Session Metadata
    entry_page: Optional[str] = None
    exit_page: Optional[str] = None
    traffic_source: Optional[str] = Field(None, max_length=100)
    campaign_data: Dict[str, Any] = Field(default_factory=dict)

class WidgetSessionCreate(WidgetSessionBase):
    widget_config_id: str
    chatbot_id: str
    analytics_id: str

class WidgetSessionUpdate(BaseModel):
    total_interactions: Optional[int] = None
    total_messages: Optional[int] = None
    session_duration_seconds: Optional[int] = None
    pages_visited: Optional[int] = None
    goal_completed: Optional[bool] = None
    goal_type: Optional[str] = Field(None, max_length=100)
    goal_value: Optional[float] = None
    engagement_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    issue_resolved: Optional[bool] = None
    exit_page: Optional[str] = None
    session_end_at: Optional[datetime] = None

class WidgetSession(WidgetSessionBase):
    id: str
    widget_config_id: str
    chatbot_id: str
    analytics_id: str
    session_start_at: datetime
    session_end_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Response Models
class WidgetAnalyticsSummary(BaseModel):
    total_sessions: int
    total_interactions: int
    average_session_duration: float
    bounce_rate: float
    conversion_rate: float
    top_pages: List[Dict[str, Any]]
    top_countries: List[Dict[str, Any]]
    device_breakdown: Dict[str, int]
    browser_breakdown: Dict[str, int]

class WidgetPerformanceMetrics(BaseModel):
    average_load_time: float
    average_first_paint: float
    average_time_to_interactive: float
    error_rate: float
    uptime_percentage: float

class WidgetEngagementMetrics(BaseModel):
    total_widget_opens: int
    total_messages: int
    average_messages_per_session: float
    user_satisfaction: float
    goal_completion_rate: float

# A/B Test Models
class WidgetABTestResult(BaseModel):
    id: str
    widget_config_id: str
    chatbot_id: str
    test_name: str = Field(..., max_length=255)
    variant_name: str = Field(..., max_length=100)
    impressions: int = 0
    interactions: int = 0
    conversions: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    confidence_level: float = 0.0
    statistical_significance: bool = False
    test_start_date: datetime
    test_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Comprehensive Widget Analytics Response
class WidgetAnalyticsReport(BaseModel):
    summary: WidgetAnalyticsSummary
    performance: WidgetPerformanceMetrics
    engagement: WidgetEngagementMetrics
    time_series_data: List[Dict[str, Any]]  # For charts
    recent_interactions: List[WidgetInteraction]
    ab_test_results: List[WidgetABTestResult]