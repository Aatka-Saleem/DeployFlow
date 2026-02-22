import os
import json
from dotenv import load_dotenv

# Import local agent tools
from analyst_agent import analyze_repository
from architect_agent import recommend_architecture
from coder_agent import generate_configs
from security_agent import validate_configs

load_dotenv()


class DeployFlowOrchestrator:
    def run_workflow(self, repo_content: str) -> dict:
        print("🚀 Starting DeployFlow Workflow...")

        # STEP 1 — Analyst Agent (logic-based)
        # Detects language, framework, port, and main file.
        analysis_json = analyze_repository(repo_content=repo_content)
        analysis = json.loads(analysis_json)
        print(f"✅ Analysis: {analysis['language']} / {analysis['framework']} on port {analysis['port']}")

        # STEP 2 — Architect Agent (LLM-powered via Groq)
        # Recommends base image, resource limits, and VPS strategy.
        recommendation_json = recommend_architecture(analysis_json)
        recommendations = json.loads(recommendation_json)
        print(f"✅ Architecture: {recommendations.get('platform', 'docker-vps')} | base: {recommendations.get('base_image')}")

        # STEP 3 — Coder Agent (template-based)
        # Generates Dockerfile + docker-compose.yml from templates.
        configs_json = generate_configs(analysis_json, recommendation_json)
        configs = json.loads(configs_json)
        print("✅ Configs generated: Dockerfile + docker-compose.yml")

        # Inside run_workflow method — replace the security part:

        # STEP 4 — Security Agent (now much stronger)
        try:
            security_json = validate_configs(configs_json)
            security = json.loads(security_json)
            print(f"✅ Security Scan: {security['status']} | {security['total_issues']} issues | Score: {security.get('compliance_score', 0)}%")
        except Exception as e:
            security = {"status": "ERROR", "total_issues": 1, "issues": [{"message": f"Security scanner failed: {e}"}]}
            print("❌ Security scan crashed — treated as BLOCKED")

        if security["status"] in ("BLOCKED", "ERROR"):
            print("🚨 DEPLOYMENT BLOCKED — Critical security issues found:")
            for issue in security.get("issues", []):
                print(f"   [{issue.get('severity', 'CRITICAL')}] {issue.get('rule')} → {issue.get('message')}")
                print(f"   Fix: {issue.get('fix', 'See report')}\n")

        return {
            "analysis": analysis,
            "architecture": recommendations,
            "files": configs,
            "security": security,
            "report_summary": f"""
            # DeployFlow Report
            **Status**: {security['status']}
            **Security Score**: {security.get('compliance_score', 0)}%
            **Platform**: {recommendations.get('platform')}
            **Base Image**: {recommendations.get('base_image')}
            **Generated**: {len(configs.get('dockerfile', '').splitlines())} lines Dockerfile + docker-compose.yml
                        """.strip()
        }




if __name__ == "__main__":
    orchestrator = DeployFlowOrchestrator()
    test_repo = "requirements.txt: flask==2.3.0\napp.py: from flask import Flask\napp.run(port=5000)"
    results = orchestrator.run_workflow(test_repo)
    print("\n--- Security Report ---")
    print(json.dumps(results["security"], indent=2))
    print("\n--- Generated Dockerfile ---")
    print(results["files"]["dockerfile"])