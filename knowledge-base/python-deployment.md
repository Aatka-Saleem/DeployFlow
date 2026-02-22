# Python Deployment Patterns – DeployFlow Recommendations

## Recommended patterns by framework (2026)

1. FastAPI
   - Base image: python:3.11-slim or python:3.12-slim
   - Server: gunicorn + uvicorn.workers.UvicornWorker
   - Workers: 2–4 (scale with CPU)
   - CMD example:
     ["gunicorn", "main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

2. Flask
   - Same base image
   - gunicorn + sync workers (or gevent/eventlet for async)
   - CMD example:
     ["gunicorn", "app:app", "--workers", "4", "--bind", "0.0.0.0:5000"]

3. Django
   - Base image: python:3.11-slim
   - Collect static in Dockerfile or entrypoint.sh
   - Use whitenoise or dedicated nginx for static/media
   - CMD: gunicorn project.wsgi:application --workers 3 --bind 0.0.0.0:8000

4. Streamlit
   - Base image: python:3.11-slim
   - Install streamlit in requirements.txt
   - CMD: ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]

5. Celery / background workers
   - Separate service in docker-compose
   - CMD: ["celery", "-A", "tasks", "worker", "--loglevel=info"]
   - Use flower for monitoring (optional separate service)

## Common environment variables

- PYTHONUNBUFFERED=1
- PYTHONDONTWRITEBYTECODE=1
- PIP_NO_CACHE_DIR=1
- PORT (fallback 8000)
- DATABASE_URL / REDIS_URL
- SECRET_KEY (never hardcoded)
- DEBUG=false (production)