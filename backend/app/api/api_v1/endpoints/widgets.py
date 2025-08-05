from fastapi import APIRouter, HTTPException, status, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid

from app.models.widget import (
    WidgetConfiguration, WidgetConfigurationCreate, WidgetConfigurationUpdate,
    WidgetTemplate, WidgetTemplateCreate, WidgetTemplateUpdate,
    WidgetDeployment, WidgetDeploymentCreate, WidgetDeploymentUpdate,
    WidgetAnalytics, WidgetAnalyticsCreate, WidgetAnalyticsUpdate,
    WidgetInteraction, WidgetInteractionCreate,
    WidgetSession, WidgetSessionCreate, WidgetSessionUpdate,
    WidgetAnalyticsSummary, WidgetPerformanceMetrics, WidgetEngagementMetrics,
    WidgetAnalyticsReport, WidgetABTestResult
)
from app.services.deployment_service import deployment_service
from app.core.database import get_supabase_admin
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Helper function to get user_id from email
async def get_user_id_from_email(user_email: str):
    """Get user ID from email, create user if not exists"""
    supabase = get_supabase_admin()
    
    user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
    
    if not user_response.data:
        # Create new user
        new_user_id = str(uuid.uuid4())
        new_user_data = {
            "id": new_user_id,
            "email": user_email,
            "hashed_password": "supabase_auth",
            "is_active": True,
            "subscription_tier": "free"
        }
        create_user_response = supabase.table("users").insert(new_user_data).execute()
        return create_user_response.data[0]["id"]
    
    return user_response.data[0]["id"]

# Widget Configuration Endpoints

@router.post("/{chatbot_id}/config", response_model=WidgetConfiguration)
async def create_widget_configuration(
    chatbot_id: str,
    config: WidgetConfigurationCreate,
    user_email: str
):
    """Create a new widget configuration for a chatbot"""
    logger.info(f"🎨 Creating widget configuration for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Create configuration
        config_data = {
            **config.dict(),
            "chatbot_id": chatbot_id
        }
        
        response = supabase.table("widget_configurations").insert(config_data).execute()
        logger.info(f"✅ Widget configuration created: {response.data[0]['id']}")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"💥 Error creating widget configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget configuration: {str(e)}"
        )

@router.get("/{chatbot_id}/config", response_model=List[WidgetConfiguration])
async def get_widget_configurations(
    chatbot_id: str,
    user_email: str,
    active_only: bool = Query(default=True, description="Only return active configurations")
):
    """Get all widget configurations for a chatbot"""
    logger.info(f"📋 Getting widget configurations for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Get configurations
        query = supabase.table("widget_configurations").select("*").eq("chatbot_id", chatbot_id)
        
        if active_only:
            query = query.in_("deployment_status", ["active", "draft"])
        
        response = query.execute()
        logger.info(f"✅ Found {len(response.data)} widget configurations")
        
        return response.data
        
    except Exception as e:
        logger.error(f"💥 Error getting widget configurations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget configurations: {str(e)}"
        )

@router.get("/{chatbot_id}/config/{config_id}", response_model=WidgetConfiguration)  
async def get_widget_configuration(
    chatbot_id: str,
    config_id: str,
    user_email: str
):
    """Get a specific widget configuration"""
    logger.info(f"🔍 Getting widget configuration {config_id} for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Get specific configuration
        response = supabase.table("widget_configurations").select("*").eq("id", config_id).eq("chatbot_id", chatbot_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget configuration not found")
        
        logger.info(f"✅ Found widget configuration: {response.data[0]['config_name']}")
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting widget configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget configuration: {str(e)}"
        )

@router.put("/{chatbot_id}/config/{config_id}", response_model=WidgetConfiguration)
async def update_widget_configuration(
    chatbot_id: str,
    config_id: str,
    config_update: WidgetConfigurationUpdate,
    user_email: str
):
    """Update a widget configuration"""
    logger.info(f"🔄 Updating widget configuration {config_id} for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Check if configuration exists
        existing = supabase.table("widget_configurations").select("*").eq("id", config_id).eq("chatbot_id", chatbot_id).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget configuration not found")
        
        # Update configuration
        update_data = {k: v for k, v in config_update.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            response = supabase.table("widget_configurations").update(update_data).eq("id", config_id).execute()
            logger.info(f"✅ Widget configuration updated successfully")
            return response.data[0]
        else:
            return existing.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error updating widget configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget configuration: {str(e)}"
        )

@router.delete("/{chatbot_id}/config/{config_id}")
async def delete_widget_configuration(
    chatbot_id: str,
    config_id: str,
    user_email: str
):
    """Delete a widget configuration"""
    logger.info(f"🗑️ Deleting widget configuration {config_id} for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Check if configuration exists
        existing = supabase.table("widget_configurations").select("*").eq("id", config_id).eq("chatbot_id", chatbot_id).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget configuration not found")
        
        # Delete configuration
        supabase.table("widget_configurations").delete().eq("id", config_id).execute()
        logger.info(f"✅ Widget configuration deleted successfully")
        
        return {"message": "Widget configuration deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error deleting widget configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete widget configuration: {str(e)}"
        )

# Widget Template Endpoints

@router.get("/templates", response_model=List[WidgetTemplate])
async def get_widget_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_premium: Optional[bool] = Query(None, description="Filter by premium status"),
    limit: int = Query(default=50, le=100, description="Limit number of results")
):
    """Get available widget templates"""
    logger.info(f"📋 Getting widget templates (category: {category}, premium: {is_premium})")
    
    supabase = get_supabase_admin()
    
    try:
        query = supabase.table("widget_templates").select("*").eq("is_active", True)
        
        if category:
            query = query.eq("category", category)
        
        if is_premium is not None:
            query = query.eq("is_premium", is_premium)
        
        query = query.order("downloads_count", desc=True).limit(limit)
        response = query.execute()
        
        logger.info(f"✅ Found {len(response.data)} widget templates")
        return response.data
        
    except Exception as e:
        logger.error(f"💥 Error getting widget templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget templates: {str(e)}"
        )

@router.get("/templates/{template_id}", response_model=WidgetTemplate)
async def get_widget_template(template_id: str):
    """Get a specific widget template"""
    logger.info(f"🔍 Getting widget template {template_id}")
    
    supabase = get_supabase_admin()
    
    try:
        response = supabase.table("widget_templates").select("*").eq("id", template_id).eq("is_active", True).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget template not found")
        
        logger.info(f"✅ Found widget template: {response.data[0]['name']}")
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting widget template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget template: {str(e)}"
        )

@router.post("/templates", response_model=WidgetTemplate)
async def create_widget_template(
    template: WidgetTemplateCreate,
    user_email: str
):
    """Create a new widget template (for admin users or template creators)"""
    logger.info(f"🎨 Creating widget template: {template.name}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        template_data = {
            **template.dict(),
            "created_by": user_id
        }
        
        response = supabase.table("widget_templates").insert(template_data).execute()
        logger.info(f"✅ Widget template created: {response.data[0]['id']}")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"💥 Error creating widget template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget template: {str(e)}"
        )

# Widget Deployment Endpoints

@router.post("/{chatbot_id}/deploy", response_model=WidgetDeployment)
async def create_widget_deployment(
    chatbot_id: str,
    deployment: WidgetDeploymentCreate,
    user_email: str
):
    """Track a new widget deployment"""
    logger.info(f"🚀 Creating widget deployment for chatbot {chatbot_id} on {deployment.domain}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        deployment_data = {
            **deployment.dict(),
            "chatbot_id": chatbot_id
        }
        
        response = supabase.table("widget_deployments").insert(deployment_data).execute()
        logger.info(f"✅ Widget deployment created: {response.data[0]['id']}")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"💥 Error creating widget deployment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget deployment: {str(e)}"
        )

@router.get("/{chatbot_id}/deployments", response_model=List[WidgetDeployment])
async def get_widget_deployments(
    chatbot_id: str,
    user_email: str,
    status_filter: Optional[str] = Query(None, description="Filter by deployment status")
):
    """Get all deployments for a chatbot"""
    logger.info(f"📋 Getting widget deployments for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        query = supabase.table("widget_deployments").select("*").eq("chatbot_id", chatbot_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.order("created_at", desc=True).execute()
        logger.info(f"✅ Found {len(response.data)} widget deployments")
        
        return response.data

    except Exception as e:
        logger.error(f"💥 Error getting widget deployments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget deployments: {str(e)}"
        )

# Widget Health Check and Verification Endpoints

@router.post("/{chatbot_id}/verify-domain")
async def verify_widget_domain(
    chatbot_id: str,
    domain: str,
    user_email: str
):
    """Verify domain for widget deployment"""
    logger.info(f"🔍 Verifying domain {domain} for chatbot {chatbot_id}")

    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)

    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")

        # Perform domain verification
        verification_result = await deployment_service.verify_domain(domain)

        return {
            "domain": verification_result.domain,
            "verified": verification_result.verified,
            "ssl_valid": verification_result.ssl_valid,
            "ssl_expires": verification_result.ssl_expires.isoformat() if verification_result.ssl_expires else None,
            "error_message": verification_result.error_message,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error verifying domain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify domain: {str(e)}"
        )

@router.post("/{chatbot_id}/health-check")
async def perform_widget_health_check(
    chatbot_id: str,
    domain: str,
    user_email: str,
    background_tasks: BackgroundTasks
):
    """Perform comprehensive health check for widget deployment"""
    logger.info(f"🏥 Performing health check for chatbot {chatbot_id} on domain {domain}")

    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)

    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")

        # Perform health check
        health_checks = await deployment_service.perform_widget_health_check(chatbot_id, domain)

        # Store results in background
        background_tasks.add_task(
            deployment_service.store_deployment_check_results,
            chatbot_id,
            domain,
            health_checks
        )

        # Prepare response
        passed_checks = [c for c in health_checks if c.status == 'passed']
        failed_checks = [c for c in health_checks if c.status == 'failed']
        warning_checks = [c for c in health_checks if c.status == 'warning']

        overall_status = 'passed'
        if failed_checks:
            overall_status = 'failed'
        elif warning_checks:
            overall_status = 'warning'

        return {
            "chatbot_id": chatbot_id,
            "domain": domain,
            "overall_status": overall_status,
            "total_checks": len(health_checks),
            "passed_checks": len(passed_checks),
            "failed_checks": len(failed_checks),
            "warning_checks": len(warning_checks),
            "checks": [
                {
                    "check_type": check.check_type,
                    "status": check.status,
                    "message": check.message,
                    "details": check.details,
                    "timestamp": check.timestamp.isoformat()
                }
                for check in health_checks
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error performing health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}"
        )

@router.get("/{chatbot_id}/deployment-history")
async def get_widget_deployment_history(
    chatbot_id: str,
    user_email: str,
    days: int = Query(default=30, ge=1, le=90, description="Days of history to retrieve")
):
    """Get deployment check history for a chatbot"""
    logger.info(f"📊 Getting deployment history for chatbot {chatbot_id}")

    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)

    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")

        # Get deployment history
        history = await deployment_service.get_deployment_history(chatbot_id, days)

        return {
            "chatbot_id": chatbot_id,
            "history": history,
            "total_checks": len(history),
            "time_range": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting deployment history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment history: {str(e)}"
        )

# Public Widget Configuration Endpoint (for widget loading)

@router.get("/public/{chatbot_id}/config")
async def get_public_widget_config(chatbot_id: str):
    """Get public widget configuration for embedding (no auth required)"""
    logger.info(f"🌐 Getting public widget config for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    
    try:
        # Get chatbot info
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("is_active", True).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found or inactive")
        
        chatbot = chatbot_response.data[0]
        
        # Get active widget configuration
        config_response = supabase.table("widget_configurations").select("*").eq("chatbot_id", chatbot_id).eq("deployment_status", "active").execute()
        
        widget_config = {}
        if config_response.data:
            config = config_response.data[0]
            # Return only safe, public configuration data
            widget_config = {
                "theme": config.get("theme", "light"),
                "position": config.get("position", "bottom-right"),
                "primary_color": config.get("primary_color", "#3b82f6"),
                "secondary_color": config.get("secondary_color", "#1f2937"),
                "border_radius": config.get("border_radius", 12),
                "auto_open": config.get("auto_open", False),
                "auto_open_delay": config.get("auto_open_delay", 3000),
                "show_avatar": config.get("show_avatar", True),
                "enable_sound": config.get("enable_sound", True),
                "enable_typing_indicator": config.get("enable_typing_indicator", True),
                "max_width": config.get("max_width", 400),
                "max_height": config.get("max_height", 600),
                "z_index": config.get("z_index", 999999),
                "custom_branding": config.get("custom_branding", {}),
                "conversation_starters": config.get("conversation_starters", []),
                "language_settings": config.get("language_settings", {}),
                "custom_css": config.get("custom_css", "")
            }
        
        # Combine chatbot and widget configuration
        public_config = {
            "chatbot_id": chatbot_id,
            "name": chatbot["name"],
            "description": chatbot.get("description", ""),
            "appearance_config": chatbot.get("appearance_config", {}),
            "behavior_config": chatbot.get("behavior_config", {}),
            "widget_config": widget_config
        }
        
        logger.info(f"✅ Returning public widget config for {chatbot['name']}")
        return public_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting public widget config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget configuration: {str(e)}"
        )