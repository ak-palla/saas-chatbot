"""
Deployment Service for Widget System
Handles automated health checks, domain verification, and compatibility testing
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
import ssl
import socket
from urllib.parse import urlparse
from app.core.database import get_supabase_admin

logger = logging.getLogger(__name__)

@dataclass
class DeploymentCheck:
    """Deployment check result"""
    check_type: str
    status: str  # 'passed', 'failed', 'warning'
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class DomainVerification:
    """Domain verification result"""
    domain: str
    verified: bool
    ssl_valid: bool
    ssl_expires: Optional[datetime] = None
    dns_records: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class DeploymentService:
    """Service for managing widget deployments and verification"""
    
    def __init__(self):
        self.user_agents = {
            'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        }
    
    async def verify_domain(self, domain: str) -> DomainVerification:
        """
        Verify domain accessibility and SSL certificate
        
        Args:
            domain: Domain to verify
            
        Returns:
            DomainVerification result
        """
        try:
            # Clean domain
            domain = domain.lower().strip()
            if domain.startswith('http://') or domain.startswith('https://'):
                parsed = urlparse(domain)
                domain = parsed.netloc
            
            # Check basic connectivity
            try:
                socket.gethostbyname(domain)
            except socket.gaierror:
                return DomainVerification(
                    domain=domain,
                    verified=False,
                    ssl_valid=False,
                    error_message="Domain not found or DNS resolution failed"
                )
            
            # Check HTTPS availability and SSL certificate
            ssl_valid = False
            ssl_expires = None
            
            try:
                context = ssl.create_default_context()
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        ssl_valid = True
                        
                        # Parse expiration date
                        if 'notAfter' in cert:
                            ssl_expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        
            except Exception as e:
                logger.debug(f"SSL check failed for {domain}: {e}")
            
            # Test HTTP/HTTPS accessibility
            verified = await self._test_domain_accessibility(domain)
            
            return DomainVerification(
                domain=domain,
                verified=verified,
                ssl_valid=ssl_valid,
                ssl_expires=ssl_expires
            )
            
        except Exception as e:
            logger.error(f"Error verifying domain {domain}: {e}")
            return DomainVerification(
                domain=domain,
                verified=False,
                ssl_valid=False,
                error_message=str(e)
            )
    
    async def _test_domain_accessibility(self, domain: str) -> bool:
        """Test if domain is accessible via HTTP/HTTPS"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Try HTTPS first
                try:
                    async with session.get(f"https://{domain}", allow_redirects=True) as response:
                        return response.status < 500
                except:
                    pass
                
                # Fallback to HTTP
                try:
                    async with session.get(f"http://{domain}", allow_redirects=True) as response:
                        return response.status < 500
                except:
                    pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Domain accessibility test failed for {domain}: {e}")
            return False
    
    async def perform_widget_health_check(self, chatbot_id: str, domain: str) -> List[DeploymentCheck]:
        """
        Perform comprehensive health check for widget deployment
        
        Args:
            chatbot_id: Chatbot ID
            domain: Domain where widget is deployed
            
        Returns:
            List of deployment check results
        """
        checks = []
        
        try:
            # 1. Domain verification
            domain_result = await self.verify_domain(domain)
            checks.append(DeploymentCheck(
                check_type='domain_verification',
                status='passed' if domain_result.verified else 'failed',
                message=f"Domain {domain} {'is accessible' if domain_result.verified else 'is not accessible'}",
                details={'ssl_valid': domain_result.ssl_valid, 'ssl_expires': domain_result.ssl_expires.isoformat() if domain_result.ssl_expires else None}
            ))
            
            # 2. Widget script accessibility
            widget_check = await self._check_widget_script_accessibility(chatbot_id, domain)
            checks.append(widget_check)
            
            # 3. API connectivity
            api_check = await self._check_api_connectivity(chatbot_id)
            checks.append(api_check)
            
            # 4. Cross-browser compatibility
            browser_checks = await self._check_cross_browser_compatibility(domain)
            checks.extend(browser_checks)
            
            # 5. Mobile responsiveness
            mobile_check = await self._check_mobile_responsiveness(domain)
            checks.append(mobile_check)
            
            # 6. Performance check
            performance_check = await self._check_widget_performance(domain)
            checks.append(performance_check)
            
        except Exception as e:
            logger.error(f"Error performing health check for {chatbot_id} on {domain}: {e}")
            checks.append(DeploymentCheck(
                check_type='health_check_error',
                status='failed',
                message=f"Health check failed: {str(e)}"
            ))
        
        return checks
    
    async def _check_widget_script_accessibility(self, chatbot_id: str, domain: str) -> DeploymentCheck:
        """Check if widget script is accessible and loads correctly"""
        try:
            # Test widget script URL
            widget_url = f"https://{domain}/widget/embed.js"  # Adjust based on your setup
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(widget_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        if 'chatbot' in content.lower() or 'widget' in content.lower():
                            return DeploymentCheck(
                                check_type='widget_script',
                                status='passed',
                                message="Widget script is accessible and appears valid",
                                details={'url': widget_url, 'size': len(content)}
                            )
                        else:
                            return DeploymentCheck(
                                check_type='widget_script',
                                status='warning',
                                message="Widget script accessible but content may be invalid",
                                details={'url': widget_url}
                            )
                    else:
                        return DeploymentCheck(
                            check_type='widget_script',
                            status='failed',
                            message=f"Widget script not accessible (HTTP {response.status})",
                            details={'url': widget_url, 'status': response.status}
                        )
                        
        except Exception as e:
            return DeploymentCheck(
                check_type='widget_script',
                status='failed',
                message=f"Widget script check failed: {str(e)}"
            )
    
    async def _check_api_connectivity(self, chatbot_id: str) -> DeploymentCheck:
        """Check API connectivity for the chatbot"""
        try:
            # Test chatbot API endpoint
            api_url = f"http://localhost:8000/api/v1/widgets/public/{chatbot_id}/config"  # Adjust based on your setup
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        return DeploymentCheck(
                            check_type='api_connectivity',
                            status='passed',
                            message="API is accessible and responding",
                            details={'endpoint': api_url}
                        )
                    else:
                        return DeploymentCheck(
                            check_type='api_connectivity',
                            status='failed',
                            message=f"API not accessible (HTTP {response.status})",
                            details={'endpoint': api_url, 'status': response.status}
                        )
                        
        except Exception as e:
            return DeploymentCheck(
                check_type='api_connectivity',
                status='failed',
                message=f"API connectivity check failed: {str(e)}"
            )
    
    async def _check_cross_browser_compatibility(self, domain: str) -> List[DeploymentCheck]:
        """Check cross-browser compatibility"""
        checks = []
        
        for browser, user_agent in self.user_agents.items():
            try:
                headers = {'User-Agent': user_agent}
                
                async with aiohttp.ClientSession(
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as session:
                    async with session.get(f"https://{domain}", allow_redirects=True) as response:
                        if response.status < 400:
                            checks.append(DeploymentCheck(
                                check_type=f'browser_compatibility_{browser}',
                                status='passed',
                                message=f"Compatible with {browser.title()}",
                                details={'user_agent': user_agent, 'status': response.status}
                            ))
                        else:
                            checks.append(DeploymentCheck(
                                check_type=f'browser_compatibility_{browser}',
                                status='warning',
                                message=f"Potential issues with {browser.title()} (HTTP {response.status})",
                                details={'user_agent': user_agent, 'status': response.status}
                            ))
                            
            except Exception as e:
                checks.append(DeploymentCheck(
                    check_type=f'browser_compatibility_{browser}',
                    status='failed',
                    message=f"Failed to test {browser.title()} compatibility: {str(e)}"
                ))
        
        return checks
    
    async def _check_mobile_responsiveness(self, domain: str) -> DeploymentCheck:
        """Check mobile responsiveness"""
        try:
            # Use mobile user agent
            mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            headers = {'User-Agent': mobile_ua}
            
            async with aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as session:
                async with session.get(f"https://{domain}", allow_redirects=True) as response:
                    if response.status < 400:
                        # Check for viewport meta tag and responsive indicators
                        content = await response.text()
                        has_viewport = 'viewport' in content.lower()
                        has_responsive = any(keyword in content.lower() for keyword in ['responsive', 'mobile', '@media'])
                        
                        if has_viewport and has_responsive:
                            status = 'passed'
                            message = "Site appears to be mobile responsive"
                        elif has_viewport:
                            status = 'warning'
                            message = "Site has viewport meta tag but may not be fully responsive"
                        else:
                            status = 'warning'
                            message = "Site may not be optimized for mobile devices"
                        
                        return DeploymentCheck(
                            check_type='mobile_responsiveness',
                            status=status,
                            message=message,
                            details={
                                'has_viewport': has_viewport,
                                'has_responsive_indicators': has_responsive,
                                'status': response.status
                            }
                        )
                    else:
                        return DeploymentCheck(
                            check_type='mobile_responsiveness',
                            status='failed',
                            message=f"Mobile accessibility test failed (HTTP {response.status})"
                        )
                        
        except Exception as e:
            return DeploymentCheck(
                check_type='mobile_responsiveness',
                status='failed',
                message=f"Mobile responsiveness check failed: {str(e)}"
            )
    
    async def _check_widget_performance(self, domain: str) -> DeploymentCheck:
        """Check widget loading performance"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(f"https://{domain}", allow_redirects=True) as response:
                    await response.text()  # Ensure full response is loaded
                    
            load_time = (asyncio.get_event_loop().time() - start_time) * 1000  # Convert to ms
            
            if load_time < 1000:
                status = 'passed'
                message = f"Excellent load time: {load_time:.0f}ms"
            elif load_time < 3000:
                status = 'warning'
                message = f"Acceptable load time: {load_time:.0f}ms"
            else:
                status = 'failed'
                message = f"Slow load time: {load_time:.0f}ms"
            
            return DeploymentCheck(
                check_type='performance',
                status=status,
                message=message,
                details={'load_time_ms': load_time}
            )
            
        except Exception as e:
            return DeploymentCheck(
                check_type='performance',
                status='failed',
                message=f"Performance check failed: {str(e)}"
            )
    
    async def store_deployment_check_results(self, chatbot_id: str, domain: str, checks: List[DeploymentCheck]) -> bool:
        """Store deployment check results in database"""
        try:
            supabase = get_supabase_admin()
            
            # Store overall deployment check record
            deployment_check_data = {
                'chatbot_id': chatbot_id,
                'domain': domain,
                'total_checks': len(checks),
                'passed_checks': len([c for c in checks if c.status == 'passed']),
                'failed_checks': len([c for c in checks if c.status == 'failed']),
                'warning_checks': len([c for c in checks if c.status == 'warning']),
                'overall_status': self._determine_overall_status(checks),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Insert deployment check record
            check_response = supabase.table("deployment_checks").insert(deployment_check_data).execute()
            check_id = check_response.data[0]['id'] if check_response.data else None
            
            if check_id:
                # Store individual check results
                check_details = []
                for check in checks:
                    check_details.append({
                        'deployment_check_id': check_id,
                        'check_type': check.check_type,
                        'status': check.status,
                        'message': check.message,
                        'details': check.details or {},
                        'created_at': check.timestamp.isoformat()
                    })
                
                if check_details:
                    supabase.table("deployment_check_details").insert(check_details).execute()
            
            logger.info(f"Stored deployment check results for {chatbot_id} on {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing deployment check results: {e}")
            return False
    
    def _determine_overall_status(self, checks: List[DeploymentCheck]) -> str:
        """Determine overall status from individual checks"""
        if not checks:
            return 'unknown'
        
        failed_count = len([c for c in checks if c.status == 'failed'])
        warning_count = len([c for c in checks if c.status == 'warning'])
        
        if failed_count > 0:
            return 'failed'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'passed'
    
    async def get_deployment_history(self, chatbot_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get deployment check history for a chatbot"""
        try:
            supabase = get_supabase_admin()
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            response = supabase.table("deployment_checks").select("*").eq(
                "chatbot_id", chatbot_id
            ).gte("created_at", start_time.isoformat()).order("created_at", desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting deployment history: {e}")
            return []

# Global deployment service instance
deployment_service = DeploymentService()
