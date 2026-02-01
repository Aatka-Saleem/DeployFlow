"""
Orchestrator Agent - Main Workflow Coordinator
Manages the complete workflow from analysis to deployment configuration generation
"""

import json
import sys
import os
from typing import Dict, Optional

# Import the other agents
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyst_agent import analyze_repository
from architect_agent import recommend_architecture
from coder_agent import generate_configs
from security_agent import validate_configs, generate_security_report


class DeployFlowOrchestrator:
    """Orchestrates the complete DeployFlow workflow"""
    
    def __init__(self):
        self.workflow_state = {
            'step': 0,
            'status': 'initialized',
            'analysis': None,
            'recommendations': None,
            'configs': None,
            'security_validation': None,
            'error': None
        }
    
    def orchestrate_deployment(self, repo_input: str) -> str:
        """
        Main orchestration function - runs complete workflow
        
        Args:
            repo_input: GitHub repo URL or repo description/content
        
        Returns:
            JSON string with complete workflow results
        """
        try:
            print("🚀 DeployFlow Orchestrator Starting...")
            print("=" * 70)
            
            # Step 1: Analysis
            print("\n📊 STEP 1: Analyzing Repository...")
            self.workflow_state['step'] = 1
            self.workflow_state['status'] = 'analyzing'
            
            analysis_result = analyze_repository(repo_content=repo_input)
            self.workflow_state['analysis'] = json.loads(analysis_result)
            
            print(f"✅ Detected: {self.workflow_state['analysis']['language']} - {self.workflow_state['analysis']['framework']}")
            
            # Step 2: Architecture Recommendations
            print("\n🏗️  STEP 2: Generating Architecture Recommendations...")
            self.workflow_state['step'] = 2
            self.workflow_state['status'] = 'recommending'
            
            recommendations_result = recommend_architecture(analysis_result)
            self.workflow_state['recommendations'] = json.loads(recommendations_result)
            
            print(f"✅ Recommended: {self.workflow_state['recommendations']['platform']}")
            print(f"   Resources: {self.workflow_state['recommendations']['resources']['cpu']} vCPU, {self.workflow_state['recommendations']['resources']['memory']}")
            
            # Step 3: Generate Configuration Files
            print("\n📝 STEP 3: Generating Configuration Files...")
            self.workflow_state['step'] = 3
            self.workflow_state['status'] = 'generating'
            
            configs_result = generate_configs(analysis_result, recommendations_result)
            self.workflow_state['configs'] = json.loads(configs_result)
            
            print("✅ Generated:")
            print("   - Dockerfile")
            print("   - kubernetes-deployment.yaml")
            print("   - github-actions.yml")
            
            # Step 4: Security Validation
            print("\n🔒 STEP 4: Validating Security...")
            self.workflow_state['step'] = 4
            self.workflow_state['status'] = 'validating'
            
            security_result = validate_configs(configs_result)
            self.workflow_state['security_validation'] = json.loads(security_result)
            
            print(f"✅ Security Status: {self.workflow_state['security_validation']['status']}")
            print(f"   Issues: {self.workflow_state['security_validation']['total_issues']} total")
            print(f"   Risk Score: {self.workflow_state['security_validation']['risk_score']}/100")
            
            # Complete
            self.workflow_state['step'] = 5
            self.workflow_state['status'] = 'complete'
            
            print("\n" + "=" * 70)
            print("✨ DeployFlow Orchestration Complete!")
            print("=" * 70)
            
            # Return complete results
            return self._format_final_results()
            
        except Exception as e:
            self.workflow_state['status'] = 'failed'
            self.workflow_state['error'] = str(e)
            print(f"\n❌ Error in orchestration: {e}")
            return json.dumps({
                'status': 'failed',
                'error': str(e),
                'step': self.workflow_state['step']
            }, indent=2)
    
    def _format_final_results(self) -> str:
        """Format final results as JSON"""
        result = {
            'status': 'success',
            'workflow': {
                'steps_completed': self.workflow_state['step'],
                'final_status': self.workflow_state['status']
            },
            'analysis': self.workflow_state['analysis'],
            'recommendations': self.workflow_state['recommendations'],
            'generated_files': {
                'dockerfile': self.workflow_state['configs']['dockerfile'],
                'kubernetes': self.workflow_state['configs']['kubernetes'],
                'cicd': self.workflow_state['configs']['cicd']
            },
            'security_validation': self.workflow_state['security_validation'],
            'summary': self._generate_summary()
        }
        
        return json.dumps(result, indent=2)
    
    def _generate_summary(self) -> Dict:
        """Generate executive summary"""
        analysis = self.workflow_state['analysis']
        recommendations = self.workflow_state['recommendations']
        security = self.workflow_state['security_validation']
        
        summary = {
            'detected_stack': f"{analysis['language']} {analysis['language_version']} with {analysis['framework']}",
            'deployment_platform': recommendations['platform'],
            'resources': f"{recommendations['resources']['cpu']} vCPU, {recommendations['resources']['memory']}",
            'security_status': security['status'],
            'production_ready': security['compliance']['production_ready'],
            'files_generated': 3,
            'next_steps': self._generate_next_steps()
        }
        
        return summary
    
    def _generate_next_steps(self) -> list:
        """Generate next steps for user"""
        security = self.workflow_state['security_validation']
        
        next_steps = []
        
        if security['status'] == 'BLOCKED':
            next_steps.append('❌ Fix CRITICAL security issues before deployment')
            next_steps.extend(security['recommendations'][:3])
        elif security['status'] == 'REVIEW_REQUIRED':
            next_steps.append('⚠️ Review and address security warnings')
            next_steps.append('Download generated configuration files')
            next_steps.append('Test locally with Docker')
        else:
            next_steps.append('✅ Download generated configuration files')
            next_steps.append('Add files to your repository')
            next_steps.append('Configure IBM Cloud credentials in GitHub Secrets')
            next_steps.append('Push to trigger CI/CD pipeline')
        
        return next_steps
    
    def get_workflow_status(self) -> str:
        """Get current workflow status"""
        return json.dumps({
            'current_step': self.workflow_state['step'],
            'status': self.workflow_state['status'],
            'steps': [
                'Analysis',
                'Architecture Recommendations',
                'Configuration Generation',
                'Security Validation',
                'Complete'
            ]
        }, indent=2)
    
    def generate_detailed_report(self) -> str:
        """Generate human-readable detailed report"""
        if self.workflow_state['status'] != 'complete':
            return "Workflow not yet complete. Run orchestrate_deployment first."
        
        report = []
        report.append("=" * 70)
        report.append("DEPLOYFLOW - DEPLOYMENT CONFIGURATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Analysis Section
        report.append("📊 REPOSITORY ANALYSIS")
        report.append("-" * 70)
        analysis = self.workflow_state['analysis']
        report.append(f"Language:         {analysis['language']} {analysis['language_version']}")
        report.append(f"Framework:        {analysis['framework']}")
        report.append(f"Database:         {analysis.get('database', 'none')}")
        report.append(f"Main File:        {analysis['main_file']}")
        report.append(f"Port:             {analysis['port']}")
        report.append(f"Package Manager:  {analysis['package_manager']}")
        report.append("")
        
        # Recommendations Section
        report.append("🏗️  DEPLOYMENT RECOMMENDATIONS")
        report.append("-" * 70)
        recs = self.workflow_state['recommendations']
        report.append(f"Platform:         {recs['platform']}")
        report.append(f"CPU:              {recs['resources']['cpu']} vCPU")
        report.append(f"Memory:           {recs['resources']['memory']}")
        report.append(f"Scaling:          {recs['scaling']['min_replicas']}-{recs['scaling']['max_replicas']} replicas")
        report.append(f"Estimated Cost:   {recs['estimated_cost']}")
        report.append(f"\nRationale: {recs['rationale']}")
        report.append("")
        
        # Generated Files Section
        report.append("📝 GENERATED FILES")
        report.append("-" * 70)
        report.append("✅ Dockerfile (production-ready)")
        report.append("✅ kubernetes-deployment.yaml (with service & HPA)")
        report.append("✅ github-actions.yml (CI/CD pipeline)")
        report.append("")
        
        # Security Section
        report.append("🔒 SECURITY VALIDATION")
        report.append("-" * 70)
        sec = self.workflow_state['security_validation']
        report.append(f"Status:           {sec['status']}")
        report.append(f"Risk Score:       {sec['risk_score']}/100")
        report.append(f"Total Issues:     {sec['total_issues']}")
        report.append(f"  - Critical:     {sec['critical']}")
        report.append(f"  - High:         {sec['high']}")
        report.append(f"  - Medium:       {sec['medium']}")
        report.append(f"  - Low:          {sec['low']}")
        report.append(f"Production Ready: {'✅ Yes' if sec['compliance']['production_ready'] else '⚠️ No'}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 70)
        for rec in recs.get('recommendations', [])[:5]:
            report.append(f"• {rec}")
        report.append("")
        
        # Next Steps
        report.append("📥 NEXT STEPS")
        report.append("-" * 70)
        summary = self._generate_summary()
        for i, step in enumerate(summary['next_steps'], 1):
            report.append(f"{i}. {step}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


# Main functions that ADK will call
def orchestrate_deployment(repo_input: str) -> str:
    """
    ADK Tool Function: Run complete DeployFlow orchestration
    
    Args:
        repo_input: GitHub repo URL or repo content/description
    
    Returns:
        JSON string with complete workflow results
    """
    orchestrator = DeployFlowOrchestrator()
    return orchestrator.orchestrate_deployment(repo_input)


def get_workflow_status() -> str:
    """
    ADK Tool Function: Get current workflow status
    
    Returns:
        JSON string with workflow status
    """
    orchestrator = DeployFlowOrchestrator()
    return orchestrator.get_workflow_status()


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("TESTING DEPLOYFLOW ORCHESTRATOR")
    print("=" * 70)
    print()
    
    # Sample repository content
    sample_repo = """
    Repository: Flask API with PostgreSQL
    
    requirements.txt:
    flask==2.3.0
    gunicorn==20.1.0
    psycopg2-binary==2.9.5
    pytest==7.0.0
    
    Files:
    - app.py (main application)
    - requirements.txt
    - tests/
    """
    
    # Run orchestration
    result_json = orchestrate_deployment(sample_repo)
    
    # Parse and display detailed report
    orchestrator = DeployFlowOrchestrator()
    orchestrator.orchestrate_deployment(sample_repo)
    
    print("\n\n")
    print(orchestrator.generate_detailed_report())
    
    print("\n\n📄 FULL JSON OUTPUT:")
    print("=" * 70)
    result = json.loads(result_json)
    print(json.dumps(result['summary'], indent=2))