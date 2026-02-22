import re
import json
from pathlib import Path
import yaml


class SecurityValidator:
    def __init__(self):
        self.rules_path = Path("security_rules/security_rules.yaml")
        self.rules = self._load_rules()

    def _load_rules(self):
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Security rules file not found: {self.rules_path}")
        with open(self.rules_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data["rules"]

    def validate(self, configs_json: str | dict) -> dict:
        if isinstance(configs_json, str):
            configs = json.loads(configs_json)
        else:
            configs = configs_json

        dockerfile = configs.get("dockerfile", "")
        docker_compose = configs.get("docker_compose", "")
        files = {"dockerfile": dockerfile, "docker-compose": docker_compose}

        issues = []

        for rule_id, rule in self.rules.items():
            severity = rule["severity"]
            rule_type = rule.get("type", "regex")

            if rule_type == "regex":
                patterns = rule.get("patterns", [])
                target_files = rule.get("files", ["dockerfile"])
                for fname in target_files:
                    content = files.get(fname, "")
                    for pattern in patterns:
                        for i, line in enumerate(content.splitlines(), 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    "rule": rule_id,
                                    "severity": severity,
                                    "message": rule["description"],
                                    "location": fname,
                                    "line": i,
                                    "matched": line.strip(),
                                    "fix": self._get_fix(rule_id)
                                })
                                break  # one hit per rule per file

            elif rule_type == "logic":
                check = rule.get("check")
                if check == "no_non_root_user":
                    if "USER " not in dockerfile or "USER root" in dockerfile or "USER 0" in dockerfile:
                        issues.append({
                            "rule": rule_id, "severity": severity,
                            "message": rule["description"], "location": "dockerfile",
                            "fix": self._get_fix(rule_id)
                        })
                elif check == "no_healthcheck":
                    if "HEALTHCHECK" not in dockerfile:
                        issues.append({
                            "rule": rule_id, "severity": severity,
                            "message": rule["description"], "location": "dockerfile",
                            "fix": self._get_fix(rule_id)
                        })

        # Count & decide status
        critical = sum(1 for i in issues if i["severity"] == "CRITICAL")
        high = sum(1 for i in issues if i["severity"] == "HIGH")

        if critical > 0:
            status = "BLOCKED"
        elif high > 0:
            status = "REVIEW_REQUIRED"
        else:
            status = "APPROVED"

        return {
            "status": status,
            "total_issues": len(issues),
            "critical": critical,
            "high": high,
            "medium": len(issues) - critical - high,
            "issues": issues,
            "compliance_score": round((1 - len(issues)/10) * 100, 1) if issues else 100.0,
            "recommendation": "Deployment ready for production" if status == "APPROVED" else "Fix issues before deploying"
        }

    def _get_fix(self, rule_id: str) -> str:
        fixes = {
            "SEC001": "Move secrets to .env / Docker Secrets / Railway variables. Never commit them.",
            "SEC002": "Add non-root user: RUN adduser --system appuser && USER appuser",
            "SEC003": "Pin version, e.g. python:3.11-slim or node:20-alpine",
            "SEC004": "Add HEALTHCHECK CMD curl -f http://localhost:PORT/health || exit 1",
            "SEC005": "Do not expose DB/Redis ports publicly. Use internal networks only.",
            "SEC006": "Remove privileged: true and cap_add. Never needed for web apps.",
            "SEC007": "Create .dockerignore file (exclude .git, __pycache__, .env, etc.)",
            "SEC008": "Replace ADD with COPY for better layer caching and security.",
        }
        return fixes.get(rule_id, "Review and apply the recommended fix.")


def validate_configs(configs_json: str) -> str:
    """Module-level function called by orchestrator"""
    result = SecurityValidator().validate(configs_json)
    return json.dumps(result, indent=2)