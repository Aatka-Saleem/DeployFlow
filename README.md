# DeployFlow – AI-Powered Zero-DevOps Deployment for EdTech Teams

**DeployFlow** is a generative AI tool that automatically analyzes a code repository and generates secure, production-ready **Dockerfile** + **docker-compose.yml** files in seconds — enabling small edtech teams in Pakistan to deploy reliable web applications without hiring a DevOps engineer.

Built for the **HEC Generative AI Training Cohort 2 Hackathon** — Powered by Aspire Pakistan  
February 2026
)

## 🎯 The Problem

Small edtech startups and university labs in Karachi often:
- Cannot afford full-time DevOps engineers
- Rely on fragile manual Docker setups
- Face downtime during exams, fee collection, or high-traffic periods
- Risk security issues with student data

DeployFlow removes the infrastructure barrier so teams can focus on teaching, learning, and student experience.

## ✨ What DeployFlow Does

Paste your repo content (requirements.txt + main files) → get instantly:

- Language & framework detection (Streamlit, FastAPI, Flask, basic Node)
- Production-grade Dockerfile
  - Non-root user
  - HEALTHCHECK
  - Pinned base images
  - Gunicorn + Uvicorn for FastAPI
  - Native Streamlit run command
- Simple docker-compose.yml with resource limits
- Basic security scan (no secrets, no root, no :latest)

## 🛠️ How Generative AI is Used

The **Architect Agent** uses **Groq** (Llama-3.3-70B) to intelligently recommend:
- Suitable base image
- CPU/memory limits for low-cost VPS
- Deployment strategy notes

All other steps (analysis, code generation, security) are fast rule-based / template-based to stay within free-tier limits and keep latency low.

## 🚀 Quick Start (Local)

```bash
# Clone repo
git clone https://github.com/Aatka-Saleem/DeployFlow.git
cd DeployFlow

# Virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# or source venv/bin/activate  # Linux/Mac

# Install
pip install -r requirements.txt

# Add Groq key
echo GROQ_API_KEY=your_key_here > .env

# Run
streamlit run app.py

Open http://localhost:8501

Live Demo
Public demo: https://aatka-saleem-deployflow-app-wk1e8z.streamlit.app/

Tech Stack

UI — Streamlit
Agents — Python + LangChain-Groq
LLM — Groq (llama-3.3-70b-versatile)
Security — Custom rule-based scanner
Output — Docker + docker-compose

Hackathon Details

Category: Education + Automation
Team: Aatka (lead) 
Why this matters in Pakistan: Lowers infrastructure cost & complexity for edtech products serving schools, students, and parents across Karachi and beyond.

Limitations & Next Steps

Currently paste-based (GitHub URL fetch planned)
Single-container only (multi-service later)
Basic security rules (expandable with more patterns)

Made for
HEC Generative AI Training Cohort 2
Powered by Aspire Pakistan
February 2026

Built with ❤️ in Karachi to help local edtech teams scale confidently.
