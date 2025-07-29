import time
from fastapi import FastAPI, Request
from app.core.config import settings

# Try to initialize rate limiter, fall back to memory if Redis unavailable
try:
    import redis
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    # Test Redis connection
    redis_url = settings.REDIS_URL
    
    # Handle cloud Redis URL format
    if not redis_url.startswith(('redis://', 'rediss://')):
        redis_url = f"redis://{redis_url}"
    
    redis_client = redis.from_url(redis_url, decode_responses=True)
    redis_client.ping()
    
    # Create rate limiter with Redis
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=redis_url,
    )
    RATE_LIMITING_ENABLED = True
except Exception as e:
    print(f"Redis not available, rate limiting disabled: {e}")
    limiter = None
    RATE_LIMITING_ENABLED = False


def setup_middleware(app: FastAPI):
    # Add rate limiting if available
    if RATE_LIMITING_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Add logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        # Log request details here if needed
        response = await call_next(request)
        return response