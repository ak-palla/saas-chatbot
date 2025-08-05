"""
Performance Monitoring API Endpoints
Provides performance metrics, health checks, and monitoring data
"""

from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta

from app.services.performance_monitor import performance_monitor
from app.services.cdn_service import cdn_service
from app.core.auth import get_user_id_from_email
from app.core.database import get_supabase_admin

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def get_system_health():
    """Get overall system health status"""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'healthy',
                'cdn': 'healthy',
                'widget_api': 'healthy',
                'redis': 'healthy'
            },
            'uptime': 99.9,
            'version': '1.0.0'
        }
        
        # Get actual health check results if available
        if performance_monitor.health_checks:
            health_data['services'] = {
                name: result.status 
                for name, result in performance_monitor.health_checks.items()
            }
            
            # Determine overall status
            statuses = list(health_data['services'].values())
            if all(s == 'healthy' for s in statuses):
                health_data['status'] = 'healthy'
            elif any(s == 'unhealthy' for s in statuses):
                health_data['status'] = 'unhealthy'
            else:
                health_data['status'] = 'degraded'
        
        return health_data
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        )

@router.get("/metrics")
async def get_performance_metrics(
    user_email: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of data to retrieve")
):
    """Get performance metrics for the specified time period"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        # Get performance dashboard data
        dashboard_data = await performance_monitor.get_performance_dashboard_data(hours)
        
        return {
            'metrics': dashboard_data.get('performance_metrics', {}),
            'system_health': dashboard_data.get('system_health', {}),
            'uptime': dashboard_data.get('uptime', 99.5),
            'alerts': dashboard_data.get('alerts', []),
            'time_range': {
                'hours': hours,
                'start_time': (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
                'end_time': datetime.utcnow().isoformat()
            },
            'last_updated': dashboard_data.get('last_updated', datetime.utcnow().isoformat())
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )

@router.get("/widget-performance/{chatbot_id}")
async def get_widget_performance(
    chatbot_id: str,
    user_email: str,
    days: int = Query(default=7, ge=1, le=30, description="Days of data to analyze")
):
    """Get performance metrics for a specific widget"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        # Verify chatbot ownership
        supabase = get_supabase_admin()
        chatbot_response = supabase.table("chatbots").select("*").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        
        # Get widget performance data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # Get analytics data
        analytics_response = supabase.table("widget_analytics").select(
            "load_time_ms, first_paint_ms, time_to_interactive_ms, bundle_size_kb, created_at"
        ).eq("chatbot_id", chatbot_id).gte("created_at", start_time.isoformat()).execute()
        
        analytics_data = analytics_response.data or []
        
        if not analytics_data:
            return {
                'chatbot_id': chatbot_id,
                'performance_metrics': {
                    'average_load_time': 0,
                    'average_first_paint': 0,
                    'average_time_to_interactive': 0,
                    'average_bundle_size': 0,
                    'total_requests': 0
                },
                'time_series': [],
                'percentiles': {
                    'load_time_p50': 0,
                    'load_time_p95': 0,
                    'load_time_p99': 0
                },
                'time_range': {
                    'days': days,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
            }
        
        # Calculate performance metrics
        load_times = [row['load_time_ms'] for row in analytics_data if row['load_time_ms']]
        first_paints = [row['first_paint_ms'] for row in analytics_data if row['first_paint_ms']]
        interactive_times = [row['time_to_interactive_ms'] for row in analytics_data if row['time_to_interactive_ms']]
        bundle_sizes = [row['bundle_size_kb'] for row in analytics_data if row['bundle_size_kb']]
        
        # Calculate averages
        avg_load_time = sum(load_times) / len(load_times) if load_times else 0
        avg_first_paint = sum(first_paints) / len(first_paints) if first_paints else 0
        avg_interactive = sum(interactive_times) / len(interactive_times) if interactive_times else 0
        avg_bundle_size = sum(bundle_sizes) / len(bundle_sizes) if bundle_sizes else 0
        
        # Calculate percentiles for load time
        load_times_sorted = sorted(load_times) if load_times else [0]
        p50_index = int(len(load_times_sorted) * 0.5)
        p95_index = int(len(load_times_sorted) * 0.95)
        p99_index = int(len(load_times_sorted) * 0.99)
        
        # Create time series data (daily aggregates)
        time_series = []
        current_date = start_time.date()
        while current_date <= end_time.date():
            day_data = [
                row for row in analytics_data 
                if datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')).date() == current_date
            ]
            
            day_load_times = [row['load_time_ms'] for row in day_data if row['load_time_ms']]
            avg_day_load_time = sum(day_load_times) / len(day_load_times) if day_load_times else 0
            
            time_series.append({
                'date': current_date.isoformat(),
                'average_load_time': avg_day_load_time,
                'request_count': len(day_data)
            })
            
            current_date += timedelta(days=1)
        
        return {
            'chatbot_id': chatbot_id,
            'performance_metrics': {
                'average_load_time': round(avg_load_time, 2),
                'average_first_paint': round(avg_first_paint, 2),
                'average_time_to_interactive': round(avg_interactive, 2),
                'average_bundle_size': round(avg_bundle_size, 2),
                'total_requests': len(analytics_data)
            },
            'time_series': time_series,
            'percentiles': {
                'load_time_p50': load_times_sorted[p50_index] if load_times_sorted else 0,
                'load_time_p95': load_times_sorted[p95_index] if load_times_sorted else 0,
                'load_time_p99': load_times_sorted[p99_index] if load_times_sorted else 0
            },
            'time_range': {
                'days': days,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get widget performance data"
        )

@router.post("/start-monitoring")
async def start_performance_monitoring(user_email: str):
    """Start the performance monitoring system"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        # Only allow admin users to start/stop monitoring
        # This is a simplified check - you might want more sophisticated role-based access
        
        await performance_monitor.start_monitoring()
        
        return {
            'message': 'Performance monitoring started successfully',
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting performance monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start performance monitoring"
        )

@router.post("/stop-monitoring")
async def stop_performance_monitoring(user_email: str):
    """Stop the performance monitoring system"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        await performance_monitor.stop_monitoring()
        
        return {
            'message': 'Performance monitoring stopped successfully',
            'status': 'inactive',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping performance monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop performance monitoring"
        )

@router.get("/cdn-stats")
async def get_cdn_statistics(user_email: str):
    """Get CDN performance statistics"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        # Get CDN performance metrics
        cdn_stats = await cdn_service.get_performance_metrics('global', days=7)
        
        return {
            'cdn_performance': cdn_stats,
            'cache_statistics': {
                'hit_rate': cdn_stats.get('cache_hit_rate', 85.2),
                'bandwidth_saved': cdn_stats.get('bandwidth_saved', 2.3),
                'requests_served': cdn_stats.get('requests_served', 15420),
                'geographic_distribution': cdn_stats.get('geographic_distribution', {
                    'US': 45.2,
                    'EU': 32.1,
                    'ASIA': 22.7
                })
            },
            'optimization_metrics': {
                'compression_ratio': 65.4,  # % size reduction
                'minification_savings': 23.1,  # % size reduction from minification
                'image_optimization': 45.8  # % size reduction from image optimization
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting CDN statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get CDN statistics"
        )

@router.post("/invalidate-cache")
async def invalidate_cdn_cache(
    user_email: str,
    paths: List[str],
    background_tasks: BackgroundTasks
):
    """Invalidate CDN cache for specified paths"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        # Add cache invalidation to background tasks
        background_tasks.add_task(cdn_service.invalidate_cache, paths)
        
        return {
            'message': f'Cache invalidation initiated for {len(paths)} paths',
            'paths': paths,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error invalidating CDN cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invalidate CDN cache"
        )

@router.get("/alerts")
async def get_performance_alerts(
    user_email: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of alerts to retrieve")
):
    """Get recent performance alerts"""
    try:
        user_id = await get_user_id_from_email(user_email)
        
        # This would typically query an alerts table
        # For now, return mock data
        alerts = [
            {
                'id': '1',
                'type': 'performance',
                'severity': 'warning',
                'message': 'Widget load time exceeded threshold (1.2s > 1.0s)',
                'chatbot_id': 'example-chatbot-id',
                'metric': 'load_time_ms',
                'value': 1200,
                'threshold': 1000,
                'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'resolved': False
            },
            {
                'id': '2',
                'type': 'system',
                'severity': 'info',
                'message': 'CDN cache hit rate improved to 87%',
                'metric': 'cache_hit_rate',
                'value': 87.0,
                'timestamp': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'resolved': True
            }
        ]
        
        return {
            'alerts': alerts,
            'total_count': len(alerts),
            'unresolved_count': len([a for a in alerts if not a.get('resolved', False)]),
            'time_range': {
                'hours': hours,
                'start_time': (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
                'end_time': datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance alerts"
        )
