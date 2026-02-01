"""
DeployFlow - Professional AI DevOps Automation
Clean, minimal interface for hackathon demo
"""

import streamlit as st
import json
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from agents.orchestrator_agent import DeployFlowOrchestrator

# Page configuration
st.set_page_config(
    page_title="DeployFlow",
    page_icon="🚀",
    layout="centered"
)

# Custom CSS - Clean and professional
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066cc;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0052a3 0%, #003d7a 100%);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Header
st.markdown('<div class="main-title">🚀 DeployFlow</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered DevOps Configuration Generator</div>', unsafe_allow_html=True)

# Simple input section
st.markdown("### Repository Information")

# Input method selection
input_method = st.radio(
    "Choose input method:",
    ["📝 Manual Description", "🔗 GitHub URL"],
    horizontal=True
)

# Quick examples in expander
with st.expander("💡 Click here for example inputs"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Flask API Example"):
            st.session_state.example = "flask"
    with col2:
        if st.button("Express.js Example"):
            st.session_state.example = "express"

if input_method == "📝 Manual Description":
    # Main input
    repo_description = st.text_area(
        "Describe your application:",
        value="""Language: Python 3.11
Framework: Flask
Database: PostgreSQL

Dependencies:
flask==2.3.0
gunicorn==20.1.0
psycopg2-binary==2.9.5

Files: app.py, requirements.txt""" if 'example' not in st.session_state or st.session_state.get('example') == 'flask' else """Language: Node.js 18
Framework: Express
Database: MongoDB

Dependencies:
express
mongoose
dotenv

Files: server.js, package.json""",
        height=200,
        help="Paste your requirements.txt or package.json, or describe your app"
    )
else:  # GitHub URL
    github_url = st.text_input(
        "GitHub Repository URL:",
        placeholder="https://github.com/username/repository",
        help="Enter a public GitHub repository URL"
    )
    
    fetch_option = st.checkbox(
        "🌐 Fetch repository data automatically (requires internet)",
        value=False,
        help="Check this to automatically fetch repo data from GitHub API"
    )
    
    if not fetch_option:
        st.info("💡 **Tip:** Uncheck the box above and describe your repository manually below for faster results")
        repo_description = st.text_area(
            "Describe your repository:",
            value="""Language: Python 3.11
Framework: Flask
Database: PostgreSQL

Dependencies (from requirements.txt):
flask==2.3.0
gunicorn==20.1.0
psycopg2-binary==2.9.5

Main file: app.py""",
            height=180,
            help="Describe what's in your GitHub repository"
        )
    else:
        repo_description = github_url  # Will be processed by GitHub fetcher

# Generate button
if st.button("🚀 Generate Deployment Configs"):
    
    # Handle GitHub URL fetching if selected
    if input_method == "🔗 GitHub URL" and fetch_option:
        with st.spinner('📡 Fetching repository data from GitHub...'):
            try:
                from github_fetcher import GitHubFetcher
                fetcher = GitHubFetcher()
                repo_description = fetcher.analyze_repository(github_url)
                
                if repo_description.startswith('Error'):
                    st.error(repo_description)
                    st.info("💡 **Tip:** Uncheck 'Fetch automatically' and describe your repository manually instead")
                    st.stop()
                else:
                    st.success("✅ Successfully fetched repository data from GitHub!")
            except Exception as e:
                st.error(f"❌ Could not fetch from GitHub: {str(e)}")
                st.info("💡 **Tip:** Describe your repository manually instead")
                st.stop()
    
    with st.spinner('🤖 AI Agents working...'):
        try:
            orchestrator = DeployFlowOrchestrator()
            result_json = orchestrator.orchestrate_deployment(repo_description)
            result = json.loads(result_json)
            st.session_state.results = result
            st.session_state.orchestrator = orchestrator
            st.success("✅ Generated successfully!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results (simplified)
if st.session_state.results:
    result = st.session_state.results
    
    st.markdown("---")
    
    # Quick summary
    st.markdown("### 📊 Summary")
    summary = result.get('summary', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Tech Stack:** {summary.get('detected_stack', 'N/A')}")
        st.markdown(f"**Platform:** {summary.get('deployment_platform', 'N/A')}")
    with col2:
        st.markdown(f"**Resources:** {summary.get('resources', 'N/A')}")
        status = summary.get('security_status', 'UNKNOWN')
        color = "🟢" if status == "APPROVED" else "🟡" if status == "REVIEW_REQUIRED" else "🔴"
        st.markdown(f"**Security:** {color} {status}")
    
    # Generated files with download buttons
    st.markdown("### 📥 Download Generated Files")
    
    files = result.get('generated_files', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📄 Dockerfile",
            files.get('dockerfile', ''),
            file_name="Dockerfile",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            "📄 Kubernetes",
            files.get('kubernetes', ''),
            file_name="deployment.yaml",
            mime="text/yaml",
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            "📄 CI/CD Pipeline",
            files.get('cicd', ''),
            file_name="deploy.yml",
            mime="text/yaml",
            use_container_width=True
        )
    
    # Details in expander
    with st.expander("🔍 View File Contents"):
        tab1, tab2, tab3 = st.tabs(["Dockerfile", "Kubernetes", "CI/CD"])
        
        with tab1:
            st.code(files.get('dockerfile', ''), language='dockerfile')
        
        with tab2:
            st.code(files.get('kubernetes', ''), language='yaml')
        
        with tab3:
            st.code(files.get('cicd', ''), language='yaml')
    
    # Security details in expander
    with st.expander("🔒 Security Validation Details"):
        security = result.get('security_validation', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Critical", security.get('critical', 0))
        with col2:
            st.metric("High", security.get('high', 0))
        with col3:
            st.metric("Medium", security.get('medium', 0))
        with col4:
            st.metric("Risk Score", f"{security.get('risk_score', 0)}/100")
        
        issues = security.get('issues', [])
        if issues:
            st.markdown("**Issues Found:**")
            for issue in issues:
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠', 
                    'MEDIUM': '🟡',
                    'LOW': '🔵'
                }.get(issue.get('severity'), '⚪')
                st.markdown(f"{severity_icon} **{issue.get('severity')}**: {issue.get('message')}")
                st.caption(f"Fix: {issue.get('fix')}")
        else:
            st.success("✅ No security issues found!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Built with IBM watsonx Orchestrate | IBM Dev Day Hackathon 2026"
    "</div>",
    unsafe_allow_html=True
)