# Deployment Guide

This guide covers deploying the FastAPI backend to production.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload
```

## Production Deployment

### Option 1: Using Gunicorn (Linux/macOS)

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t fastapi-translate .
docker run -p 8000:8000 fastapi-translate
```

### Option 3: Cloud Deployment (Heroku, Railway, Render)

1. Push to GitHub
2. Connect repository to deployment platform
3. Set environment variables
4. Deploy

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Performance Optimization

1. **Enable CORS selectively** - Don't use `["*"]` in production
2. **Add rate limiting** - Prevent abuse
3. **Use HTTPS** - Enable SSL/TLS
4. **Monitor logs** - Set up logging infrastructure

## Health Monitoring

Check server health:
```bash
curl http://localhost:8000/health
```

## Scaling

For high traffic:
- Use multiple workers with Gunicorn
- Deploy behind a reverse proxy (Nginx)
- Use load balancing
- Cache responses where possible

## Database (if needed)

If you add a database:
- Use connection pooling
- Run migrations on deployment
- Backup data regularly

## SSL/TLS Certificates

For HTTPS:
```bash
# Using Certbot with Let's Encrypt
certbot certonly --standalone -d yourdomain.com
```

## Troubleshooting

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

**Module not found:**
```bash
# Verify virtual environment is activated
which python  # Should show venv path
```

**Model download issues:**
- Ensure internet connection
- Check disk space
- Increase timeout for large models
