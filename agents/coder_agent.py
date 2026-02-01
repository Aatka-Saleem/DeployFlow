"""
Coder Agent - Configuration File Generator
Generates Dockerfile, Kubernetes manifests, and CI/CD pipelines
"""

import json
import os
from typing import Dict


class ConfigurationGenerator:
    """Generates deployment configuration files from templates"""
    
    def __init__(self, templates_path: str = None):
        """
        Initialize generator with templates
        
        Args:
            templates_path: Path to template files
        """
        # Find templates relative to this file
        if templates_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_path = os.path.join(os.path.dirname(current_dir), 'templates')
        
        self.templates_path = templates_path
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load EVERY file in the templates folder ending in .template or .simple"""
        if not os.path.exists(self.templates_path):
            print(f"Warning: Templates path not found: {self.templates_path}")
            return
    
        try:
            # 1. Get a list of every filename in the folder
            all_files = os.listdir(self.templates_path)
        
            # 2. Define what extensions we want to load
            extensions = ('.template', '.simple')
        
            for filename in all_files:
                # 3. Check if the file ends with our allowed extensions
                if filename.endswith(extensions):
                    filepath = os.path.join(self.templates_path, filename)
                
                    # 4. Create a clean "Key" for the dictionary (e.g., 'k8s_deployment')
                    # This removes the extension from the name
                    key = filename
                    for ext in extensions:
                        key = key.replace(ext, '')
                
                    # 5. Read the file and store it
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.templates[key] = f.read()
        
            print(f"✅ Loaded {len(self.templates)} templates: {list(self.templates.keys())}")
        
        except Exception as e:
            print(f"❌ Error loading templates: {e}")
    
    
    
    def generate_dockerfile(self, analysis: Dict, recommendations: Dict) -> str:
        """
        Generate Dockerfile based on analysis and recommendations
        
        Args:
            analysis: From Analyst Agent
            recommendations: From Architect Agent
        
        Returns:
            Dockerfile content as string
        """
        language = analysis.get('language', 'python')
        framework = analysis.get('framework', 'flask')
        main_file = analysis.get('main_file', 'app.py')
        port = analysis.get('port', 8080)
        language_version = analysis.get('language_version', '3.11')
        
        # Select appropriate template
        if language == 'python':
            template = self.templates.get('dockerfile_python', self._get_default_python_dockerfile())
            
            # Determine app module for gunicorn
            app_module = main_file.replace('.py', '') if main_file.endswith('.py') else 'app'
            
            # Replace template variables
            dockerfile = template.replace('{PYTHON_VERSION}', language_version)
            dockerfile = dockerfile.replace('{PORT}', str(port))
            dockerfile = dockerfile.replace('{APP_MODULE}', app_module)
            dockerfile = dockerfile.replace('{WORKERS}', '2')
            
        elif language == 'nodejs':
            template = self.templates.get('dockerfile_nodejs', self._get_default_nodejs_dockerfile())
            
            node_version = language_version if language_version else '18'
            
            # Replace template variables
            dockerfile = template.replace('{NODE_VERSION}', node_version)
            dockerfile = dockerfile.replace('{PORT}', str(port))
            dockerfile = dockerfile.replace('{MAIN_FILE}', main_file)
        
        else:
            # Generic Dockerfile
            dockerfile = f"""# Generic Dockerfile for {language}
FROM alpine:latest
WORKDIR /app
COPY . .
EXPOSE {port}
CMD ["echo", "Configure for {language}"]
"""
        
        return dockerfile
    
    def generate_kubernetes(self, analysis: Dict, recommendations: Dict) -> str:
        """
        Generate Kubernetes deployment manifest
        
        Args:
            analysis: From Analyst Agent
            recommendations: From Architect Agent
        
        Returns:
            Kubernetes YAML content
        """
        # Extract values
        app_name = "my-app"  # Could be extracted from repo name
        image_url = f"us.icr.io/namespace/{app_name}:latest"
        port = analysis.get('port', 8080)
        
        resources = recommendations.get('resources', {})
        cpu_request = resources.get('cpu', '0.5')
        memory_request = resources.get('memory', '1G')
        
        # CPU limit is typically 2x request
        cpu_limit = str(float(cpu_request) * 2)
        # Memory limit is typically 1.5x request
        memory_limit = memory_request  # Keep same for simplicity
        
        scaling = recommendations.get('scaling', {})
        replicas = scaling.get('min_replicas', 2)
        min_replicas = scaling.get('min_replicas', 2)
        max_replicas = scaling.get('max_replicas', 10)
        
        # Generate Kubernetes YAML
        k8s_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
    version: v1
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
        version: v1
    spec:
      containers:
      - name: {app_name}
        image: {image_url}
        ports:
        - containerPort: {port}
          protocol: TCP
        env:
        - name: PORT
          value: "{port}"
        resources:
          requests:
            cpu: {cpu_request}
            memory: {memory_request}
          limits:
            cpu: {cpu_limit}
            memory: {memory_limit}
        livenessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
---
apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
  labels:
    app: {app_name}
spec:
  type: LoadBalancer
  selector:
    app: {app_name}
  ports:
  - port: 80
    targetPort: {port}
    protocol: TCP
    name: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {app_name}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {app_name}
  minReplicas: {min_replicas}
  maxReplicas: {max_replicas}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""
        return k8s_yaml
    
    def generate_cicd(self, analysis: Dict, recommendations: Dict) -> str:
        """
        Generate GitHub Actions CI/CD pipeline
        
        Args:
            analysis: From Analyst Agent
            recommendations: From Architect Agent
        
        Returns:
            GitHub Actions YAML content
        """
        language = analysis.get('language', 'python')
        framework = analysis.get('framework', 'flask')
        language_version = analysis.get('language_version', '3.11')
        platform = recommendations.get('platform', 'code-engine')
        
        app_name = "my-app"
        
        # Generate GitHub Actions workflow
        if language == 'python':
            test_setup = f"""    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '{language_version}'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest flake8
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Run tests
      run: |
        pytest --verbose"""
        
        elif language == 'nodejs':
            test_setup = f"""    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '{language_version if language_version else "18"}'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint --if-present
    
    - name: Run tests
      run: npm test --if-present"""
        
        else:
            test_setup = """    - name: Run tests
      run: echo "Configure tests for your language" """
        
        # Deployment section
        if platform == 'code-engine':
            deploy_cmd = f"""ibmcloud ce application update --name {app_name} \\
          --image ${{{{ env.REGISTRY }}}}/${{{{ env.NAMESPACE }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}} \\
          --registry-secret icr-secret \\
          --port 8080 || \\
        ibmcloud ce application create --name {app_name} \\
          --image ${{{{ env.REGISTRY }}}}/${{{{ env.NAMESPACE }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}} \\
          --registry-secret icr-secret \\
          --port 8080"""
        else:
            deploy_cmd = f"""kubectl apply -f kubernetes-deployment.yaml
        kubectl set image deployment/{app_name} {app_name}=${{{{ env.REGISTRY }}}}/${{{{ env.NAMESPACE }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}}
        kubectl rollout status deployment/{app_name}"""
        
        cicd_yaml = f"""name: Build and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: us.icr.io
  NAMESPACE: my-namespace
  IMAGE_NAME: {app_name}

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
{test_setup}

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to IBM Cloud Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{{{ env.REGISTRY }}}}
        username: iamapikey
        password: ${{{{ secrets.IBM_CLOUD_API_KEY }}}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{{{ env.REGISTRY }}}}/${{{{ env.NAMESPACE }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Scan image for vulnerabilities
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{{{ env.REGISTRY }}}}/${{{{ env.NAMESPACE }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}}
        format: 'sarif'
        output: 'trivy-results.sarif'

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Install IBM Cloud CLI
      run: |
        curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
        ibmcloud plugin install {'code-engine' if platform == 'code-engine' else 'kubernetes-service'} -f
    
    - name: Authenticate with IBM Cloud
      run: |
        ibmcloud login --apikey ${{{{ secrets.IBM_CLOUD_API_KEY }}}} -r us-south
        ibmcloud target -g Default
    
    - name: Deploy
      run: |
        {deploy_cmd}
"""
        return cicd_yaml
    
    def generate_configs(self, analysis: Dict, recommendations: Dict) -> str:
        """
        Generate all configuration files
        
        Args:
            analysis: From Analyst Agent
            recommendations: From Architect Agent
        
        Returns:
            JSON string with all generated configs
        """
        dockerfile = self.generate_dockerfile(analysis, recommendations)
        kubernetes = self.generate_kubernetes(analysis, recommendations)
        cicd = self.generate_cicd(analysis, recommendations)
        
        result = {
            'dockerfile': dockerfile,
            'kubernetes': kubernetes,
            'cicd': cicd,
            'summary': f"Generated configs for {analysis.get('language')} {analysis.get('framework')} app"
        }
        
        return json.dumps(result, indent=2)
    
    def _get_default_python_dockerfile(self) -> str:
        """Fallback Python Dockerfile template"""
        return """FROM python:{PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE {PORT}

ENV PYTHONUNBUFFERED=1
ENV PORT={PORT}

CMD ["gunicorn", "-b", "0.0.0.0:{PORT}", "--workers", "{WORKERS}", "{APP_MODULE}:app"]
"""
    
    def _get_default_nodejs_dockerfile(self) -> str:
        """Fallback Node.js Dockerfile template"""
        return """FROM node:{NODE_VERSION}-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
RUN chown -R nodejs:nodejs /app
USER nodejs

EXPOSE {PORT}

ENV NODE_ENV=production
ENV PORT={PORT}

CMD ["node", "{MAIN_FILE}"]
"""


# Main functions that ADK will call
def generate_configs(analysis_json: str, recommendations_json: str) -> str:
    """
    ADK Tool Function: Generate all configuration files
    
    Args:
        analysis_json: JSON from Analyst Agent
        recommendations_json: JSON from Architect Agent
    
    Returns:
        JSON string with all generated configs
    """
    try:
        analysis = json.loads(analysis_json)
        recommendations = json.loads(recommendations_json)
    except:
        # Mock data for testing
        analysis = {
            'language': 'python',
            'framework': 'flask',
            'port': 5000,
            'main_file': 'app.py',
            'language_version': '3.11'
        }
        recommendations = {
            'platform': 'code-engine',
            'resources': {'cpu': '0.5', 'memory': '1G'},
            'scaling': {'min_replicas': 2, 'max_replicas': 10}
        }
    
    generator = ConfigurationGenerator()
    return generator.generate_configs(analysis, recommendations)


def generate_dockerfile(analysis_json: str, recommendations_json: str) -> str:
    """Generate only Dockerfile"""
    analysis = json.loads(analysis_json)
    recommendations = json.loads(recommendations_json)
    generator = ConfigurationGenerator()
    return generator.generate_dockerfile(analysis, recommendations)


def generate_kubernetes(analysis_json: str, recommendations_json: str) -> str:
    """Generate only Kubernetes manifest"""
    analysis = json.loads(analysis_json)
    recommendations = json.loads(recommendations_json)
    generator = ConfigurationGenerator()
    return generator.generate_kubernetes(analysis, recommendations)


def generate_cicd(analysis_json: str, recommendations_json: str) -> str:
    """Generate only CI/CD pipeline"""
    analysis = json.loads(analysis_json)
    recommendations = json.loads(recommendations_json)
    generator = ConfigurationGenerator()
    return generator.generate_cicd(analysis, recommendations)


# Test function
if __name__ == "__main__":
    print("Testing Coder Agent:\n")
    
    # Sample data
    sample_analysis = {
        'language': 'python',
        'framework': 'flask',
        'port': 5000,
        'main_file': 'app.py',
        'language_version': '3.11',
        'database': 'postgresql'
    }
    
    sample_recommendations = {
        'platform': 'kubernetes',
        'resources': {'cpu': '0.75', 'memory': '1G'},
        'scaling': {'min_replicas': 2, 'max_replicas': 20}
    }
    
    result = generate_configs(
        json.dumps(sample_analysis),
        json.dumps(sample_recommendations)
    )
    
    configs = json.loads(result)
    
    print("=" * 60)
    print("DOCKERFILE:")
    print("=" * 60)
    print(configs['dockerfile'])
    
    print("\n" + "=" * 60)
    print("KUBERNETES MANIFEST:")
    print("=" * 60)
    print(configs['kubernetes'][:500] + "...\n[truncated]")
    
    print("\n" + "=" * 60)
    print("CI/CD PIPELINE:")
    print("=" * 60)
    print(configs['cicd'][:500] + "...\n[truncated]")