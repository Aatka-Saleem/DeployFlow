# Docker Best Practices – DeployFlow Edition (Karachi EdTech Context 2026)

## Core Principles

1. Use small, official base images (alpine/slim variants)
   - python:3.11-slim / python:3.12-slim-bookworm
   - node:20-alpine / node:22-alpine
   - Avoid :latest – always pin versions

2. Never run as root
   - Create non-root user + group in every image
   - USER appuser (or similar) before CMD/ENTRYPOINT

3. Multi-stage builds when appropriate
   Especially useful for:
   - Node/React/Next.js frontend → copy only /app/.next or /app/build
   - Python with heavy build deps (numpy/pandas/scipy) → separate build & runtime stage

4. Minimize layers & image size
   - Combine RUN commands when possible
   - Use --no-cache-dir for pip
   - Use npm ci --only=production
   - COPY only what's needed (.dockerignore is mandatory)

5. Security defaults
   - No hardcoded secrets (ENV only for defaults)
   - HEALTHCHECK mandatory for web services
   - No unnecessary EXPOSE (only the actual app port)
   - No privileged containers

6. Health & readiness
   - HEALTHCHECK interval 20–30s, start-period 5–10s
   - Prefer /health or /healthz endpoint if available

## EdTech-specific recommendations

- Streamlit apps
  - streamlit run --server.port=$PORT --server.address=0.0.0.0
  - Expose 8501 internally, map externally if needed

- FastAPI / Uvicorn
  - Prefer gunicorn + uvicorn workers on production (2–4 workers)
  - --preload if using large models

- Django
  - Use gunicorn + whitenoise for static files
  - Collectstatic in Dockerfile or entrypoint

- Next.js
  - Build → output standalone or .next
  - Can run with node server.js or next start
  - Consider static export + nginx when no dynamic API needed

- Exam / high-concurrency periods
  - Use connection pooling (PgBouncer, Redis)
  - Rate limiting / caching layer (Redis/memcached)
  - Read replicas when possible

- Fee collection / payment gateways
  - Never log full card / transaction data
  - Use webhooks + background tasks (celery / dramatiq / rq)

## Common .dockerignore content

.git
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
*.env*
*.log
node_modules
npm-debug.log
.next/cache