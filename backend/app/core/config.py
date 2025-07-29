from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Chatbot SaaS Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # AI Services
    GROQ_API_KEY: str
    DEEPGRAM_API_KEY: str
    OPENAI_API_KEY: str = ""  # Optional, deprecated in favor of HF
    HUGGINGFACE_API_TOKEN: str = ""  # Hugging Face API token
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Stripe
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Drive (optional)
    GOOGLE_DRIVE_CREDENTIALS_PATH: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = ""  # Optional: specific folder for uploads
    
    model_config = {"env_file": ".env"}


settings = Settings()