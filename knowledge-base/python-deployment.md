# Python Application Deployment Guide

## Overview
Best practices for deploying Python applications using containers and IBM Cloud.

## Recommended Dockerfile Structure

### For Web Applications (Flask/Django/FastAPI)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Use production server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "2", "app:app"]
```

### For ML/Data Science Applications
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["python", "main.py"]
```

## Resource Recommendations

### Small Python Web App
- **CPU**: 0.5 vCPU
- **Memory**: 512MB
- **Replicas**: 2
- **Auto-scaling**: 2-5 pods

### Python ML Application
- **CPU**: 1-2 vCPU
- **Memory**: 2GB - 4GB
- **Replicas**: 1-3
- **GPU**: Optional for inference

### Python API Server
- **CPU**: 1 vCPU
- **Memory**: 1GB
- **Replicas**: 3
- **Auto-scaling**: 3-10 pods

## Common Dependencies
- **Flask**: Use gunicorn (production server)
- **Django**: Use gunicorn or uwsgi
- **FastAPI**: Use uvicorn workers
- **NumPy/Pandas**: May need more memory
- **TensorFlow/PyTorch**: Likely needs GPU

## Environment Variables
- `PORT`: Application port (default 8080)
- `WORKERS`: Number of worker processes (default 2)
- `PYTHONUNBUFFERED`: Set to 1 for logging
- `LOG_LEVEL`: INFO or DEBUG

## IBM Code Engine Settings
- Use Python buildpack auto-detection
- Set min instances to 0 for cost savings
- Enable auto-scaling based on CPU/requests
- Use secrets for sensitive configuration
