# CI/CD Pipeline Guide

## GitHub Actions for Container Deployment

### Basic Build and Push Workflow
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: us.icr.io
  NAMESPACE: my-namespace
  IMAGE_NAME: my-app

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to IBM Cloud Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: iamapikey
        password: ${{ secrets.IBM_CLOUD_API_KEY }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/${{ env.IMAGE_NAME }}
        tags: |
          type=sha,prefix={{branch}}-
          type=ref,event=branch
          type=semver,pattern={{version}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### Python Application Testing
```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Run tests
      run: |
        pytest --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Node.js Application Testing
```yaml
name: Node.js CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Run tests
      run: npm test
    
    - name: Build
      run: npm run build --if-present
```

### Deploy to IBM Code Engine
```yaml
name: Deploy to Code Engine

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Install IBM Cloud CLI
      run: |
        curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
        ibmcloud plugin install code-engine
    
    - name: Authenticate with IBM Cloud
      run: |
        ibmcloud login --apikey ${{ secrets.IBM_CLOUD_API_KEY }} -r us-south
        ibmcloud target -g Default
    
    - name: Deploy to Code Engine
      run: |
        ibmcloud ce project select --name my-project
        ibmcloud ce application update --name my-app \
          --image us.icr.io/my-namespace/my-app:latest \
          --registry-secret my-registry-secret
```

## Pipeline Best Practices

### Secrets Management
Store these as GitHub Secrets:
- `IBM_CLOUD_API_KEY`: IBM Cloud API key
- `DOCKER_USERNAME`: Container registry username
- `DOCKER_PASSWORD`: Container registry password

### Branch Strategy
```yaml
on:
  push:
    branches:
      - main        # Production
      - develop     # Staging
      - 'release/*' # Release candidates
```

### Environment-Specific Deployments
```yaml
jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to Staging
        run: deploy-to-staging.sh

  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: deploy-staging
    steps:
      - name: Deploy to Production
        run: deploy-to-production.sh
```

### Container Scanning
```yaml
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload scan results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

### Build Caching
Use layer caching for faster builds:
```yaml
- name: Build with cache
  uses: docker/build-push-action@v4
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Deployment Strategies

### Rolling Update
Default for Kubernetes - gradually replace old pods with new ones.

### Blue-Green Deployment
```yaml
- name: Deploy to Green
  run: kubectl apply -f green-deployment.yaml

- name: Test Green
  run: ./test-green-deployment.sh

- name: Switch Traffic to Green
  run: kubectl patch service app --type='json' -p='[{"op": "replace", "path": "/spec/selector/version", "value":"green"}]'
```

### Canary Deployment
Deploy to small percentage of users first:
```yaml
- name: Deploy Canary (10%)
  run: kubectl set image deployment/app-canary app=app:$VERSION

- name: Monitor Metrics
  run: ./monitor-canary.sh

- name: Promote if Successful
  run: kubectl set image deployment/app app=app:$VERSION
```

## Monitoring Integration

### Add Deployment Notifications
```yaml
- name: Notify Slack on Success
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: custom
    custom_payload: |
      {
        text: "Deployment successful! Version: ${{ github.sha }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Rollback Strategy

### Automatic Rollback on Failure
```yaml
- name: Deploy
  id: deploy
  run: kubectl apply -f deployment.yaml

- name: Wait for Rollout
  run: kubectl rollout status deployment/app --timeout=5m

- name: Rollback on Failure
  if: failure()
  run: kubectl rollout undo deployment/app
```
