"""
Analyst Agent - Repository Analysis Tool
Detects programming language, framework, and dependencies from GitHub repos
"""

import re
import json
from typing import Dict, List, Optional


class RepositoryAnalyzer:
    """Analyzes repository structure and identifies tech stack"""
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        'python': {
            'flask': ['flask', 'Flask'],
            'django': ['django', 'Django'],
            'fastapi': ['fastapi', 'FastAPI'],
        },
        'nodejs': {
            'express': ['express', '"express"'],
            'nextjs': ['next', '"next"'],
            'nestjs': ['@nestjs/core'],
            'fastify': ['fastify'],
        },
        'java': {
            'spring-boot': ['spring-boot-starter', 'springframework.boot'],
            'quarkus': ['quarkus'],
        }
    }
    
    # Default ports by framework
    DEFAULT_PORTS = {
        'flask': 5000,
        'django': 8000,
        'fastapi': 8000,
        'express': 3000,
        'nextjs': 3000,
        'nestjs': 3000,
        'spring-boot': 8080,
        'quarkus': 8080,
    }
    
    def __init__(self):
        self.detected_language = None
        self.detected_framework = None
        self.dependencies = []
        self.language_version = None
    
    def analyze_repository(self, repo_content: str) -> Dict:
        """
        Main analysis function
        
        Args:
            repo_content: String containing repository file contents or structure
            
        Returns:
            Dictionary with analysis results
        """
        # Detect language first
        self.detected_language = self._detect_language(repo_content)
        
        if not self.detected_language:
            return self._create_error_response("Unable to detect programming language")
        
        # Extract dependencies
        self.dependencies = self._extract_dependencies(repo_content, self.detected_language)
        
        # Detect framework
        self.detected_framework = self._detect_framework(self.dependencies, self.detected_language)
        
        # Detect versions
        self.language_version = self._detect_language_version(repo_content, self.detected_language)
        
        # Determine main file
        main_file = self._determine_main_file(repo_content, self.detected_language, self.detected_framework)
        
        # Determine port
        port = self._determine_port(self.detected_framework)
        
        # Detect database
        database = self._detect_database(self.dependencies)
        
        # Determine package manager
        package_manager = self._determine_package_manager(self.detected_language)
        
        return {
            'language': self.detected_language,
            'language_version': self.language_version or self._get_default_version(self.detected_language),
            'framework': self.detected_framework or 'none',
            'main_file': main_file,
            'port': port,
            'dependencies': self.dependencies[:10],  # Limit to top 10
            'database': database,
            'package_manager': package_manager,
            'analysis_confidence': self._calculate_confidence()
        }
    
    def _detect_language(self, content: str) -> Optional[str]:
        """Detect programming language from file patterns"""
        if 'requirements.txt' in content or '.py' in content:
            return 'python'
        elif 'package.json' in content or '.js' in content or '.ts' in content:
            return 'nodejs'
        elif 'pom.xml' in content or '.java' in content:
            return 'java'
        elif 'go.mod' in content or '.go' in content:
            return 'go'
        return None
    
    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract dependency list from content"""
        dependencies = []
        
        if language == 'python':
            # Extract from requirements.txt pattern
            req_pattern = r'([a-zA-Z0-9\-_]+)(?:==|>=|<=|~=)?'
            matches = re.findall(req_pattern, content)
            dependencies = [m.lower() for m in matches if len(m) > 2]
            
        elif language == 'nodejs':
            # Extract from package.json pattern
            dep_pattern = r'"([a-zA-Z0-9\-@/]+)":\s*"'
            matches = re.findall(dep_pattern, content)
            dependencies = matches
            
        elif language == 'java':
            # Extract from pom.xml or gradle
            artifact_pattern = r'<artifactId>([a-zA-Z0-9\-_]+)</artifactId>'
            matches = re.findall(artifact_pattern, content)
            dependencies = matches
        
        return list(set(dependencies))  # Remove duplicates
    
    def _detect_framework(self, dependencies: List[str], language: str) -> Optional[str]:
        """Detect framework from dependencies"""
        if language not in self.FRAMEWORK_PATTERNS:
            return None
        
        frameworks = self.FRAMEWORK_PATTERNS[language]
        
        for framework, patterns in frameworks.items():
            for pattern in patterns:
                if any(pattern.lower() in dep.lower() for dep in dependencies):
                    return framework
        
        return None
    
    def _detect_language_version(self, content: str, language: str) -> Optional[str]:
        """Detect language version from content"""
        if language == 'python':
            # Look for python_requires or runtime
            version_pattern = r'python[_-]?(?:requires)?["\']?[>=<~]*([0-9.]+)'
            match = re.search(version_pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        elif language == 'nodejs':
            # Look for engines in package.json
            version_pattern = r'"node":\s*"[>=<~]*([0-9.]+)"'
            match = re.search(version_pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _determine_main_file(self, content: str, language: str, framework: Optional[str]) -> str:
        """Determine the main application file"""
        if language == 'python':
            if 'app.py' in content:
                return 'app.py'
            elif 'main.py' in content:
                return 'main.py'
            elif 'server.py' in content:
                return 'server.py'
            return 'app.py'  # default
        
        elif language == 'nodejs':
            if 'server.js' in content:
                return 'server.js'
            elif 'index.js' in content:
                return 'index.js'
            elif 'app.js' in content:
                return 'app.js'
            return 'index.js'  # default
        
        elif language == 'java':
            return 'Application.java'
        
        elif language == 'go':
            return 'main.go'
        
        return 'main'
    
    def _determine_port(self, framework: Optional[str]) -> int:
        """Determine appropriate port for framework"""
        if framework and framework in self.DEFAULT_PORTS:
            return self.DEFAULT_PORTS[framework]
        return 8080  # default
    
    def _detect_database(self, dependencies: List[str]) -> str:
        """Detect database from dependencies"""
        db_patterns = {
            'postgresql': ['psycopg2', 'pg', 'postgres'],
            'mysql': ['mysql', 'pymysql', 'mysql2'],
            'mongodb': ['pymongo', 'mongoose', 'mongodb'],
            'redis': ['redis'],
            'sqlite': ['sqlite3', 'sqlite'],
        }
        
        for db, patterns in db_patterns.items():
            if any(pattern in dep.lower() for dep in dependencies for pattern in patterns):
                return db
        
        return 'none'
    
    def _determine_package_manager(self, language: str) -> str:
        """Determine package manager for language"""
        managers = {
            'python': 'pip',
            'nodejs': 'npm',
            'java': 'maven',
            'go': 'go-mod'
        }
        return managers.get(language, 'unknown')
    
    def _get_default_version(self, language: str) -> str:
        """Get default/recommended version for language"""
        defaults = {
            'python': '3.11',
            'nodejs': '18',
            'java': '17',
            'go': '1.21'
        }
        return defaults.get(language, 'latest')
    
    def _calculate_confidence(self) -> str:
        """Calculate confidence level of analysis"""
        score = 0
        if self.detected_language:
            score += 40
        if self.detected_framework:
            score += 30
        if self.dependencies:
            score += 20
        if self.language_version:
            score += 10
        
        if score >= 80:
            return 'high'
        elif score >= 50:
            return 'medium'
        return 'low'
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create error response"""
        return {
            'error': error_message,
            'language': 'unknown',
            'framework': 'unknown',
            'dependencies': [],
            'analysis_confidence': 'none'
        }


# Main function that ADK will call
def analyze_repository(repo_url: str = None, repo_content: str = None) -> str:
    """
    ADK Tool Function: Analyze a repository
    
    Args:
        repo_url: GitHub repository URL (optional)
        repo_content: Repository content as string (for testing)
    
    Returns:
        JSON string with analysis results
    """
    analyzer = RepositoryAnalyzer()
    
    # For hackathon demo, we'll work with repo_content
    # In production, you'd fetch from repo_url using GitHub API
    
    if not repo_content:
        # Simple mock content for testing
        repo_content = """
        requirements.txt:
        flask==2.3.0
        gunicorn==20.1.0
        psycopg2-binary==2.9.5
        
        app.py:
        from flask import Flask
        app = Flask(__name__)
        """
    
    result = analyzer.analyze_repository(repo_content)
    return json.dumps(result, indent=2)


# Test function
if __name__ == "__main__":
    # Test with sample Flask app
    sample_content = """
    requirements.txt:
    flask==2.3.0
    gunicorn==20.1.0
    psycopg2-binary==2.9.5
    pytest==7.0.0
    
    app.py exists
    """
    
    print("Testing Analyst Agent:")
    print(analyze_repository(repo_content=sample_content))