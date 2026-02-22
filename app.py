# app.py
import streamlit as st
import json
import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Import your agents (adjust paths if needed)
from agents.analyst_agent import analyze_repository
from agents.architect_agent import recommend_architecture
from agents.coder_agent import generate_configs
# from security_rules.security_scanner import SecurityScanner  # ← assuming this is the updated one
from agents.security_agent import validate_configs
load_dotenv()

# ────────────────────────────────────────────────
# Page config & theme
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="DeployFlow — Karachi EdTech DevOps",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-org/deployflow/issues',
        'Report a bug': "https://github.com/your-org/deployflow/issues",
        'About': "DeployFlow v1.0 • Intelligent Docker deployment for small EdTech teams"
    }
)

# Custom CSS for better Karachi/edtech branding feel (optional)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f4f8, #e0e7ff); }
    .stButton>button { background-color: #4f46e5; color: white; border-radius: 8px; }
    .stSuccess { background-color: #d1fae5; border-left: 6px solid #10b981; }
    .stError   { background-color: #fee2e2; border-left: 6px solid #ef4444; }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Sidebar – Controls & Info
# ────────────────────────────────────────────────
with st.sidebar:
    st.header("🚀 DeployFlow")
    st.caption("Fast, secure Docker setups for Karachi EdTech startups")
    
    st.markdown("---")
    input_mode = st.radio("Input method", ["Paste repo content", "Upload files (coming soon)"], index=0)
    
    st.markdown("---")
    st.info("**Supported stacks (2026)**\n• Python: FastAPI, Flask, Django, Streamlit\n• Node.js: Express, Next.js")
    st.caption("Paste a simulation of your repo structure & key files (requirements.txt, app.py, package.json, etc.)")

# ────────────────────────────────────────────────
# Main content
# ────────────────────────────────────────────────
st.title("Generate Production-Ready Docker Deployment")
st.markdown("Paste your repository files/content below → get Dockerfile, docker-compose.yml + security report in seconds.")

# ── Input area ───────────────────────────────────────
if input_mode == "Paste repo content":
    repo_input = st.text_area(
        "Repository snapshot (file names + content)",
        height=240,
        placeholder="Example:\nrequirements.txt: fastapi==0.115.0\nuvicorn==0.32.0\n\nmain.py:\nfrom fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root(): return {'msg': 'hello'}",
        help="Include file names followed by : and content. One file per block. Focus on key files."
    )
else:
    repo_input = ""
    st.warning("File upload mode coming soon — drag & drop multiple files or zip archive")

# ── Run button + spinner ─────────────────────────────
if st.button("✨ Analyze & Generate Package", type="primary", use_container_width=True, disabled=not repo_input.strip()):
    if not repo_input.strip():
        st.error("Please provide some repository content.")
        st.stop()

    with st.spinner("DeployFlow agents at work... (Analyst → Architect → Coder → Security)"):
        try:
            # Step 1: Analyst
            analysis_json = analyze_repository(repo_content=repo_input)
            analysis = json.loads(analysis_json)

            # Step 2: Architect
            arch_json = recommend_architecture(analysis_json)
            arch = json.loads(arch_json)

            # Step 3: Coder
            configs_json = generate_configs(analysis_json, arch_json)
            configs = json.loads(configs_json)

            # Inside the try block, replace the scanner lines with:

            security_json = validate_configs(json.dumps(configs))
            security_result = json.loads(security_json)

            status = security_result.get("status", "UNKNOWN")
            score = security_result.get("compliance_score", 0.0)
            issues = security_result.get("issues", [])

            # Step 4: Security (using your updated scanner)
            
            # scanner = SecurityScanner()
            # # Assuming your scanner now accepts both dockerfile & docker_compose
            # security_result = json.loads(scanner.validate(json.dumps(configs)))  # ← updated call

            # status = security_result.get("status", "UNKNOWN")
            # issues = security_result.get("issues", [])
            # score = security_result.get("compliance_score", 0)

            # ── Results layout ───────────────────────────────────
            st.markdown("---")
            cols = st.columns([2, 1])

            with cols[0]:
                st.subheader("Deployment Summary")
                c1, c2, c3 = st.columns(3)
                c1.metric("Language", analysis.get("language", "?").upper())
                c2.metric("Framework", analysis.get("framework", "?").title())
                c3.metric("Port", f"{analysis.get('port', '?')}")

                st.markdown(f"**Platform**: {arch.get('platform', 'docker-single-container')}")
                st.markdown(f"**Base image**: `{arch.get('base_image', 'n/a')}`")
                st.markdown(f"**Resources**: {arch.get('resources', {})}")

            with cols[1]:
                if status == "APPROVED":
                    st.success(f"✅ Approved\nSecurity Score: **{score:.1f}%**")
                elif status == "REVIEW_REQUIRED":
                    st.warning(f"⚠️ Review needed\nSecurity Score: **{score:.1f}%**")
                else:
                    st.error(f"🚫 Blocked\nSecurity Score: **{score:.1f}%**")

                if score < 100:
                    with st.expander("Security Issues", expanded=score < 90):
                        if issues:
                            for issue in issues:
                                sev = issue.get("severity", "UNKNOWN")
                                color = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "blue"}.get(sev, "grey")
                                st.markdown(f"**[{sev}]** {issue.get('message')}  \n{issue.get('fix', '')}", unsafe_allow_html=True)
                        else:
                            st.info("No issues detected")

            # ── Code display ─────────────────────────────────────
            tab1, tab2 = st.tabs(["Dockerfile", "docker-compose.yml"])

            with tab1:
                st.code(configs.get("dockerfile", "# No Dockerfile generated"), language="dockerfile", line_numbers=True)

            with tab2:
                st.code(configs.get("docker_compose", "# No compose file generated"), language="yaml", line_numbers=True)

            # ── Download buttons ─────────────────────────────────
            st.download_button(
                label="📥 Download Dockerfile",
                data=configs.get("dockerfile", ""),
                file_name="Dockerfile",
                mime="text/plain",
                use_container_width=True
            )

            st.download_button(
                label="📥 Download docker-compose.yml",
                data=configs.get("docker_compose", ""),
                file_name="docker-compose.yml",
                mime="text/yaml"
            )

        except json.JSONDecodeError as e:
            st.error(f"JSON parsing failed in agent output:\n{str(e)}")
        except Exception as e:
            st.error("Unexpected error during generation")
            with st.expander("Details (for debugging)"):
                st.code(traceback.format_exc(), language="python")

# ── Footer / Help ────────────────────────────────────────
st.markdown("---")
st.caption("DeployFlow • Built for Karachi EdTech teams • Powered by Groq + LangChain • v1.0 (Feb 2026)")