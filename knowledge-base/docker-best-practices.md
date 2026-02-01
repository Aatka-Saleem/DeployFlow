# Docker Best Practices

## Image Optimization

### Use Specific Base Image Tags
❌ **Bad**: `FROM python:latest`
✅ **Good**: `FROM python:3.11-slim`

**Why**: Ensures reproducible builds and smaller image size.

### Multi-Stage Builds
Use multi-stage builds to reduce final image size:
```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

### Layer Caching
Order instructions from least to most frequently changed:
```dockerfile
# 1. Base image (rarely changes)
FROM python:3.11-slim

# 2. System dependencies (rarely change)
RUN apt-get update && apt-get install -y curl

# 3. Application dependencies (change occasionally)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. Application code (changes frequently)
COPY . .
```

## Security Best Practices

### Don't Run as Root
```dockerfile
RUN useradd -m appuser
USER appuser
```

### Don't Include Secrets
❌ **Never**: `ENV API_KEY=secret123`
✅ **Use**: Environment variables at runtime or secrets management

### Minimize Attack Surface
```dockerfile
# Remove unnecessary packages
RUN apt-get update && apt-get install -y \
    required-package \
    && rm -rf /var/lib/apt/lists/*
```

### Scan for Vulnerabilities
- Use `docker scan` or IBM Cloud Container Registry scanning
- Keep base images updated
- Monitor for CVEs

## Size Optimization

### Use Alpine Images When Possible
```dockerfile
FROM python:3.11-alpine  # ~50MB
# vs
FROM python:3.11         # ~900MB
```

### Use .dockerignore
```
node_modules
.git
.env
*.log
test/
```

### Combine RUN Commands
❌ **Bad**: 
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean
```

✅ **Good**:
```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

## Health Checks

### Add Health Check Endpoints
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8080/health || exit 1
```

## Port Configuration

### Standard Ports by Framework
- Python Flask/Django: 8080 or 5000
- Node.js Express: 3000
- Java Spring Boot: 8080
- Go: 8080

### Use ARG for Flexibility
```dockerfile
ARG PORT=8080
EXPOSE ${PORT}
ENV PORT=${PORT}
```

## Logging

### Log to STDOUT/STDERR
```dockerfile
ENV PYTHONUNBUFFERED=1
```

### Don't Write Logs to Files in Container
Containers are ephemeral - use stdout and let orchestration handle logging.

## IBM Cloud Specific

### Use IBM Container Registry
- Automatic vulnerability scanning
- Regional registries for faster pulls
- Integration with IBM Cloud services

### Optimize for Code Engine
- Keep images under 1GB when possible
- Use health checks
- Set resource limits appropriately
