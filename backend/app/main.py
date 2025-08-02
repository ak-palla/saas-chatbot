from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.middleware import setup_middleware

import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Chatbot SaaS Platform API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Security middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# Add trusted host middleware for production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[host.replace("http://", "").replace("https://", "").split(":")[0] for host in settings.ALLOWED_HOSTS]
    )

setup_middleware(app)

app.include_router(api_router, prefix=settings.API_V1_STR)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = JsonFormatter()
ch.setFormatter(formatter)
logger.addHandler(ch)





@app.get("/")
async def root():
    logger.info("🌟 Root endpoint accessed")
    return {
        "message": "Chatbot SaaS Platform API", 
        "version": settings.VERSION,
        "status": "operational"
    }


from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse


@app.get("/health")
async def health_check():
    try:
        return {"status": "ok", "message": "Service is healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},)
