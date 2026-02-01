"""
Architect Agent - Deployment Architecture Recommendation
Uses RAG to query knowledge base and recommend optimal deployment strategy
"""

import json
import os
from typing import Dict, List


class DeploymentArchitect:
    """Recommends deployment architecture using knowledge base"""
    
    # Platform selection rules
    PLATFORM_RULES = {
        'code-engine': {
            'good_for': ['web-apps', 'apis', 'microservices', 'serverless'],
            'max_replicas': 100,
            'supports_scale_to_zero': True,
            'cost_model': 'pay-per-use'
        },
        'kubernetes': {
            'good_for': ['stateful-apps', 'complex-workflows', 'high-traffic', 'ml-inference'],
            'max_replicas': 1000,
            'supports_scale_to_zero': False,
            'cost_model': 'always-on'
        }
    }
    
    # Resource recommendations by framework
    RESOURCE_TEMPLATES = {
        'flask': {'cpu': '0.5', 'memory': '1G', 'workers': 2},
        'django': {'cpu': '1', 'memory': '2G', 'workers': 4},
        'fastapi': {'cpu': '0.5', 'memory': '1G', 'workers': 2},
        'express': {'cpu': '0.25', 'memory': '512M', 'workers': 1},
        'nextjs': {'cpu': '0.5', 'memory': '1G', 'workers': 1},
        'spring-boot': {'cpu': '1', 'memory': '2G', 'workers': 1},
    }
    
    def __init__(self, knowledge_base_path: str = None):
        """
        Initialize architect with knowledge base
        
        Args:
            knowledge_base_path: Path to knowledge base documents
        """
        self.knowledge_base_path = knowledge_base_path or r'D:/DeployFlow/knowledge-base'
        self.knowledge_cache = {}
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load knowledge base documents into memory with UTF-8 encoding"""
        if not os.path.exists(self.knowledge_base_path):
            print(f"Warning: Knowledge base path not found: {self.knowledge_base_path}")
            return
    
        try:
            for filename in os.listdir(self.knowledge_base_path):
                if filename.endswith('.md'):
                    filepath = os.path.join(self.knowledge_base_path, filename)
                    # FIX: Explicitly set encoding to utf-8
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.knowledge_cache[filename] = f.read()
            print(f"Loaded {len(self.knowledge_cache)} knowledge documents")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")

    
    

    
    def query_knowledge_base(self, query: str, doc_type: str = None) -> str:
        """
        Query knowledge base (RAG simulation)
        
        Args:
            query: Search query
            doc_type: Specific document type (python, nodejs, docker, etc.)
        
        Returns:
            Relevant knowledge snippet
        """
        query_lower = query.lower()
        relevant_docs = []
        
        # Simple keyword-based retrieval (in production, use embeddings)
        for doc_name, content in self.knowledge_cache.items():
            if doc_type and doc_type not in doc_name.lower():
                continue
            
            # Check if query keywords appear in document
            score = sum(1 for word in query_lower.split() if word in content.lower())
            if score > 0:
                relevant_docs.append((doc_name, content, score))
        
        # Sort by relevance
        relevant_docs.sort(key=lambda x: x[2], reverse=True)
        
        if relevant_docs:
            # Return snippet from most relevant document
            doc_name, content, _ = relevant_docs[0]
            # Extract relevant section (first 500 chars containing query terms)
            for line in content.split('\n'):
                if any(word in line.lower() for word in query_lower.split()):
                    return f"[From {doc_name}]: {line[:500]}"
        
        return "No relevant knowledge found"
    
    def recommend_architecture(self, analysis: Dict) -> str:
        """
        Main function: Recommend deployment architecture
        
        Args:
            analysis: Application analysis from Analyst Agent
        
        Returns:
            JSON string with architecture recommendations
        """
        language = analysis.get('language', 'unknown')
        framework = analysis.get('framework', 'none')
        database = analysis.get('database', 'none')
        
        # Determine platform
        platform = self._select_platform(analysis)
        
        # Get resource recommendations
        resources = self._recommend_resources(framework, database)
        
        # Get scaling configuration
        scaling = self._recommend_scaling(platform, framework)
        
        # Query knowledge base for specific recommendations
        kb_recommendations = self._get_kb_recommendations(language, framework)
        
        # Generate best practices
        best_practices = self._generate_best_practices(language, framework, platform)
        
        # Estimate cost
        cost = self._estimate_cost(resources, scaling)
        
        # Build recommendation
        recommendation = {
            'platform': platform,
            'rationale': self._build_rationale(analysis, platform),
            'resources': resources,
            'scaling': scaling,
            'recommendations': kb_recommendations,
            'best_practices': best_practices,
            'estimated_cost': cost,
            'confidence': 'high'
        }
        
        return json.dumps(recommendation, indent=2)
    
    def _select_platform(self, analysis: Dict) -> str:
        """Select deployment platform based on analysis"""
        framework = analysis.get('framework', 'none')
        database = analysis.get('database', 'none')
        
        # Rules for platform selection
        if database != 'none' and database != 'sqlite':
            # Stateful apps better on Kubernetes
            return 'kubernetes'
        
        if framework in ['flask', 'express', 'fastapi']:
            # Stateless APIs good for Code Engine
            return 'code-engine'
        
        # Default to Code Engine for simplicity
        return 'code-engine'
    
    def _recommend_resources(self, framework: str, database: str) -> Dict:
        """Recommend CPU and memory resources"""
        # Get template or use defaults
        template = self.RESOURCE_TEMPLATES.get(framework, {'cpu': '0.5', 'memory': '1G'})
        
        # Adjust for database
        if database != 'none':
            # Apps with databases need more resources
            cpu = float(template['cpu'])
            memory_val = int(template['memory'].rstrip('GM'))
            memory_unit = template['memory'][-1]
            
            cpu = min(cpu * 1.5, 2)  # Max 2 vCPU
            memory_val = min(int(memory_val * 1.5), 4)
            
            template = {
                'cpu': str(cpu),
                'memory': f"{memory_val}{memory_unit}"
            }
        
        return {
            'cpu': template['cpu'],
            'memory': template['memory'],
            'cpu_unit': 'vCPU',
            'memory_unit': 'GB'
        }
    
    def _recommend_scaling(self, platform: str, framework: str) -> Dict:
        """Recommend scaling configuration"""
        if platform == 'code-engine':
            return {
                'min_replicas': 0,  # Scale to zero for cost savings
                'max_replicas': 10,
                'target_cpu_percent': 70,
                'scale_down_delay': '30s'
            }
        else:  # kubernetes
            return {
                'min_replicas': 2,  # HA with 2 minimum
                'max_replicas': 20,
                'target_cpu_percent': 70,
                'scale_down_delay': '60s'
            }
    
    def _get_kb_recommendations(self, language: str, framework: str) -> List[str]:
        """Get recommendations from knowledge base via RAG"""
        recommendations = []
        
        # Query knowledge base for language-specific recommendations
        query = f"{language} {framework} deployment production"
        kb_result = self.query_knowledge_base(query, language)
        
        # Extract recommendations based on framework
        if framework == 'flask':
            recommendations = [
                "Use gunicorn as production WSGI server with 2-4 workers",
                "Set PYTHONUNBUFFERED=1 for proper logging",
                "Implement health check endpoint at /health",
                "Use python:3.11-slim for smaller image size"
            ]
        elif framework == 'express':
            recommendations = [
                "Set NODE_ENV=production for optimizations",
                "Use PM2 or clustering for better performance",
                "Implement graceful shutdown handlers",
                "Use node:18-alpine for smaller image size"
            ]
        elif framework == 'fastapi':
            recommendations = [
                "Use uvicorn with --workers flag for concurrency",
                "Enable automatic API documentation at /docs",
                "Implement async endpoints for I/O operations",
                "Configure CORS if frontend is separate"
            ]
        else:
            recommendations = [
                "Follow framework-specific best practices",
                "Implement proper error handling",
                "Configure appropriate timeout values",
                "Enable monitoring and logging"
            ]
        
        return recommendations
    
    def _generate_best_practices(self, language: str, framework: str, platform: str) -> List[str]:
        """Generate best practices from knowledge base"""
        practices = [
            "Use specific version tags, avoid :latest",
            "Run containers as non-root user",
            "Set resource limits to prevent resource exhaustion",
            "Implement liveness and readiness probes",
            "Use secrets management for sensitive data"
        ]
        
        # Add platform-specific practices
        if platform == 'code-engine':
            practices.append("Configure auto-scaling for cost optimization")
            practices.append("Use built-in TLS certificates")
        else:
            practices.append("Deploy minimum 2 replicas for high availability")
            practices.append("Configure network policies for security")
        
        return practices
    
    def _estimate_cost(self, resources: Dict, scaling: Dict) -> str:
        """Estimate relative cost level"""
        cpu = float(resources['cpu'])
        memory_val = int(resources['memory'].rstrip('GM'))
        max_replicas = scaling['max_replicas']
        
        # Simple cost estimation
        cost_score = (cpu * 10) + (memory_val * 2) + (max_replicas * 0.5)
        
        if cost_score < 15:
            return 'low'
        elif cost_score < 40:
            return 'medium'
        else:
            return 'high'
    
    def _build_rationale(self, analysis: Dict, platform: str) -> str:
        """Build explanation for platform choice"""
        framework = analysis.get('framework', 'unknown')
        database = analysis.get('database', 'none')
        
        reasons = []
        
        if platform == 'code-engine':
            reasons.append(f"{framework} is well-suited for serverless deployment")
            reasons.append("Code Engine provides automatic scaling and cost optimization")
            if database == 'none':
                reasons.append("Stateless application benefits from scale-to-zero")
        else:
            reasons.append(f"Kubernetes provides better control for {framework} applications")
            if database != 'none':
                reasons.append(f"Stateful app with {database} database needs persistent storage")
            reasons.append("Complex applications benefit from Kubernetes orchestration")
        
        return '. '.join(reasons) + '.'


# Main function that ADK will call
def recommend_architecture(analysis_json: str) -> str:
    """
    ADK Tool Function: Recommend deployment architecture
    
    Args:
        analysis_json: JSON string from Analyst Agent
    
    Returns:
        JSON string with architecture recommendations
    """
    try:
        analysis = json.loads(analysis_json)
    except:
        # If not JSON, create mock analysis
        analysis = {
            'language': 'python',
            'framework': 'flask',
            'database': 'postgresql'
        }
    
    architect = DeploymentArchitect()
    return architect.recommend_architecture(analysis)


def query_knowledge_base(query: str, doc_type: str = None) -> str:
    """
    ADK Tool Function: Query knowledge base
    
    Args:
        query: Search query
        doc_type: Document type filter
    
    Returns:
        Relevant knowledge snippet
    """
    architect = DeploymentArchitect()
    return architect.query_knowledge_base(query, doc_type)


# Test function
if __name__ == "__main__":
    print("Testing Architect Agent:")
    print("\n1. Testing with Flask app:")
    
    sample_analysis = {
        'language': 'python',
        'framework': 'flask',
        'database': 'postgresql',
        'port': 5000
    }
    
    result = recommend_architecture(json.dumps(sample_analysis))
    print(result)
    
    print("\n2. Testing knowledge base query:")
    kb_result = query_knowledge_base("python flask production deployment")
    print(kb_result)