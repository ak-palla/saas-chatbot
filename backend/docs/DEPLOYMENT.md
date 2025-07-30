# Deployment Guide

Complete guide for deploying the Chatbot SaaS backend to production environments.

## 🎯 Production Checklist

Before deploying to production, ensure:

- [ ] All API keys are properly configured
- [ ] Database is set up and migrated
- [ ] FFmpeg is available on the server
- [ ] Environment variables are secured
- [ ] Rate limiting is configured
- [ ] Logging and monitoring are set up
- [ ] SSL/HTTPS is enabled
- [ ] CORS settings are properly configured

## 🚀 Deployment Options

### Option 1: Railway (Recommended)

Railway provides easy Python deployment with automatic builds.

#### Step 1: Prepare for Railway
1. **Create `railway.toml`:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

2. **Create `Procfile`:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. **Update `requirements.txt`** to include production dependencies:
```txt
# Add to your existing requirements.txt
gunicorn==21.2.0
uvicorn[standard]==0.24.0
```

#### Step 2: Deploy to Railway
1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Set environment variables in Railway dashboard:
   - Go to your project → Variables
   - Add all your `.env` variables

#### Step 3: Install FFmpeg on Railway
Add to your `nixpacks.toml`:
```toml
[phases.install]
nixPkgs = ["ffmpeg"]
```

### Option 2: Render

#### Step 1: Create `render.yaml`
```yaml
services:
  - type: web
    name: chatbot-saas-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: "/health"
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

#### Step 2: Deploy
1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically on git push

### Option 3: DigitalOcean App Platform

#### Step 1: Create `.do/app.yaml`
```yaml
name: chatbot-saas-backend
services:
- name: api
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  health_check:
    http_path: /health
  envs:
  - key: PYTHON_VERSION
    value: "3.11"
```

### Option 4: AWS EC2 with Docker

#### Step 1: Create `Dockerfile`
```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 2: Create `docker-compose.yml`
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
    env_file:
      - .env
    restart: unless-stopped
```

#### Step 3: Deploy to EC2
```bash
# On your EC2 instance
git clone your-repo
cd chatbot-saas-backend/backend
docker-compose up -d
```

## 🔧 Environment Configuration

### Production Environment Variables
```env
# Server Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services
GROQ_API_KEY=your_groq_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Security
SECRET_KEY=your_super_secure_secret_key_here
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
REDIS_URL=redis://your-redis-instance
RATE_LIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File Upload
MAX_FILE_SIZE=50MB
UPLOAD_DIR=/tmp/uploads

# Voice Features
AUDIO_MAX_DURATION=300
AUDIO_MAX_SIZE=100MB
```

### Securing Environment Variables

#### Railway
Set in Railway dashboard under Project → Variables

#### Render
Set in Render dashboard under Environment

#### Docker/EC2
Use Docker secrets or AWS Systems Manager Parameter Store:

```bash
# Using AWS Systems Manager
aws ssm put-parameter \
  --name "/chatbot-saas/groq-api-key" \
  --value "your-api-key" \
  --type "SecureString"
```

## 🗄️ Database Setup

### Production Database Migration
```bash
# Run on production server
python scripts/database/setup_database.py --environment=production
```

### Database Backup
Set up automated backups in Supabase:
1. Go to Supabase Dashboard → Settings → Database
2. Enable automated backups
3. Configure backup frequency and retention

## 🔒 Security Configuration

### 1. CORS Configuration
Update `app/core/config.py`:
```python
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com", 
    "https://admin.yourdomain.com"
]
```

### 2. Rate Limiting
Enable Redis-based rate limiting:
```python
# In app/core/config.py
REDIS_URL = os.getenv("REDIS_URL")
RATE_LIMIT_ENABLED = True
```

### 3. API Key Security
- Use separate API keys for production
- Rotate keys regularly
- Monitor API usage and quotas
- Set up alerts for unusual activity

### 4. File Upload Security
```python
# Restrict file types and sizes
ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx', '.wav', '.mp3']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

## 📊 Monitoring and Logging

### Application Monitoring
```python
# Add to requirements.txt
sentry-sdk[fastapi]==1.38.0
prometheus-client==0.19.0
```

### Sentry Integration
```python
# In app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### Health Checks
The `/health` endpoint provides comprehensive health monitoring:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "voice_services": "healthy",
    "file_storage": "healthy"
  },
  "metrics": {
    "active_sessions": 25,
    "requests_per_minute": 120,
    "average_response_time": 0.85
  }
}
```

## 🚀 Performance Optimization

### 1. Caching
Implement Redis caching for:
- Chatbot configurations
- Frequently accessed documents
- API responses

### 2. Database Optimization
- Index frequently queried fields
- Use connection pooling
- Implement query optimization

### 3. File Storage
- Use CDN for static assets
- Implement file compression
- Set up automatic cleanup of temporary files

### 4. Load Balancing
For high-traffic applications:
```yaml
# nginx.conf
upstream backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python scripts/dev-tools.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway deploy --token ${{ secrets.RAILWAY_TOKEN }}
```

## 📋 Post-Deployment Checklist

After successful deployment:

- [ ] Verify health check endpoint returns 200
- [ ] Test text chat functionality
- [ ] Test voice chat functionality
- [ ] Verify file upload works
- [ ] Check WebSocket connections
- [ ] Test rate limiting
- [ ] Verify logging is working
- [ ] Set up monitoring alerts
- [ ] Test backup/restore procedures
- [ ] Update DNS records
- [ ] Configure SSL certificates
- [ ] Test with production data

## 🆘 Troubleshooting

### Common Issues

**1. FFmpeg Not Found**
```bash
# On Ubuntu/Debian
apt-get update && apt-get install -y ffmpeg

# Using Docker
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg
```

**2. Memory Issues**
Increase server memory or optimize:
```python
# Reduce worker processes
uvicorn app.main:app --workers 2 --max-requests 1000
```

**3. Database Connection Issues**
- Check Supabase connection limits
- Implement connection pooling
- Verify network connectivity

**4. File Upload Failures**
- Check disk space
- Verify file permissions
- Review upload size limits

### Log Analysis
```bash
# View recent logs
tail -f /var/log/chatbot-saas/app.log

# Search for errors
grep -i error /var/log/chatbot-saas/app.log

# Monitor real-time
docker logs -f container_name
```

## 📞 Support

For deployment assistance:
1. Check server logs for detailed error messages
2. Verify all environment variables are set
3. Test individual components (database, APIs, FFmpeg)
4. Review the health check endpoint for service status

Your Chatbot SaaS backend is now ready for production deployment! 🚀