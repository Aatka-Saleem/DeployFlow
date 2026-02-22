import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class DeploymentArchitect:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.15,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a practical DevOps architect helping small edtech teams in Pakistan deploy on affordable infrastructure (VPS, shared hosting, Railway/Render/Fly.io style platforms).

Given this analysis of the codebase:
{analysis_json}

Recommend the **most appropriate, low-cost, low-maintenance** deployment strategy.

Common realistic options for Karachi edtech context:
- "docker-single-container"     → standard VPS (Hetzner, Contabo, DigitalOcean, local providers)
- "docker-compose-multi"        → when there are multiple services (app + redis + postgres)
- "railway/render/fly"          → PaaS with Git push → auto deploy (very popular among small teams)
- "vercel/netlify"              → for Next.js / React static + API
- "pythonanywhere / heroku-like" → very cheap but limited

Rules:
- Prefer simplest option that works reliably
- Never recommend AWS/GCP/Azure unless the analysis shows very large scale
- Always include base_image for container options (use slim/alpine variants)
- resources: realistic small VPS values (0.5–2 vCPU, 512M–4G RAM)
- Return **only** clean JSON. No markdown, no fences, no extra text.

Example output structure:
{
  "platform": "docker-single-container",
  "base_image": "python:3.11-slim",
  "resources": {"cpu": "1.0", "memory": "1G"},
  "notes": "Run on 2–4 USD/month VPS. Use coolify.io or caprover if self-hosting panel wanted.",
  "alternative": "railway"  // optional second-best choice
}
"""),
            ("human", "Analysis: {analysis_json}")
        ])

        self.chain = self.prompt | self.llm | JsonOutputParser()

    def recommend(self, analysis_json: str) -> dict:
        try:
            result = self.chain.invoke({"analysis_json": analysis_json})
            return result
        except Exception as e:
            return {
                "platform": "docker-single-container",
                "base_image": "python:3.11-slim",
                "resources": {"cpu": "0.5", "memory": "1G"},
                "notes": f"Error in architect recommendation: {str(e)}. Using safe fallback."
            }


def recommend_architecture(analysis_json: str) -> str:
    result = DeploymentArchitect().recommend(analysis_json)
    return json.dumps(result, indent=2)