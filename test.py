#!/usr/bin/env python3
"""
Quick Test Script - Verify DeployFlow is working
Run this before your demo to make sure everything works!
"""

import sys
import os

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

print("=" * 70)
print("DeployFlow - Quick System Test")
print("=" * 70)
print()

# Test 1: Check all agent files exist
print("TEST 1: Checking agent files...")
required_files = [
    'agents/analyst_agent.py',
    'agents/architect_agent.py',
    'agents/coder_agent.py',
    'agents/security_agent.py',
    'agents/orchestrator_agent.py'
]

all_exist = True
for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - MISSING!")
        all_exist = False

if not all_exist:
    print("\n❌ Some files are missing! Cannot continue.")
    sys.exit(1)

print("\n✅ All agent files found!")
print()

# Test 2: Import agents
print("TEST 2: Importing agents...")
try:
    from agents.analyst_agent import analyze_repository
    print("  ✅ Analyst Agent")
    
    from agents.architect_agent import recommend_architecture
    print("  ✅ Architect Agent")
    
    from agents.coder_agent import generate_configs
    print("  ✅ Coder Agent")
    
    from agents.security_agent import validate_configs
    print("  ✅ Security Agent")
    
    from agents.orchestrator_agent import DeployFlowOrchestrator
    print("  ✅ Orchestrator Agent")
    
    print("\n✅ All agents imported successfully!")
    print()
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    sys.exit(1)

# Test 3: Run simple orchestration
print("TEST 3: Running simple orchestration test...")
print()

sample_input = """
Language: Python 3.11
Framework: Flask
Database: PostgreSQL

Dependencies:
flask==2.3.0
gunicorn==20.1.0
psycopg2-binary==2.9.5
"""

try:
    orchestrator = DeployFlowOrchestrator()
    result = orchestrator.orchestrate_deployment(sample_input)
    
    print("\n✅ Orchestration completed successfully!")
    print()
    
    # Parse result
    import json
    result_data = json.loads(result)
    
    # Show summary
    print("=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)
    
    summary = result_data.get('summary', {})
    print(f"\n📊 Detected: {summary.get('detected_stack', 'N/A')}")
    print(f"🏗️  Platform: {summary.get('deployment_platform', 'N/A')}")
    print(f"💾 Resources: {summary.get('resources', 'N/A')}")
    print(f"🔒 Security: {summary.get('security_status', 'N/A')}")
    print(f"📝 Files Generated: {summary.get('files_generated', 0)}")
    
    # Check files
    files = result_data.get('generated_files', {})
    print("\n📥 Generated Files:")
    if files.get('dockerfile'):
        print("  ✅ Dockerfile")
    if files.get('kubernetes'):
        print("  ✅ Kubernetes manifest")
    if files.get('cicd'):
        print("  ✅ CI/CD pipeline")
    
    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED! DeployFlow is ready to use!")
    print("=" * 70)
    print()
    print("🚀 You can now run the Streamlit app:")
    print("   streamlit run app_clean.py")
    print()
    
except Exception as e:
    print(f"\n❌ Orchestration test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)