#!/usr/bin/env python3
"""
Simple security scanner for Dockerfiles and K8s manifests
Used by the Security Agent to validate generated configurations
"""

import re
from typing import List, Dict, Tuple

class SecurityScanner:
    """Scans configuration files for security issues"""
    
    # Critical security patterns
    CRITICAL_PATTERNS = {
        'hardcoded_secrets': {
            'pattern': r'(PASSWORD|API_KEY|SECRET|TOKEN)\s*=\s*[\'"]?[\w-]+',
            'message': 'Hardcoded secrets detected. Use environment variables.',
            'severity': 'CRITICAL'
        },
        'root_user': {
            'pattern': r'USER\s+root',
            'message': 'Running as root user. Create and use non-root user.',
            'severity': 'CRITICAL'
        },
        'latest_tag': {
            'pattern': r'FROM\s+[\w/-]+:latest',
            'message': 'Using :latest tag. Specify exact version.',
            'severity': 'HIGH'
        },
        'exposed_db_ports': {
            'pattern': r'EXPOSE\s+(3306|5432|27017|6379)',
            'message': 'Database ports exposed. Remove if not needed.',
            'severity': 'HIGH'
        }
    }
    
    def scan_dockerfile(self, content: str) -> Tuple[List[Dict], int]:
        """
        Scan Dockerfile content for security issues
        
        Returns:
            Tuple of (issues_list, severity_score)
        """
        issues = []
        severity_score = 0
        
        # Check if USER instruction exists and is not root
        has_user_instruction = bool(re.search(r'USER\s+(?!root)\w+', content))
        if not has_user_instruction:
            issues.append({
                'rule': 'no_user_instruction',
                'severity': 'CRITICAL',
                'message': 'No non-root USER instruction found',
                'line': None,
                'fix': 'Add: RUN useradd -m appuser && USER appuser'
            })
            severity_score += 10
        
        # Check each pattern
        for rule_name, rule_config in self.CRITICAL_PATTERNS.items():
            matches = re.finditer(rule_config['pattern'], content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'rule': rule_name,
                    'severity': rule_config['severity'],
                    'message': rule_config['message'],
                    'line': line_num,
                    'matched': match.group(0)
                })
                
                # Add to severity score
                if rule_config['severity'] == 'CRITICAL':
                    severity_score += 10
                elif rule_config['severity'] == 'HIGH':
                    severity_score += 5
                elif rule_config['severity'] == 'MEDIUM':
                    severity_score += 2
        
        # Additional checks
        if ':latest' in content:
            if not any(i['rule'] == 'latest_tag' for i in issues):
                issues.append({
                    'rule': 'latest_tag',
                    'severity': 'HIGH',
                    'message': 'Using :latest tag detected',
                    'line': None
                })
                severity_score += 5
        
        # Check for HEALTHCHECK
        if 'HEALTHCHECK' not in content:
            issues.append({
                'rule': 'missing_healthcheck',
                'severity': 'MEDIUM',
                'message': 'No HEALTHCHECK instruction found',
                'line': None,
                'fix': 'Add: HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1'
            })
            severity_score += 2
        
        return issues, severity_score
    
    def scan_kubernetes(self, content: str) -> Tuple[List[Dict], int]:
        """Scan Kubernetes YAML for security issues"""
        issues = []
        severity_score = 0
        
        # Check for resource limits
        if 'limits:' not in content:
            issues.append({
                'rule': 'missing_resource_limits',
                'severity': 'HIGH',
                'message': 'No resource limits defined',
                'fix': 'Add CPU and memory limits'
            })
            severity_score += 5
        
        # Check for security context
        if 'runAsNonRoot: true' not in content:
            issues.append({
                'rule': 'missing_security_context',
                'severity': 'HIGH',
                'message': 'runAsNonRoot not set to true',
                'fix': 'Add: runAsNonRoot: true in securityContext'
            })
            severity_score += 5
        
        # Check for privilege escalation
        if 'allowPrivilegeEscalation: true' in content:
            issues.append({
                'rule': 'privilege_escalation_enabled',
                'severity': 'CRITICAL',
                'message': 'Privilege escalation is enabled',
                'fix': 'Set: allowPrivilegeEscalation: false'
            })
            severity_score += 10
        
        return issues, severity_score
    
    def generate_report(self, issues: List[Dict], severity_score: int) -> str:
        """Generate a human-readable security report"""
        if not issues:
            return "✅ No security issues found! Configuration looks good."
        
        report = f"🔒 Security Scan Report\n"
        report += f"{'=' * 60}\n\n"
        report += f"Total Issues: {len(issues)}\n"
        report += f"Severity Score: {severity_score}/100\n"
        
        if severity_score >= 10:
            report += f"Status: ⚠️  CRITICAL - Must fix before deployment\n\n"
        elif severity_score >= 5:
            report += f"Status: ⚠️  HIGH - Should fix soon\n\n"
        else:
            report += f"Status: ℹ️  LOW - Consider improvements\n\n"
        
        # Group by severity
        critical = [i for i in issues if i['severity'] == 'CRITICAL']
        high = [i for i in issues if i['severity'] == 'HIGH']
        medium = [i for i in issues if i['severity'] == 'MEDIUM']
        
        if critical:
            report += "🔴 CRITICAL Issues:\n"
            for issue in critical:
                report += f"  - {issue['message']}\n"
                if 'fix' in issue:
                    report += f"    Fix: {issue['fix']}\n"
            report += "\n"
        
        if high:
            report += "🟠 HIGH Issues:\n"
            for issue in high:
                report += f"  - {issue['message']}\n"
                if 'fix' in issue:
                    report += f"    Fix: {issue['fix']}\n"
            report += "\n"
        
        if medium:
            report += "🟡 MEDIUM Issues:\n"
            for issue in medium:
                report += f"  - {issue['message']}\n"
            report += "\n"
        
        return report


# Example usage
if __name__ == "__main__":
    scanner = SecurityScanner()
    
    # Test Dockerfile
    test_dockerfile = """
    FROM python:latest
    WORKDIR /app
    COPY . .
    ENV API_KEY=secret123
    RUN pip install -r requirements.txt
    EXPOSE 8080
    CMD ["python", "app.py"]
    """
    
    issues, score = scanner.scan_dockerfile(test_dockerfile)
    print(scanner.generate_report(issues, score))