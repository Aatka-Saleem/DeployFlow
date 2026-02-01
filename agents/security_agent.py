"""
Security Agent - Configuration Security Validator
Scans Dockerfiles and Kubernetes manifests for security vulnerabilities
"""

import json
import re
from typing import Dict, List, Tuple


class SecurityValidator:
    """Validates deployment configurations for security issues"""
    
    # Security rules with patterns and severity
    SECURITY_RULES = {
        # CRITICAL RULES
        'hardcoded_secrets': {
            'pattern': r'(PASSWORD|API_KEY|SECRET|TOKEN)\s*[:=]\s*["\']?[\w-]{8,}',
            'severity': 'CRITICAL',
            'message': 'Hardcoded secrets detected. Use environment variables or secrets management.',
            'applies_to': ['dockerfile', 'kubernetes', 'cicd'],
            'fix': 'Use environment variables: ENV API_KEY=${API_KEY}'
        },
        'root_user_missing': {
            'pattern': r'USER\s+(?!root)',
            'severity': 'CRITICAL',
            'message': 'No non-root USER instruction found',
            'applies_to': ['dockerfile'],
            'fix': 'Add: RUN useradd -m appuser && USER appuser',
            'inverse': True  # Check for absence
        },
        'privilege_escalation': {
            'pattern': r'allowPrivilegeEscalation:\s*true',
            'severity': 'CRITICAL',
            'message': 'Privilege escalation is enabled',
            'applies_to': ['kubernetes'],
            'fix': 'Set: allowPrivilegeEscalation: false'
        },
        
        # HIGH RULES
        'latest_tag': {
            'pattern': r'FROM\s+[\w/-]+:latest',
            'severity': 'HIGH',
            'message': 'Using :latest tag - use specific version',
            'applies_to': ['dockerfile'],
            'fix': 'Use specific version: FROM python:3.11-slim'
        },
        'missing_resource_limits': {
            'pattern': r'limits:',
            'severity': 'HIGH',
            'message': 'No resource limits defined',
            'applies_to': ['kubernetes'],
            'fix': 'Add CPU and memory limits in resources section',
            'inverse': True
        },
        'no_security_context': {
            'pattern': r'runAsNonRoot:\s*true',
            'severity': 'HIGH',
            'message': 'runAsNonRoot not set to true',
            'applies_to': ['kubernetes'],
            'fix': 'Add: runAsNonRoot: true in securityContext',
            'inverse': True
        },
        'exposed_db_ports': {
            'pattern': r'EXPOSE\s+(22|3306|5432|27017|6379)',
            'severity': 'HIGH',
            'message': 'Sensitive ports (SSH/DB) exposed',
            'applies_to': ['dockerfile'],
            'fix': 'Remove EXPOSE for database/SSH ports'
        },
        
        # MEDIUM RULES
        'missing_healthcheck': {
            'pattern': r'HEALTHCHECK|livenessProbe',
            'severity': 'MEDIUM',
            'message': 'No health checks configured',
            'applies_to': ['dockerfile', 'kubernetes'],
            'fix': 'Add HEALTHCHECK or probes for reliability',
            'inverse': True
        },
        'writable_filesystem': {
            'pattern': r'readOnlyRootFilesystem:\s*false',
            'severity': 'MEDIUM',
            'message': 'Root filesystem is writable',
            'applies_to': ['kubernetes'],
            'fix': 'Set: readOnlyRootFilesystem: true when possible'
        },
        'large_base_image': {
            'pattern': r'FROM\s+(python|node):[\\d.]+\\s',
            'severity': 'LOW',
            'message': 'Using full base image instead of slim/alpine',
            'applies_to': ['dockerfile'],
            'fix': 'Use slim variant: python:3.11-slim or node:18-alpine'
        }
    }
    
    # Production readiness requirements
    PRODUCTION_REQUIREMENTS = [
        {'name': 'Non-root user', 'check': 'root_user_missing'},
        {'name': 'Specific image tags', 'check': 'latest_tag'},
        {'name': 'Resource limits', 'check': 'missing_resource_limits'},
        {'name': 'Security context', 'check': 'no_security_context'},
        {'name': 'No hardcoded secrets', 'check': 'hardcoded_secrets'},
    ]
    
    def __init__(self):
        self.issues = []
        self.total_critical = 0
        self.total_high = 0
        self.total_medium = 0
        self.total_low = 0
    
    def scan_dockerfile(self, dockerfile_content: str) -> List[Dict]:
        """
        Scan Dockerfile for security issues
        
        Args:
            dockerfile_content: Dockerfile content as string
        
        Returns:
            List of security issues found
        """
        issues = []
        
        for rule_name, rule in self.SECURITY_RULES.items():
            if 'dockerfile' not in rule['applies_to']:
                continue
            
            inverse = rule.get('inverse', False)
            pattern_found = bool(re.search(rule['pattern'], dockerfile_content, re.IGNORECASE))
            
            # For inverse rules, issue exists if pattern NOT found
            has_issue = (not pattern_found) if inverse else pattern_found
            
            if has_issue:
                # Find line number if pattern exists
                line_num = None
                if pattern_found:
                    match = re.search(rule['pattern'], dockerfile_content, re.IGNORECASE)
                    if match:
                        line_num = dockerfile_content[:match.start()].count('\n') + 1
                
                issue = {
                    'severity': rule['severity'],
                    'rule': rule_name,
                    'message': rule['message'],
                    'location': 'dockerfile',
                    'line': line_num,
                    'fix': rule.get('fix', 'Review security best practices')
                }
                issues.append(issue)
                
                # Count by severity
                if rule['severity'] == 'CRITICAL':
                    self.total_critical += 1
                elif rule['severity'] == 'HIGH':
                    self.total_high += 1
                elif rule['severity'] == 'MEDIUM':
                    self.total_medium += 1
                else:
                    self.total_low += 1
        
        return issues
    
    def scan_kubernetes(self, k8s_content: str) -> List[Dict]:
        """
        Scan Kubernetes manifest for security issues
        
        Args:
            k8s_content: Kubernetes YAML content as string
        
        Returns:
            List of security issues found
        """
        issues = []
        
        for rule_name, rule in self.SECURITY_RULES.items():
            if 'kubernetes' not in rule['applies_to']:
                continue
            
            inverse = rule.get('inverse', False)
            pattern_found = bool(re.search(rule['pattern'], k8s_content, re.IGNORECASE))
            
            has_issue = (not pattern_found) if inverse else pattern_found
            
            if has_issue:
                line_num = None
                if pattern_found:
                    match = re.search(rule['pattern'], k8s_content, re.IGNORECASE)
                    if match:
                        line_num = k8s_content[:match.start()].count('\n') + 1
                
                issue = {
                    'severity': rule['severity'],
                    'rule': rule_name,
                    'message': rule['message'],
                    'location': 'kubernetes',
                    'line': line_num,
                    'fix': rule.get('fix', 'Review Kubernetes security best practices')
                }
                issues.append(issue)
                
                if rule['severity'] == 'CRITICAL':
                    self.total_critical += 1
                elif rule['severity'] == 'HIGH':
                    self.total_high += 1
                elif rule['severity'] == 'MEDIUM':
                    self.total_medium += 1
                else:
                    self.total_low += 1
        
        return issues
    
    def validate_configs(self, configs: Dict) -> str:
        """
        Validate all configurations
        
        Args:
            configs: Dictionary with dockerfile, kubernetes, cicd content
        
        Returns:
            JSON string with validation results
        """
        self.issues = []
        self.total_critical = 0
        self.total_high = 0
        self.total_medium = 0
        self.total_low = 0
        
        # Scan Dockerfile
        if 'dockerfile' in configs:
            dockerfile_issues = self.scan_dockerfile(configs['dockerfile'])
            self.issues.extend(dockerfile_issues)
        
        # Scan Kubernetes
        if 'kubernetes' in configs:
            k8s_issues = self.scan_kubernetes(configs['kubernetes'])
            self.issues.extend(k8s_issues)
        
        # Calculate risk score (0-100)
        risk_score = (
            self.total_critical * 25 +
            self.total_high * 10 +
            self.total_medium * 5 +
            self.total_low * 2
        )
        risk_score = min(risk_score, 100)
        
        # Determine status
        if self.total_critical > 0:
            status = 'BLOCKED'
        elif risk_score > 40:
            status = 'REVIEW_REQUIRED'
        else:
            status = 'APPROVED'
        
        # Check production readiness
        missing_requirements = []
        for req in self.PRODUCTION_REQUIREMENTS:
            if any(issue['rule'] == req['check'] for issue in self.issues):
                missing_requirements.append(req['name'])
        
        production_ready = len(missing_requirements) == 0 and self.total_critical == 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        result = {
            'total_issues': len(self.issues),
            'critical': self.total_critical,
            'high': self.total_high,
            'medium': self.total_medium,
            'low': self.total_low,
            'risk_score': risk_score,
            'status': status,
            'issues': self.issues,
            'compliance': {
                'production_ready': production_ready,
                'missing_requirements': missing_requirements
            },
            'recommendations': recommendations
        }
        
        return json.dumps(result, indent=2)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on found issues"""
        recommendations = []
        
        if self.total_critical > 0:
            recommendations.append('⚠️ CRITICAL issues must be fixed before deployment')
        
        if any(i['rule'] == 'root_user_missing' for i in self.issues):
            recommendations.append('Add non-root user to Dockerfile')
        
        if any(i['rule'] == 'latest_tag' for i in self.issues):
            recommendations.append('Use specific version tags instead of :latest')
        
        if any(i['rule'] == 'missing_resource_limits' for i in self.issues):
            recommendations.append('Set resource limits to prevent resource exhaustion')
        
        if any(i['rule'] == 'no_security_context' for i in self.issues):
            recommendations.append('Configure security context with runAsNonRoot: true')
        
        if any(i['rule'] == 'missing_healthcheck' for i in self.issues):
            recommendations.append('Add health checks for better reliability')
        
        if len(recommendations) == 0:
            recommendations.append('✅ Configuration follows security best practices')
        
        return recommendations
    
    def generate_security_report(self, validation_result: str) -> str:
        """
        Generate human-readable security report
        
        Args:
            validation_result: JSON validation result
        
        Returns:
            Formatted security report
        """
        result = json.loads(validation_result)
        
        report = "=" * 70 + "\n"
        report += "SECURITY VALIDATION REPORT\n"
        report += "=" * 70 + "\n\n"
        
        # Summary
        report += f"Total Issues: {result['total_issues']}\n"
        report += f"  🔴 Critical: {result['critical']}\n"
        report += f"  🟠 High: {result['high']}\n"
        report += f"  🟡 Medium: {result['medium']}\n"
        report += f"  🔵 Low: {result['low']}\n\n"
        
        report += f"Risk Score: {result['risk_score']}/100\n"
        report += f"Status: {result['status']}\n\n"
        
        # Production readiness
        compliance = result['compliance']
        if compliance['production_ready']:
            report += "✅ PRODUCTION READY\n\n"
        else:
            report += "⚠️ NOT PRODUCTION READY\n"
            report += "Missing requirements:\n"
            for req in compliance['missing_requirements']:
                report += f"  - {req}\n"
            report += "\n"
        
        # Issues by severity
        if result['issues']:
            report += "ISSUES FOUND:\n"
            report += "-" * 70 + "\n\n"
            
            for issue in sorted(result['issues'], key=lambda x: 
                               {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}[x['severity']]):
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🔵'
                }[issue['severity']]
                
                report += f"{severity_icon} {issue['severity']}: {issue['message']}\n"
                report += f"   Location: {issue['location']}"
                if issue['line']:
                    report += f" (line {issue['line']})"
                report += f"\n   Fix: {issue['fix']}\n\n"
        
        # Recommendations
        report += "RECOMMENDATIONS:\n"
        report += "-" * 70 + "\n"
        for rec in result['recommendations']:
            report += f"• {rec}\n"
        
        report += "\n" + "=" * 70 + "\n"
        
        return report


# Main functions that ADK will call
def validate_configs(configs_json: str) -> str:
    """
    ADK Tool Function: Validate all configurations
    
    Args:
        configs_json: JSON with dockerfile, kubernetes, cicd content
    
    Returns:
        JSON string with validation results
    """
    try:
        configs = json.loads(configs_json)
    except:
        configs = {}
    
    validator = SecurityValidator()
    return validator.validate_configs(configs)


def scan_dockerfile(dockerfile_content: str) -> str:
    """Scan only Dockerfile"""
    validator = SecurityValidator()
    issues = validator.scan_dockerfile(dockerfile_content)
    return json.dumps({'issues': issues}, indent=2)


def scan_kubernetes(k8s_content: str) -> str:
    """Scan only Kubernetes manifest"""
    validator = SecurityValidator()
    issues = validator.scan_kubernetes(k8s_content)
    return json.dumps({'issues': issues}, indent=2)


def generate_security_report(validation_json: str) -> str:
    """Generate human-readable report"""
    validator = SecurityValidator()
    return validator.generate_security_report(validation_json)


# Test function
if __name__ == "__main__":
    print("Testing Security Agent:\n")
    
    # Test with sample configs
    test_dockerfile = """FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
"""
    
    test_k8s = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: my-app
        image: my-app:v1.0.0
        resources:
          limits:
            cpu: 1
            memory: 1G
        securityContext:
          runAsNonRoot: true
          allowPrivilegeEscalation: false
"""
    
    configs = {
        'dockerfile': test_dockerfile,
        'kubernetes': test_k8s
    }
    
    result = validate_configs(json.dumps(configs))
    print(generate_security_report(result))