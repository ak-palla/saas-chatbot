"""
CDN Service for Widget Asset Management
Handles CDN integration, caching strategies, and asset optimization
"""

import os
import hashlib
import json
import gzip
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class CDNService:
    """Service for managing CDN operations and asset optimization"""
    
    def __init__(self):
        self.s3_client = None
        self.cloudfront_client = None
        self.redis_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS and Redis clients"""
        try:
            # Initialize S3 client for asset storage
            if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
                )
                
                # Initialize CloudFront client for CDN management
                self.cloudfront_client = boto3.client(
                    'cloudfront',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
                )
            
            # Initialize Redis client for caching
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                
        except Exception as e:
            logger.warning(f"CDN service initialization warning: {e}")
    
    async def upload_widget_assets(self, assets: Dict[str, bytes]) -> Dict[str, str]:
        """
        Upload widget assets to CDN
        
        Args:
            assets: Dictionary of filename -> file content
            
        Returns:
            Dictionary of filename -> CDN URL
        """
        if not self.s3_client:
            logger.warning("S3 client not available, using local storage")
            return await self._upload_local_assets(assets)
        
        try:
            bucket_name = getattr(settings, 'CDN_BUCKET_NAME', 'chatbot-widget-assets')
            cdn_urls = {}
            
            for filename, content in assets.items():
                # Generate content hash for cache busting
                content_hash = hashlib.md5(content).hexdigest()[:8]
                s3_key = f"widgets/{content_hash}/{filename}"
                
                # Compress content if it's text-based
                if filename.endswith(('.js', '.css', '.html')):
                    content = gzip.compress(content)
                    content_encoding = 'gzip'
                else:
                    content_encoding = None
                
                # Upload to S3
                upload_params = {
                    'Bucket': bucket_name,
                    'Key': s3_key,
                    'Body': content,
                    'ContentType': self._get_content_type(filename),
                    'CacheControl': 'public, max-age=31536000',  # 1 year
                }
                
                if content_encoding:
                    upload_params['ContentEncoding'] = content_encoding
                
                self.s3_client.put_object(**upload_params)
                
                # Generate CDN URL
                cdn_domain = getattr(settings, 'CDN_DOMAIN', f"{bucket_name}.s3.amazonaws.com")
                cdn_urls[filename] = f"https://{cdn_domain}/{s3_key}"
                
                logger.info(f"Uploaded {filename} to CDN: {cdn_urls[filename]}")
            
            return cdn_urls
            
        except ClientError as e:
            logger.error(f"Error uploading to CDN: {e}")
            return await self._upload_local_assets(assets)
    
    async def _upload_local_assets(self, assets: Dict[str, bytes]) -> Dict[str, str]:
        """Fallback to local asset storage"""
        local_urls = {}
        asset_dir = "static/widget-assets"
        os.makedirs(asset_dir, exist_ok=True)
        
        for filename, content in assets.items():
            file_path = os.path.join(asset_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(content)
            
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            local_urls[filename] = f"{base_url}/{asset_dir}/{filename}"
        
        return local_urls
    
    def _get_content_type(self, filename: str) -> str:
        """Get appropriate content type for file"""
        content_types = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
        }
        
        ext = os.path.splitext(filename)[1].lower()
        return content_types.get(ext, 'application/octet-stream')
    
    async def invalidate_cache(self, paths: List[str]) -> bool:
        """
        Invalidate CDN cache for specific paths
        
        Args:
            paths: List of paths to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cloudfront_client:
            logger.warning("CloudFront client not available")
            return False
        
        try:
            distribution_id = getattr(settings, 'CLOUDFRONT_DISTRIBUTION_ID', None)
            if not distribution_id:
                logger.warning("CloudFront distribution ID not configured")
                return False
            
            response = self.cloudfront_client.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': str(datetime.utcnow().timestamp())
                }
            )
            
            logger.info(f"Created CloudFront invalidation: {response['Invalidation']['Id']}")
            return True
            
        except ClientError as e:
            logger.error(f"Error creating CloudFront invalidation: {e}")
            return False
    
    async def cache_widget_config(self, chatbot_id: str, config: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache widget configuration in Redis
        
        Args:
            chatbot_id: Chatbot ID
            config: Widget configuration
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = f"widget_config:{chatbot_id}"
            config_json = json.dumps(config, default=str)
            
            self.redis_client.setex(cache_key, ttl, config_json)
            logger.debug(f"Cached widget config for chatbot {chatbot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching widget config: {e}")
            return False
    
    async def get_cached_widget_config(self, chatbot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached widget configuration
        
        Args:
            chatbot_id: Chatbot ID
            
        Returns:
            Cached configuration or None
        """
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"widget_config:{chatbot_id}"
            cached_config = self.redis_client.get(cache_key)
            
            if cached_config:
                return json.loads(cached_config)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached widget config: {e}")
            return None
    
    async def optimize_widget_bundle(self, js_content: str, css_content: str) -> Dict[str, bytes]:
        """
        Optimize widget bundle for performance
        
        Args:
            js_content: JavaScript content
            css_content: CSS content
            
        Returns:
            Dictionary of optimized assets
        """
        optimized_assets = {}
        
        try:
            # Minify JavaScript (basic minification)
            minified_js = self._minify_js(js_content)
            optimized_assets['widget.min.js'] = minified_js.encode('utf-8')
            
            # Minify CSS
            minified_css = self._minify_css(css_content)
            optimized_assets['widget.min.css'] = minified_css.encode('utf-8')
            
            # Create combined bundle
            bundle_content = f"/* Widget Bundle - Generated {datetime.utcnow().isoformat()} */\n"
            bundle_content += f"/* CSS */\n{minified_css}\n"
            bundle_content += f"/* JavaScript */\n{minified_js}\n"
            optimized_assets['widget.bundle.js'] = bundle_content.encode('utf-8')
            
            logger.info("Widget bundle optimized successfully")
            return optimized_assets
            
        except Exception as e:
            logger.error(f"Error optimizing widget bundle: {e}")
            # Return original content if optimization fails
            return {
                'widget.js': js_content.encode('utf-8'),
                'widget.css': css_content.encode('utf-8')
            }
    
    def _minify_js(self, js_content: str) -> str:
        """Basic JavaScript minification"""
        # Remove comments
        lines = js_content.split('\n')
        minified_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                minified_lines.append(line)
        
        return ' '.join(minified_lines)
    
    def _minify_css(self, css_content: str) -> str:
        """Basic CSS minification"""
        # Remove comments and extra whitespace
        import re
        
        # Remove CSS comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        css_content = re.sub(r':\s*', ':', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        
        return css_content.strip()
    
    async def get_performance_metrics(self, chatbot_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get performance metrics for widget
        
        Args:
            chatbot_id: Chatbot ID
            days: Number of days to analyze
            
        Returns:
            Performance metrics
        """
        try:
            # This would typically query your analytics database
            # For now, return mock data structure
            return {
                'average_load_time': 450,  # ms
                'cache_hit_rate': 85.2,   # %
                'bandwidth_saved': 2.3,   # GB
                'requests_served': 15420,
                'error_rate': 0.1,        # %
                'uptime': 99.9,           # %
                'geographic_distribution': {
                    'US': 45.2,
                    'EU': 32.1,
                    'ASIA': 22.7
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

# Global CDN service instance
cdn_service = CDNService()
