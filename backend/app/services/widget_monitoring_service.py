import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import aiohttp
from urllib.parse import urlparse
import ssl

from app.core.database import get_supabase_admin
from app.models.widget import WidgetDeployment

# Set up logging
logger = logging.getLogger(__name__)

class WidgetMonitoringService:
    """Service for monitoring widget performance, uptime, and health"""
    
    def __init__(self):
        self.supabase = get_supabase_admin()
        self.monitoring_interval = 300  # 5 minutes
        self.alert_thresholds = {
            'response_time': 3000,  # 3 seconds
            'error_rate': 5.0,      # 5%
            'uptime': 95.0,         # 95%
            'load_time': 2000,      # 2 seconds
        }
        self.monitoring_active = {}  # Track active monitoring sessions
        
    async def start_monitoring(self, chatbot_id: str) -> Dict[str, Any]:
        """Start monitoring all deployments for a chatbot"""
        logger.info(f"🔍 Starting monitoring for chatbot {chatbot_id}")
        
        try:
            # Get all active deployments for this chatbot
            deployments_response = self.supabase.table("widget_deployments").select("*").eq("chatbot_id", chatbot_id).eq("status", "active").execute()
            
            deployments = deployments_response.data
            
            if not deployments:
                return {
                    "success": False,
                    "message": "No active deployments found for monitoring"
                }
            
            # Start monitoring tasks for each deployment
            monitoring_tasks = []
            for deployment in deployments:
                task = asyncio.create_task(
                    self._monitor_deployment_continuously(deployment)
                )
                monitoring_tasks.append(task)
            
            self.monitoring_active[chatbot_id] = {
                "tasks": monitoring_tasks,
                "started_at": datetime.utcnow(),
                "deployment_count": len(deployments)
            }
            
            logger.info(f"✅ Started monitoring {len(deployments)} deployments for chatbot {chatbot_id}")
            
            return {
                "success": True,
                "message": f"Started monitoring {len(deployments)} deployments",
                "deployment_count": len(deployments)
            }
            
        except Exception as e:
            logger.error(f"💥 Error starting monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_monitoring(self, chatbot_id: str) -> Dict[str, Any]:
        """Stop monitoring for a chatbot"""
        logger.info(f"⏹️ Stopping monitoring for chatbot {chatbot_id}")
        
        if chatbot_id not in self.monitoring_active:
            return {
                "success": False,
                "message": "No active monitoring found for this chatbot"
            }
        
        try:
            # Cancel all monitoring tasks
            monitoring_session = self.monitoring_active[chatbot_id]
            for task in monitoring_session["tasks"]:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            await asyncio.gather(*monitoring_session["tasks"], return_exceptions=True)
            
            # Remove from active monitoring
            del self.monitoring_active[chatbot_id]
            
            logger.info(f"✅ Stopped monitoring for chatbot {chatbot_id}")
            
            return {
                "success": True,
                "message": "Monitoring stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"💥 Error stopping monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _monitor_deployment_continuously(self, deployment: Dict[str, Any]):
        """Continuously monitor a single deployment"""
        deployment_id = deployment["id"]
        domain = deployment["domain"]
        
        logger.info(f"🔄 Starting continuous monitoring for deployment {deployment_id} on {domain}")
        
        while True:
            try:
                # Perform health check
                health_result = await self._perform_health_check(deployment)
                
                # Store monitoring result
                await self._store_monitoring_result(deployment_id, health_result)
                
                # Check if alerts need to be sent
                await self._check_and_send_alerts(deployment, health_result)
                
                # Wait for next check
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                logger.info(f"⏹️ Monitoring cancelled for deployment {deployment_id}")
                break
            except Exception as e:
                logger.error(f"💥 Error in continuous monitoring for {deployment_id}: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _perform_health_check(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive health check for a deployment"""
        domain = deployment["domain"]
        page_url = deployment.get("page_url") or f"https://{domain}"
        
        health_result = {
            "deployment_id": deployment["id"],
            "domain": domain,
            "page_url": page_url,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # 1. Basic connectivity check
        connectivity_result = await self._check_connectivity(page_url)
        health_result["checks"]["connectivity"] = connectivity_result
        
        # 2. Widget presence check
        widget_presence = await self._check_widget_presence(page_url, deployment["chatbot_id"])
        health_result["checks"]["widget_presence"] = widget_presence
        
        # 3. Performance check
        performance_result = await self._check_performance(page_url)
        health_result["checks"]["performance"] = performance_result
        
        # 4. SSL certificate check
        ssl_result = await self._check_ssl_certificate(domain)
        health_result["checks"]["ssl"] = ssl_result
        
        # 5. CORS check
        cors_result = await self._check_cors(page_url)
        health_result["checks"]["cors"] = cors_result
        
        # Calculate overall health score
        health_result["overall_score"] = self._calculate_health_score(health_result["checks"])
        health_result["status"] = "healthy" if health_result["overall_score"] >= 80 else "degraded" if health_result["overall_score"] >= 60 else "unhealthy"
        
        return health_result
    
    async def _check_connectivity(self, url: str) -> Dict[str, Any]:
        """Check basic connectivity to the URL"""
        start_time = datetime.utcnow()
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    end_time = datetime.utcnow()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    return {
                        "status": "success",
                        "response_code": response.status,
                        "response_time_ms": round(response_time),
                        "content_length": response.headers.get("Content-Length", 0),
                        "server": response.headers.get("Server", "Unknown")
                    }
        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "status": "error",
                "error": str(e),
                "response_time_ms": round(response_time),
                "response_code": 0
            }
    
    async def _check_widget_presence(self, url: str, chatbot_id: str) -> Dict[str, Any]:
        """Check if the widget is present and properly loaded on the page"""
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            "status": "error",
                            "error": f"Page returned status {response.status}"
                        }
                    
                    content = await response.text()
                    
                    # Check for widget script presence
                    widget_script_found = any([
                        f'data-chatbot-id="{chatbot_id}"' in content,
                        f"chatbotId: '{chatbot_id}'" in content,
                        f'chatbot_id: "{chatbot_id}"' in content,
                        "chatbot-widget" in content.lower()
                    ])
                    
                    # Check for widget CDN or script URLs
                    widget_cdn_found = any([
                        "chatbot-saas.com" in content,
                        "widget.js" in content,
                        "embed.js" in content
                    ])
                    
                    return {
                        "status": "success",
                        "widget_script_found": widget_script_found,
                        "widget_cdn_found": widget_cdn_found,
                        "page_size_kb": round(len(content) / 1024, 2),
                        "has_meta_tags": '<meta' in content,
                        "has_csp": 'Content-Security-Policy' in str(response.headers)
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_performance(self, url: str) -> Dict[str, Any]:
        """Check page performance metrics"""
        start_time = datetime.utcnow()
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Measure TTFB (Time to First Byte)
                ttfb_start = datetime.utcnow()
                async with session.get(url) as response:
                    # Read first chunk
                    async for chunk in response.content.iter_chunked(1024):
                        ttfb_end = datetime.utcnow()
                        ttfb = (ttfb_end - ttfb_start).total_seconds() * 1000
                        break
                    
                    # Read rest of content
                    content = await response.read()
                    end_time = datetime.utcnow()
                    
                    total_time = (end_time - start_time).total_seconds() * 1000
                    content_size = len(content)
                    
                    # Calculate performance metrics
                    transfer_rate = (content_size / 1024) / (total_time / 1000) if total_time > 0 else 0
                    
                    return {
                        "status": "success",
                        "ttfb_ms": round(ttfb),
                        "total_load_time_ms": round(total_time),
                        "content_size_kb": round(content_size / 1024, 2),
                        "transfer_rate_kbps": round(transfer_rate, 2),
                        "compression_used": 'gzip' in response.headers.get('Content-Encoding', '').lower(),
                        "cache_headers": bool(response.headers.get('Cache-Control') or response.headers.get('ETag'))
                    }
                    
        except Exception as e:
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "status": "error",
                "error": str(e),
                "total_load_time_ms": round(total_time)
            }
    
    async def _check_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate validity"""
        try:
            # Remove protocol if present
            if '://' in domain:
                domain = domain.split('://')[1]
            
            # Remove path if present
            domain = domain.split('/')[0]
            
            # Get SSL certificate info
            context = ssl.create_default_context()
            
            try:
                # Connect and get certificate
                with ssl.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        
                        # Parse certificate dates
                        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        
                        now = datetime.utcnow()
                        days_until_expiry = (not_after - now).days
                        
                        return {
                            "status": "success",
                            "issuer": cert.get('issuer', [{}])[0].get('organizationName', 'Unknown'),
                            "subject": cert.get('subject', [{}])[0].get('commonName', domain),
                            "not_before": not_before.isoformat(),
                            "not_after": not_after.isoformat(),
                            "days_until_expiry": days_until_expiry,
                            "is_valid": now >= not_before and now <= not_after,
                            "expires_soon": days_until_expiry <= 30
                        }
                        
            except Exception as ssl_error:
                return {
                    "status": "error",
                    "error": f"SSL connection failed: {str(ssl_error)}",
                    "has_ssl": False
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "has_ssl": False
            }
    
    async def _check_cors(self, url: str) -> Dict[str, Any]:
        """Check CORS configuration for widget loading"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            headers = {
                'Origin': 'https://widget-test.chatbot-saas.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Preflight OPTIONS request
                async with session.options(url, headers=headers) as response:
                    cors_headers = {
                        "access_control_allow_origin": response.headers.get("Access-Control-Allow-Origin"),
                        "access_control_allow_methods": response.headers.get("Access-Control-Allow-Methods"),
                        "access_control_allow_headers": response.headers.get("Access-Control-Allow-Headers"),
                        "access_control_max_age": response.headers.get("Access-Control-Max-Age")
                    }
                    
                    allows_origin = cors_headers["access_control_allow_origin"] in ["*", "https://widget-test.chatbot-saas.com"]
                    
                    return {
                        "status": "success",
                        "allows_widget_origin": allows_origin,
                        "cors_headers": cors_headers,
                        "preflight_status": response.status
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_health_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall health score from check results"""
        scores = []
        weights = {
            "connectivity": 30,
            "widget_presence": 25,
            "performance": 20,
            "ssl": 15,
            "cors": 10
        }
        
        for check_name, check_result in checks.items():
            weight = weights.get(check_name, 10)
            
            if check_result["status"] == "success":
                score = 100
                
                # Adjust score based on specific metrics
                if check_name == "connectivity":
                    response_time = check_result.get("response_time_ms", 0)
                    if response_time > 3000:
                        score = 50
                    elif response_time > 1000:
                        score = 80
                        
                elif check_name == "performance":
                    load_time = check_result.get("total_load_time_ms", 0)
                    if load_time > 5000:
                        score = 40
                    elif load_time > 2000:
                        score = 70
                        
                elif check_name == "ssl":
                    days_until_expiry = check_result.get("days_until_expiry", 365)
                    if days_until_expiry <= 7:
                        score = 30
                    elif days_until_expiry <= 30:
                        score = 70
                        
            else:
                score = 0
            
            scores.append(score * weight / 100)
        
        return sum(scores) / len(scores) if scores else 0
    
    async def _store_monitoring_result(self, deployment_id: str, health_result: Dict[str, Any]):
        """Store monitoring result in database"""
        try:
            monitoring_data = {
                "deployment_id": deployment_id,
                "health_score": health_result["overall_score"],
                "status": health_result["status"],
                "checks_result": health_result["checks"],
                "response_time_ms": health_result["checks"].get("connectivity", {}).get("response_time_ms", 0),
                "load_time_ms": health_result["checks"].get("performance", {}).get("total_load_time_ms", 0),
                "ssl_valid": health_result["checks"].get("ssl", {}).get("is_valid", False),
                "widget_present": health_result["checks"].get("widget_presence", {}).get("widget_script_found", False),
                "created_at": health_result["timestamp"]
            }
            
            # Store in widget_monitoring_logs table (create if not exists)
            self.supabase.table("widget_monitoring_logs").insert(monitoring_data).execute()
            
            # Update deployment status
            deployment_status = "active" if health_result["overall_score"] >= 80 else "error"
            last_error = None if deployment_status == "active" else f"Health score: {health_result['overall_score']:.1f}%"
            
            self.supabase.table("widget_deployments").update({
                "status": deployment_status,
                "last_verified_at": datetime.utcnow().isoformat(),
                "last_error": last_error
            }).eq("id", deployment_id).execute()
            
        except Exception as e:
            logger.error(f"💥 Error storing monitoring result: {str(e)}")
    
    async def _check_and_send_alerts(self, deployment: Dict[str, Any], health_result: Dict[str, Any]):
        """Check if alerts need to be sent based on monitoring results"""
        try:
            alerts = []
            
            # Check response time
            connectivity_check = health_result["checks"].get("connectivity", {})
            if connectivity_check.get("response_time_ms", 0) > self.alert_thresholds["response_time"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"High response time: {connectivity_check['response_time_ms']}ms",
                    "threshold": self.alert_thresholds["response_time"]
                })
            
            # Check overall health score
            if health_result["overall_score"] < self.alert_thresholds["uptime"]:
                alerts.append({
                    "type": "health",
                    "severity": "critical" if health_result["overall_score"] < 50 else "warning",
                    "message": f"Low health score: {health_result['overall_score']:.1f}%",
                    "threshold": self.alert_thresholds["uptime"]
                })
            
            # Check SSL certificate expiry
            ssl_check = health_result["checks"].get("ssl", {})
            if ssl_check.get("expires_soon", False):
                alerts.append({
                    "type": "ssl",
                    "severity": "warning",
                    "message": f"SSL certificate expires in {ssl_check.get('days_until_expiry', 0)} days",
                    "threshold": 30
                })
            
            # Check widget presence
            widget_check = health_result["checks"].get("widget_presence", {})
            if not widget_check.get("widget_script_found", True):
                alerts.append({
                    "type": "widget",
                    "severity": "critical",
                    "message": "Widget script not found on page",
                    "threshold": "presence"
                })
            
            # Store alerts if any
            if alerts:
                for alert in alerts:
                    await self._store_alert(deployment, alert, health_result)
                    
        except Exception as e:
            logger.error(f"💥 Error checking alerts: {str(e)}")
    
    async def _store_alert(self, deployment: Dict[str, Any], alert: Dict[str, Any], health_result: Dict[str, Any]):
        """Store alert in database"""
        try:
            alert_data = {
                "deployment_id": deployment["id"],
                "chatbot_id": deployment["chatbot_id"],
                "alert_type": alert["type"],
                "severity": alert["severity"],
                "message": alert["message"],
                "threshold_value": alert["threshold"],
                "current_value": health_result.get("overall_score", 0),
                "health_check_data": health_result,
                "resolved": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in widget_alerts table (create if not exists)
            self.supabase.table("widget_alerts").insert(alert_data).execute()
            
            logger.warning(f"🚨 Alert generated for deployment {deployment['id']}: {alert['message']}")
            
        except Exception as e:
            logger.error(f"💥 Error storing alert: {str(e)}")
    
    async def get_monitoring_status(self, chatbot_id: str) -> Dict[str, Any]:
        """Get current monitoring status for a chatbot"""
        try:
            # Check if monitoring is active
            is_active = chatbot_id in self.monitoring_active
            
            # Get recent monitoring results
            deployments_response = self.supabase.table("widget_deployments").select("*").eq("chatbot_id", chatbot_id).execute()
            deployments = deployments_response.data
            
            # Get recent alerts
            alerts_response = self.supabase.table("widget_alerts").select("*").eq("chatbot_id", chatbot_id).eq("resolved", False).order("created_at", desc=True).limit(10).execute()
            active_alerts = alerts_response.data
            
            return {
                "monitoring_active": is_active,
                "deployment_count": len(deployments),
                "active_deployments": len([d for d in deployments if d.get("status") == "active"]),
                "active_alerts": len(active_alerts),
                "last_check": max([d.get("last_verified_at", "") for d in deployments]) if deployments else None,
                "overall_health": self._calculate_overall_health(deployments),
                "alerts": active_alerts
            }
            
        except Exception as e:
            logger.error(f"💥 Error getting monitoring status: {str(e)}")
            return {
                "monitoring_active": False,
                "error": str(e)
            }
    
    def _calculate_overall_health(self, deployments: List[Dict[str, Any]]) -> str:
        """Calculate overall health status from deployments"""
        if not deployments:
            return "unknown"
        
        active_count = len([d for d in deployments if d.get("status") == "active"])
        error_count = len([d for d in deployments if d.get("status") == "error"])
        
        if error_count == 0:
            return "healthy"
        elif error_count < len(deployments) / 2:
            return "degraded"
        else:
            return "unhealthy"

# Create singleton instance
widget_monitoring_service = WidgetMonitoringService()