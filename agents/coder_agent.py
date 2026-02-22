import json
import os


# ── Templates ────────────────────────────────────────────────

PYTHON_WEB_DOCKERFILE = """\
FROM {base_image}

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt {gunicorn_line}

COPY . .

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}{health_path} || exit 1

CMD {cmd}
"""

NODE_DOCKERFILE = """\
FROM {base_image}

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY . .

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}{health_path} || exit 1

CMD {cmd}
"""

DOCKER_COMPOSE_BASE = """\
version: "3.9"
services:
  app:
    build: .
    ports:
      - "{external_port}:{port}"
    env_file:
      - .env
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "{cpu}"
          memory: {memory}
"""


# ─────────────────────────────────────────────────────────────

class ConfigurationGenerator:
    def generate(self, analysis: dict, recommendation: dict) -> dict:
        lang = analysis["language"]
        framework = analysis.get("framework", "unknown")
        port = analysis["port"]
        main_file = analysis["main_file"]
        base_image = recommendation.get("base_image", "python:3.11-slim" if lang == "python" else "node:20-alpine")
        cpu = recommendation.get("resources", {}).get("cpu", "0.5")
        memory = recommendation.get("resources", {}).get("memory", "1G")

        health_path = "/health" if framework in ("fastapi", "flask") else "/"

        gunicorn_line = ""
        cmd = ""

        if lang == "python":
            module_name = main_file.replace(".py", "")

            if framework == "streamlit":
                cmd = f'["streamlit", "run", "{main_file}", "--server.port={port}", "--server.address=0.0.0.0"]'
            elif framework in ("fastapi", "flask", "django"):
                gunicorn_line = "gunicorn"
                # Choose worker class BEFORE building the string
                worker_class = "uvicorn.workers.UvicornWorker" if framework == "fastapi" else "sync"
                cmd = (
                    f'["gunicorn", "{module_name}:app", '
                    f'"-w", "2", '
                    f'"-k", "{worker_class}", '
                    f'"--bind", "0.0.0.0:{port}"]'
                )
            else:
                # generic python script / worker / bot
                cmd = f'["python", "{main_file}"]'

        else:  # nodejs
            # Simple heuristic — prefer npm start if scripts exist, else direct node
            cmd = f'["npm", "start"]' if "scripts" in analysis else f'["node", "{main_file}"]'

        if lang == "python":
            dockerfile = PYTHON_WEB_DOCKERFILE.format(
                base_image=base_image,
                port=port,
                health_path=health_path,
                cmd=cmd,
                gunicorn_line=gunicorn_line
            )
        else:
            dockerfile = NODE_DOCKERFILE.format(
                base_image=base_image,
                port=port,
                health_path=health_path,
                cmd=cmd
            )

        docker_compose = DOCKER_COMPOSE_BASE.format(
            external_port=port,
            port=port,
            cpu=cpu,
            memory=memory
        )

        return {
            "dockerfile": dockerfile,
            "docker_compose": docker_compose,
            "metadata": {
                "framework": framework,
                "command_used": cmd,
                "health_path": health_path
            }
        }


def generate_configs(analysis_json: str, recommendation_json: str) -> str:
    """Module-level function called by the orchestrator. Returns JSON string."""
    analysis = json.loads(analysis_json)
    recommendation = json.loads(recommendation_json)
    result = ConfigurationGenerator().generate(analysis, recommendation)
    return json.dumps(result, indent=2)