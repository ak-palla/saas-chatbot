from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

from app.models.widget import (
    WidgetAnalytics, WidgetAnalyticsCreate, WidgetAnalyticsUpdate,
    WidgetInteraction, WidgetInteractionCreate,
    WidgetSession, WidgetSessionCreate, WidgetSessionUpdate,
    WidgetAnalyticsSummary, WidgetPerformanceMetrics, WidgetEngagementMetrics,
    WidgetAnalyticsReport, WidgetABTestResult
)
from app.core.database import get_supabase_admin

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Helper function to get user_id from email
async def get_user_id_from_email(user_email: str):
    """Get user ID from email"""
    supabase = get_supabase_admin()
    user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
    
    if not user_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user_response.data[0]["id"]

# Analytics Tracking Endpoints

@router.post("/{chatbot_id}/analytics", response_model=WidgetAnalytics)
async def track_widget_analytics(
    chatbot_id: str,
    analytics: WidgetAnalyticsCreate
):
    """Track widget analytics (public endpoint for widget usage)"""
    logger.info(f"📊 Tracking analytics for chatbot {chatbot_id}, session {analytics.session_id}")
    
    supabase = get_supabase_admin()
    
    try:
        # Verify chatbot exists and is active
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("is_active", True).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found or inactive")
        
        analytics_data = {
            **analytics.dict(),
            "chatbot_id": chatbot_id
        }
        
        response = supabase.table("widget_analytics").insert(analytics_data).execute()
        logger.info(f"✅ Widget analytics tracked: {response.data[0]['id']}")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error tracking widget analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track widget analytics: {str(e)}"
        )

@router.put("/{chatbot_id}/analytics/{analytics_id}")
async def update_widget_analytics(
    chatbot_id: str,
    analytics_id: str,
    analytics_update: WidgetAnalyticsUpdate
):
    """Update widget analytics session (public endpoint)"""
    logger.info(f"🔄 Updating analytics {analytics_id} for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    
    try:
        # Verify analytics record exists for this chatbot
        existing = supabase.table("widget_analytics").select("*").eq("id", analytics_id).eq("chatbot_id", chatbot_id).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analytics record not found")
        
        # Update analytics
        update_data = {k: v for k, v in analytics_update.dict().items() if v is not None}
        if update_data:
            response = supabase.table("widget_analytics").update(update_data).eq("id", analytics_id).execute()
            logger.info(f"✅ Widget analytics updated successfully")
            return {"message": "Analytics updated successfully"}
        else:
            return {"message": "No updates provided"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error updating widget analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget analytics: {str(e)}"
        )

@router.post("/{chatbot_id}/interactions", response_model=WidgetInteraction)
async def track_widget_interaction(
    chatbot_id: str,
    interaction: WidgetInteractionCreate
):
    """Track widget interaction (public endpoint)"""
    logger.info(f"🎯 Tracking interaction for chatbot {chatbot_id}: {interaction.interaction_type}")
    
    supabase = get_supabase_admin()
    
    try:
        interaction_data = {
            **interaction.dict(),
            "chatbot_id": chatbot_id
        }
        
        response = supabase.table("widget_interactions").insert(interaction_data).execute()
        logger.info(f"✅ Widget interaction tracked: {response.data[0]['id']}")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"💥 Error tracking widget interaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track widget interaction: {str(e)}"
        )

# Analytics Reporting Endpoints (Authenticated)

@router.get("/{chatbot_id}/analytics/summary", response_model=WidgetAnalyticsSummary)
async def get_analytics_summary(
    chatbot_id: str,
    user_email: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis")
):
    """Get analytics summary for a chatbot"""
    logger.info(f"📈 Getting analytics summary for chatbot {chatbot_id} ({days} days)")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Calculate date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=days)
        
        # Get analytics data
        analytics_response = supabase.table("widget_analytics").select("*").eq("chatbot_id", chatbot_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
        
        analytics_data = analytics_response.data
        
        if not analytics_data:
            return WidgetAnalyticsSummary(
                total_sessions=0,
                total_interactions=0,
                average_session_duration=0.0,
                bounce_rate=100.0,
                conversion_rate=0.0,
                top_pages=[],
                top_countries=[],
                device_breakdown={},
                browser_breakdown={}
            )
        
        # Calculate metrics
        total_sessions = len(analytics_data)
        total_interactions = sum(session.get("messages_sent", 0) + session.get("messages_received", 0) for session in analytics_data)
        
        # Average session duration
        durations = [session.get("session_duration_seconds", 0) for session in analytics_data if session.get("session_duration_seconds")]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Bounce rate (sessions with no interactions)
        bounced_sessions = sum(1 for session in analytics_data if session.get("bounce_rate", True))
        bounce_rate = (bounced_sessions / total_sessions) * 100 if total_sessions > 0 else 100.0
        
        # Conversion rate (sessions where widget was opened)
        converted_sessions = sum(1 for session in analytics_data if session.get("widget_opened", False))
        conversion_rate = (converted_sessions / total_sessions) * 100 if total_sessions > 0 else 0.0
        
        # Top pages
        page_counts = defaultdict(int)
        for session in analytics_data:
            if session.get("page_url"):
                page_counts[session["page_url"]] += 1
        
        top_pages = [{"page": page, "sessions": count} for page, count in sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        # Top countries
        country_counts = defaultdict(int)
        for session in analytics_data:
            if session.get("country_code"):
                country_counts[session["country_code"]] += 1
        
        top_countries = [{"country": country, "sessions": count} for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        # Device breakdown
        device_counts = defaultdict(int)
        for session in analytics_data:
            device = session.get("device_type", "unknown")
            device_counts[device] += 1
        
        # Browser breakdown
        browser_counts = defaultdict(int)
        for session in analytics_data:
            browser = session.get("browser_name", "unknown")
            browser_counts[browser] += 1
        
        summary = WidgetAnalyticsSummary(
            total_sessions=total_sessions,
            total_interactions=total_interactions,
            average_session_duration=avg_duration,
            bounce_rate=bounce_rate,
            conversion_rate=conversion_rate,
            top_pages=top_pages,
            top_countries=top_countries,
            device_breakdown=dict(device_counts),
            browser_breakdown=dict(browser_counts)
        )
        
        logger.info(f"✅ Analytics summary calculated: {total_sessions} sessions, {total_interactions} interactions")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting analytics summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics summary: {str(e)}"
        )

@router.get("/{chatbot_id}/analytics/performance", response_model=WidgetPerformanceMetrics)
async def get_performance_metrics(
    chatbot_id: str,
    user_email: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """Get performance metrics for a chatbot widget"""
    logger.info(f"⚡ Getting performance metrics for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Get performance data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics_response = supabase.table("widget_analytics").select("load_time_ms, first_paint_ms, time_to_interactive_ms").eq("chatbot_id", chatbot_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
        
        analytics_data = analytics_response.data
        
        if not analytics_data:
            return WidgetPerformanceMetrics(
                average_load_time=0.0,
                average_first_paint=0.0,
                average_time_to_interactive=0.0,
                error_rate=0.0,
                uptime_percentage=100.0
            )
        
        # Calculate averages
        load_times = [session.get("load_time_ms", 0) for session in analytics_data if session.get("load_time_ms")]
        first_paints = [session.get("first_paint_ms", 0) for session in analytics_data if session.get("first_paint_ms")]
        tti_times = [session.get("time_to_interactive_ms", 0) for session in analytics_data if session.get("time_to_interactive_ms")]
        
        avg_load_time = sum(load_times) / len(load_times) if load_times else 0.0
        avg_first_paint = sum(first_paints) / len(first_paints) if first_paints else 0.0
        avg_tti = sum(tti_times) / len(tti_times) if tti_times else 0.0
        
        # Get deployment errors for error rate calculation
        deployments_response = supabase.table("widget_deployments").select("status").eq("chatbot_id", chatbot_id).execute()
        deployments = deployments_response.data
        
        total_deployments = len(deployments)
        error_deployments = sum(1 for d in deployments if d.get("status") == "error")
        error_rate = (error_deployments / total_deployments) * 100 if total_deployments > 0 else 0.0
        
        # Calculate uptime (assuming 99.9% default, would need monitoring system for real data)
        uptime_percentage = 99.9 - (error_rate * 0.1) if error_rate < 1 else 99.0
        
        metrics = WidgetPerformanceMetrics(
            average_load_time=avg_load_time,
            average_first_paint=avg_first_paint,
            average_time_to_interactive=avg_tti,
            error_rate=error_rate,
            uptime_percentage=uptime_percentage
        )
        
        logger.info(f"✅ Performance metrics calculated: {avg_load_time:.1f}ms avg load time")
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/{chatbot_id}/analytics/engagement", response_model=WidgetEngagementMetrics)
async def get_engagement_metrics(
    chatbot_id: str,
    user_email: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """Get engagement metrics for a chatbot widget"""
    logger.info(f"💬 Getting engagement metrics for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    user_id = await get_user_id_from_email(user_email)
    
    try:
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Get engagement data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics_response = supabase.table("widget_analytics").select("widget_opened, messages_sent, messages_received").eq("chatbot_id", chatbot_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
        
        sessions_response = supabase.table("widget_sessions").select("goal_completed, satisfaction_rating, engagement_score").eq("chatbot_id", chatbot_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
        
        analytics_data = analytics_response.data
        sessions_data = sessions_response.data
        
        if not analytics_data:
            return WidgetEngagementMetrics(
                total_widget_opens=0,
                total_messages=0,
                average_messages_per_session=0.0,
                user_satisfaction=0.0,
                goal_completion_rate=0.0
            )
        
        # Calculate engagement metrics
        total_widget_opens = sum(1 for session in analytics_data if session.get("widget_opened", False))
        total_messages = sum(session.get("messages_sent", 0) + session.get("messages_received", 0) for session in analytics_data)
        
        total_sessions = len(analytics_data)
        avg_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0.0
        
        # User satisfaction from sessions data
        ratings = [session.get("satisfaction_rating", 0) for session in sessions_data if session.get("satisfaction_rating")]
        user_satisfaction = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Goal completion rate
        completed_goals = sum(1 for session in sessions_data if session.get("goal_completed", False))
        goal_completion_rate = (completed_goals / len(sessions_data)) * 100 if sessions_data else 0.0
        
        metrics = WidgetEngagementMetrics(
            total_widget_opens=total_widget_opens,
            total_messages=total_messages,
            average_messages_per_session=avg_messages_per_session,
            user_satisfaction=user_satisfaction,
            goal_completion_rate=goal_completion_rate
        )
        
        logger.info(f"✅ Engagement metrics calculated: {total_widget_opens} opens, {total_messages} messages")
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting engagement metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get engagement metrics: {str(e)}"
        )

@router.get("/{chatbot_id}/analytics/report", response_model=WidgetAnalyticsReport)
async def get_analytics_report(
    chatbot_id: str,
    user_email: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """Get comprehensive analytics report for a chatbot widget"""
    logger.info(f"📊 Generating analytics report for chatbot {chatbot_id}")
    
    try:
        # Get all metrics components
        summary = await get_analytics_summary(chatbot_id, user_email, days)
        performance = await get_performance_metrics(chatbot_id, user_email, days)
        engagement = await get_engagement_metrics(chatbot_id, user_email, days)
        
        # Get time series data for charts
        supabase = get_supabase_admin()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get daily analytics data for time series
        daily_analytics = supabase.table("widget_analytics").select("created_at, widget_opened, messages_sent").eq("chatbot_id", chatbot_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).order("created_at").execute()
        
        # Group by day for time series
        daily_data = defaultdict(lambda: {"sessions": 0, "opens": 0, "messages": 0})
        for record in daily_analytics.data:
            day = record["created_at"][:10]  # Extract date part
            daily_data[day]["sessions"] += 1
            if record.get("widget_opened"):
                daily_data[day]["opens"] += 1
            daily_data[day]["messages"] += record.get("messages_sent", 0)
        
        time_series_data = [
            {
                "date": day,
                "sessions": data["sessions"],
                "opens": data["opens"],
                "messages": data["messages"]
            }
            for day, data in sorted(daily_data.items())
        ]
        
        # Get recent interactions
        recent_interactions_response = supabase.table("widget_interactions").select("*").eq("chatbot_id", chatbot_id).order("created_at", desc=True).limit(50).execute()
        
        # Get A/B test results (if any)
        ab_test_response = supabase.table("widget_ab_test_results").select("*").eq("chatbot_id", chatbot_id).execute()
        
        report = WidgetAnalyticsReport(
            summary=summary,
            performance=performance,
            engagement=engagement,
            time_series_data=time_series_data,
            recent_interactions=recent_interactions_response.data,
            ab_test_results=ab_test_response.data
        )
        
        logger.info(f"✅ Analytics report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"💥 Error generating analytics report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics report: {str(e)}"
        )

# Session Management Endpoints

@router.post("/{chatbot_id}/sessions", response_model=WidgetSession)
async def create_widget_session(
    chatbot_id: str,
    session: WidgetSessionCreate
):
    """Create a new widget session (public endpoint)"""
    logger.info(f"📝 Creating widget session for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    
    try:
        session_data = {
            **session.dict(),
            "chatbot_id": chatbot_id
        }
        
        response = supabase.table("widget_sessions").insert(session_data).execute()
        logger.info(f"✅ Widget session created: {response.data[0]['id']}")
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"💥 Error creating widget session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget session: {str(e)}"
        )

@router.put("/{chatbot_id}/sessions/{session_id}")
async def update_widget_session(
    chatbot_id: str,
    session_id: str,
    session_update: WidgetSessionUpdate
):
    """Update a widget session (public endpoint)"""
    logger.info(f"🔄 Updating widget session {session_id} for chatbot {chatbot_id}")
    
    supabase = get_supabase_admin()
    
    try:
        # Verify session exists for this chatbot
        existing = supabase.table("widget_sessions").select("*").eq("id", session_id).eq("chatbot_id", chatbot_id).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget session not found")
        
        # Update session
        update_data = {k: v for k, v in session_update.dict().items() if v is not None}
        if update_data:
            response = supabase.table("widget_sessions").update(update_data).eq("id", session_id).execute()
            logger.info(f"✅ Widget session updated successfully")
            return {"message": "Session updated successfully"}
        else:
            return {"message": "No updates provided"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error updating widget session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget session: {str(e)}"
        )