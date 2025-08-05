"""
Performance Monitoring Service for Widget System
Tracks performance metrics, monitors health, and provides alerts
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
import time
from app.core.database import get_supabase_admin
from app.services.cdn_service import cdn_service

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    chatbot_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class HealthCheckResult:
    """Health check result data structure"""
    service_name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    response_time: float
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class PerformanceMonitor:
    """Service for monitoring widget performance and health"""
    
    def __init__(self):
        self.metrics_buffer: List[PerformanceMetric] = []
        self.health_checks: Dict[str, HealthCheckResult] = {}
        self.alert_thresholds = {
            'load_time_ms': 1000,      # Alert if load time > 1s
            'error_rate': 5.0,         # Alert if error rate > 5%
            'uptime': 99.0,            # Alert if uptime < 99%
            'memory_usage': 80.0,      # Alert if memory usage > 80%
            'cpu_usage': 80.0,         # Alert if CPU usage > 80%
        }
        self.monitoring_active = False
    
    async def start_monitoring(self):
        """Start the performance monitoring system"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info("Starting performance monitoring system")
        
        # Start background tasks
        asyncio.create_task(self._collect_metrics_loop())
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._process_metrics_loop())
    
    async def stop_monitoring(self):
        """Stop the performance monitoring system"""
        self.monitoring_active = False
        logger.info("Stopping performance monitoring system")
    
    async def _collect_metrics_loop(self):
        """Background task to collect performance metrics"""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await self._collect_widget_metrics()
                await asyncio.sleep(60)  # Collect every minute
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """Background task to perform health checks"""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(300)  # Health check every 5 minutes
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(300)
    
    async def _process_metrics_loop(self):
        """Background task to process and store metrics"""
        while self.monitoring_active:
            try:
                await self._process_metrics_buffer()
                await asyncio.sleep(30)  # Process every 30 seconds
            except Exception as e:
                logger.error(f"Error in metrics processing loop: {e}")
                await asyncio.sleep(30)
    
    async def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric(PerformanceMetric(
                metric_name='cpu_usage',
                value=cpu_percent,
                unit='percent',
                timestamp=datetime.utcnow()
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.add_metric(PerformanceMetric(
                metric_name='memory_usage',
                value=memory.percent,
                unit='percent',
                timestamp=datetime.utcnow()
            ))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.add_metric(PerformanceMetric(
                metric_name='disk_usage',
                value=disk_percent,
                unit='percent',
                timestamp=datetime.utcnow()
            ))
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_widget_metrics(self):
        """Collect widget-specific performance metrics"""
        try:
            supabase = get_supabase_admin()
            
            # Get recent widget analytics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            response = supabase.table("widget_analytics").select(
                "load_time_ms, first_paint_ms, time_to_interactive_ms, chatbot_id"
            ).gte("created_at", start_time.isoformat()).execute()
            
            if response.data:
                # Calculate average load times
                load_times = [row['load_time_ms'] for row in response.data if row['load_time_ms']]
                if load_times:
                    avg_load_time = sum(load_times) / len(load_times)
                    self.add_metric(PerformanceMetric(
                        metric_name='avg_widget_load_time',
                        value=avg_load_time,
                        unit='milliseconds',
                        timestamp=datetime.utcnow()
                    ))
                
                # Calculate first paint times
                paint_times = [row['first_paint_ms'] for row in response.data if row['first_paint_ms']]
                if paint_times:
                    avg_paint_time = sum(paint_times) / len(paint_times)
                    self.add_metric(PerformanceMetric(
                        metric_name='avg_first_paint_time',
                        value=avg_paint_time,
                        unit='milliseconds',
                        timestamp=datetime.utcnow()
                    ))
            
        except Exception as e:
            logger.error(f"Error collecting widget metrics: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on various services"""
        checks = [
            self._check_database_health(),
            self._check_cdn_health(),
            self._check_widget_endpoints(),
            self._check_redis_health(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, HealthCheckResult):
                self.health_checks[result.service_name] = result
            elif isinstance(result, Exception):
                logger.error(f"Health check failed with exception: {result}")
    
    async def _check_database_health(self) -> HealthCheckResult:
        """Check database connectivity and performance"""
        start_time = time.time()
        try:
            supabase = get_supabase_admin()
            response = supabase.table("chatbots").select("id").limit(1).execute()
            
            response_time = (time.time() - start_time) * 1000
            
            if response.data is not None:
                status = 'healthy' if response_time < 500 else 'degraded'
                return HealthCheckResult(
                    service_name='database',
                    status=status,
                    response_time=response_time
                )
            else:
                return HealthCheckResult(
                    service_name='database',
                    status='unhealthy',
                    response_time=response_time,
                    error_message='No data returned from database'
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name='database',
                status='unhealthy',
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _check_cdn_health(self) -> HealthCheckResult:
        """Check CDN availability and performance"""
        start_time = time.time()
        try:
            # Test CDN by checking if we can access a known asset
            test_url = "https://cdn.example.com/health-check"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        status = 'healthy' if response_time < 1000 else 'degraded'
                        return HealthCheckResult(
                            service_name='cdn',
                            status=status,
                            response_time=response_time
                        )
                    else:
                        return HealthCheckResult(
                            service_name='cdn',
                            status='unhealthy',
                            response_time=response_time,
                            error_message=f'HTTP {response.status}'
                        )
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name='cdn',
                status='unhealthy',
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _check_widget_endpoints(self) -> HealthCheckResult:
        """Check widget API endpoints"""
        start_time = time.time()
        try:
            # Test widget configuration endpoint
            base_url = "http://localhost:8000"  # This should be configurable
            test_url = f"{base_url}/api/v1/widgets/templates"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        status = 'healthy' if response_time < 500 else 'degraded'
                        return HealthCheckResult(
                            service_name='widget_api',
                            status=status,
                            response_time=response_time
                        )
                    else:
                        return HealthCheckResult(
                            service_name='widget_api',
                            status='unhealthy',
                            response_time=response_time,
                            error_message=f'HTTP {response.status}'
                        )
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name='widget_api',
                status='unhealthy',
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _check_redis_health(self) -> HealthCheckResult:
        """Check Redis connectivity and performance"""
        start_time = time.time()
        try:
            if cdn_service.redis_client:
                # Test Redis with a simple ping
                result = cdn_service.redis_client.ping()
                response_time = (time.time() - start_time) * 1000
                
                if result:
                    status = 'healthy' if response_time < 100 else 'degraded'
                    return HealthCheckResult(
                        service_name='redis',
                        status=status,
                        response_time=response_time
                    )
                else:
                    return HealthCheckResult(
                        service_name='redis',
                        status='unhealthy',
                        response_time=response_time,
                        error_message='Redis ping failed'
                    )
            else:
                return HealthCheckResult(
                    service_name='redis',
                    status='unhealthy',
                    response_time=0,
                    error_message='Redis client not available'
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name='redis',
                status='unhealthy',
                response_time=response_time,
                error_message=str(e)
            )
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric to the buffer"""
        self.metrics_buffer.append(metric)
        
        # Check for alerts
        self._check_alert_thresholds(metric)
    
    def _check_alert_thresholds(self, metric: PerformanceMetric):
        """Check if metric exceeds alert thresholds"""
        threshold = self.alert_thresholds.get(metric.metric_name)
        if threshold and metric.value > threshold:
            logger.warning(
                f"Performance alert: {metric.metric_name} = {metric.value} {metric.unit} "
                f"(threshold: {threshold} {metric.unit})"
            )
            # Here you would typically send alerts via email, Slack, etc.
    
    async def _process_metrics_buffer(self):
        """Process and store metrics from buffer"""
        if not self.metrics_buffer:
            return
        
        try:
            # Store metrics in database
            supabase = get_supabase_admin()
            
            metrics_data = []
            for metric in self.metrics_buffer:
                metrics_data.append({
                    'metric_name': metric.metric_name,
                    'value': metric.value,
                    'unit': metric.unit,
                    'chatbot_id': metric.chatbot_id,
                    'metadata': metric.metadata or {},
                    'created_at': metric.timestamp.isoformat()
                })
            
            # Insert metrics in batches
            batch_size = 100
            for i in range(0, len(metrics_data), batch_size):
                batch = metrics_data[i:i + batch_size]
                supabase.table("performance_metrics").insert(batch).execute()
            
            logger.debug(f"Stored {len(metrics_data)} performance metrics")
            
            # Clear buffer
            self.metrics_buffer.clear()
            
        except Exception as e:
            logger.error(f"Error processing metrics buffer: {e}")
    
    async def get_performance_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance data for dashboard"""
        try:
            supabase = get_supabase_admin()
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Get recent metrics
            response = supabase.table("performance_metrics").select("*").gte(
                "created_at", start_time.isoformat()
            ).order("created_at", desc=True).execute()
            
            metrics = response.data if response.data else []
            
            # Process metrics into dashboard format
            dashboard_data = {
                'system_health': {
                    'status': self._get_overall_health_status(),
                    'services': {name: result.status for name, result in self.health_checks.items()}
                },
                'performance_metrics': self._aggregate_metrics(metrics),
                'alerts': self._get_recent_alerts(),
                'uptime': self._calculate_uptime(hours),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting performance dashboard data: {e}")
            return {}
    
    def _get_overall_health_status(self) -> str:
        """Get overall system health status"""
        if not self.health_checks:
            return 'unknown'
        
        statuses = [result.status for result in self.health_checks.values()]
        
        if all(status == 'healthy' for status in statuses):
            return 'healthy'
        elif any(status == 'unhealthy' for status in statuses):
            return 'unhealthy'
        else:
            return 'degraded'
    
    def _aggregate_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate metrics for dashboard display"""
        aggregated = {}
        
        for metric in metrics:
            metric_name = metric['metric_name']
            if metric_name not in aggregated:
                aggregated[metric_name] = {
                    'values': [],
                    'unit': metric['unit'],
                    'latest': metric['value'],
                    'average': 0,
                    'max': metric['value'],
                    'min': metric['value']
                }
            
            aggregated[metric_name]['values'].append({
                'value': metric['value'],
                'timestamp': metric['created_at']
            })
            
            # Update aggregates
            values = [v['value'] for v in aggregated[metric_name]['values']]
            aggregated[metric_name]['average'] = sum(values) / len(values)
            aggregated[metric_name]['max'] = max(values)
            aggregated[metric_name]['min'] = min(values)
        
        return aggregated
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        # This would typically query an alerts table
        # For now, return empty list
        return []
    
    def _calculate_uptime(self, hours: int) -> float:
        """Calculate system uptime percentage"""
        # This would typically calculate based on health check history
        # For now, return a mock value
        return 99.5

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
