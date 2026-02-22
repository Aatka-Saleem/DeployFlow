import re
import json


class RepositoryAnalyzer:
    def analyze_repository(self, repo_content: str) -> dict:
        content_lower = repo_content.lower()

        # ── Language ────────────────────────────────────────────────
        has_python = any(f in repo_content for f in ["requirements.txt", "setup.py", ".py", "pyproject.toml"])
        has_node   = any(f in repo_content for f in ["package.json", "yarn.lock", ".js", ".ts", ".jsx", ".tsx"])

        if has_python and not has_node:
            lang = "python"
        elif has_node and not has_python:
            lang = "nodejs"
        elif has_python and has_node:
            lang = "polyglot"
        else:
            lang = "unknown"

        # ── Framework ───────────────────────────────────────────────
        framework = "unknown"

        if lang == "python":
            scores = {"fastapi":0, "flask":0, "django":0, "streamlit":0}
            if "fastapi" in content_lower or "APIRouter" in repo_content: scores["fastapi"] += 10
            if "uvicorn" in content_lower: scores["fastapi"] += 8
            if "django" in content_lower or "manage.py" in repo_content: scores["django"] += 12
            if "flask" in content_lower or "@app.route" in repo_content: scores["flask"] += 10
            if "streamlit" in content_lower or "st.title" in repo_content: scores["streamlit"] += 15

            max_score = max(scores.values())
            if max_score >= 8:
                framework = max(scores, key=scores.get)
            else:
                framework = "generic-python"

        elif lang == "nodejs":
            if "next.config" in repo_content or "getServerSideProps" in repo_content:
                framework = "nextjs"
            elif "express" in content_lower:
                framework = "express"
            else:
                framework = "nodejs-generic"

        # ── Port ─────────────────────────────────────────────────────
        port = None
        port_patterns = [
            r"port\s*[=:]\s*(\d{2,5})",
            r"PORT\s*[=:]\s*(\d{2,5})",
            r"os\.environ\.get\(['\"]PORT['\"][^,]*,\s*(\d{2,5})",
            r"getenv\(['\"]PORT['\"][^,]*,\s*['\"](\d{2,5})['\"]\)",
            r"app\.run\([^)]*port\s*[=:]\s*(\d{2,5})",
        ]
        for pat in port_patterns:
            m = re.search(pat, content_lower)
            if m:
                port = int(m.group(1))
                break

        if port is None:
            if framework in ("fastapi", "django"):   port = 8000
            elif framework in ("flask",):            port = 5000
            elif framework == "streamlit":           port = 8501
            elif framework in ("nextjs", "express"): port = 3000
            else:                                    port = 8000

        if not (1 <= port <= 65535):
            port = 8000

        # ── Main file ────────────────────────────────────────────────
        if lang == "python":
            main_file = "app.py"
            candidates = ["streamlit_app.py","main.py", "app.py", "run.py", "manage.py", "wsgi.py", "asgi.py"]
            for c in candidates:
                if c in repo_content:
                    main_file = c
                    break
            if framework == "django" and "manage.py" in repo_content:
                main_file = "manage.py"
        else:
            main_file = "index.js"
            candidates = ["index.js", "server.js", "app.js", "index.ts", "main.js"]
            for c in candidates:
                if c in repo_content:
                    main_file = c
                    break

        # ── Result ───────────────────────────────────────────────────
        result = {
            "language": lang,
            "framework": framework,
            "port": port,
            "main_file": main_file,
            "package_manager": "pip" if "python" in lang else "npm",
            "app_type": (
                "web"       if framework in ("fastapi","flask","django","express","nextjs") else
                "streamlit" if framework == "streamlit" else
                "unknown"
            )
        }

        return result


def analyze_repository(repo_content: str) -> str:
    return json.dumps(RepositoryAnalyzer().analyze_repository(repo_content), indent=2)