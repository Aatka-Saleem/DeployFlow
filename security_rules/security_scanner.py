import re
import yaml
import os
from typing import List, Dict, Tuple


class SecurityScanner:
    """
    Loads rules from security_rules.yaml and scans Dockerfiles.
    Severity scoring: CRITICAL=30pts, HIGH=20pts, MEDIUM=10pts
    """

    SEVERITY_SCORES = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10}

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict]:
        rules_path = os.path.join(os.path.dirname(__file__), "security_rules.yaml")
        try:
            with open(rules_path, "r") as f:
                data = yaml.safe_load(f)
            return data.get("security_rules", [])
        except FileNotFoundError:
            # Fallback: inline rules if YAML file is missing
            return [
                {
                    "rule_id": "SEC001",
                    "severity": "CRITICAL",
                    "pattern": r'(?i)(PASSWORD|API_KEY|SECRET|TOKEN)\s*=\s*[\'"]?[a-zA-Z0-9_\-]{4,}',
                    "message": "Hardcoded secrets found. Use environment variables.",
                    "fix_suggestion": "Pass secrets via environment variables at runtime.",
                },
                {
                    "rule_id": "SEC002",
                    "severity": "CRITICAL",
                    "check": "missing_nonroot_user",
                    "message": "Container should not run as root.",
                    "fix_suggestion": "Add a non-root USER instruction before CMD.",
                },
            ]

    def scan_dockerfile(self, content: str) -> Tuple[List[Dict], int]:
        """
        Scans Dockerfile content against all loaded rules.
        Returns (issues list, risk score 0-100).
        """
        issues = []
        score = 0

        for rule in self.rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            severity = rule.get("severity", "MEDIUM")
            message = rule.get("message", "Security issue detected.")
            fix = rule.get("fix_suggestion", "Review and fix this issue.")
            check = rule.get("check")
            pattern = rule.get("pattern")

            triggered = False
            line_number = None

            # --- Logic-based checks ---
            if check == "missing_nonroot_user":
                # Triggered if no USER instruction at all, or only USER root
                has_nonroot = re.search(r'^\s*USER\s+(?!root\s*$)\w+', content, re.MULTILINE)
                if not has_nonroot:
                    triggered = True

            elif check == "missing_healthcheck":
                if "HEALTHCHECK" not in content:
                    triggered = True

            # --- Pattern-based checks ---
            elif pattern:
                for i, line in enumerate(content.splitlines(), start=1):
                    if re.search(pattern, line, re.IGNORECASE):
                        triggered = True
                        line_number = i
                        break

            if triggered:
                issue = {
                    "rule_id": rule_id,
                    "severity": severity,
                    "message": message,
                    "fix": fix,
                }
                if line_number:
                    issue["line"] = line_number
                issues.append(issue)
                score += self.SEVERITY_SCORES.get(severity, 10)

        # Cap score at 100
        score = min(score, 100)
        return issues, score

    def generate_report(self, issues: List[Dict], score: int) -> str:
        """Returns a human-readable security report string."""
        if not issues:
            return "✅ All security checks passed. Safe to deploy."

        lines = [f"⚠️  Risk Score: {score}/100\n"]
        for issue in issues:
            icon = "🚨" if issue["severity"] == "CRITICAL" else ("⚠️" if issue["severity"] == "HIGH" else "💡")
            line_info = f" (line {issue['line']})" if issue.get("line") else ""
            lines.append(f"{icon} [{issue['severity']}] {issue['rule_id']}{line_info}: {issue['message']}")
            lines.append(f"   Fix → {issue['fix']}")
            lines.append("")

        return "\n".join(lines)

    def get_status(self, issues: List[Dict]) -> str:
        """Returns BLOCKED / REVIEW_REQUIRED / APPROVED based on issue severities."""
        severities = {i["severity"] for i in issues}
        if "CRITICAL" in severities:
            return "BLOCKED"
        if "HIGH" in severities:
            return "REVIEW_REQUIRED"
        return "APPROVED"