# Security Checklist for Container Deployments

## Dockerfile Security

### ✅ Use Official Base Images
```dockerfile
# Good
FROM python:3.11-slim
FROM node:18-alpine

# Bad
FROM random-user/python:latest
```

### ✅ Don't Run as Root
```dockerfile
# Create and use non-root user
RUN useradd -m -u 1001 appuser
USER appuser
```

### ✅ Use Specific Image Tags
```dockerfile
# Good
FROM python:3.11-slim

# Bad
FROM python:latest
FROM python
```

### ✅ No Hardcoded Secrets
```dockerfile
# Bad - NEVER DO THIS
ENV API_KEY=sk-12345
ENV DB_PASSWORD=secretpassword

# Good - Use environment variables at runtime
ENV API_KEY=${API_KEY}
```

### ✅ Minimize Image Layers
```dockerfile
# Good
RUN apt-get update && \
    apt-get install -y curl wget && \
    rm -rf /var/lib/apt/lists/*

# Bad
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
```

### ✅ Use .dockerignore
```
.git
.env
*.log
node_modules
__pycache__
.pytest_cache
secrets/
```

## Kubernetes Security

### ✅ Resource Limits
Always set limits to prevent resource exhaustion:
```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 100m
    memory: 128Mi
```

### ✅ Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
```

### ✅ Network Policies
Restrict network access:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
```

### ✅ Use Secrets for Sensitive Data
```yaml
# Never use ConfigMaps for secrets
# Use Kubernetes Secrets instead
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  api-key: base64encodedvalue
```

## Common Vulnerabilities to Check

### Critical Issues
- ❌ Running containers as root
- ❌ Hardcoded secrets in code or Dockerfiles
- ❌ Using `:latest` tag in production
- ❌ Exposed sensitive ports (database ports, admin panels)
- ❌ Missing security patches in base images

### High Priority Issues
- ⚠️ No resource limits defined
- ⚠️ Outdated dependencies with known CVEs
- ⚠️ Allowing privilege escalation
- ⚠️ No network policies
- ⚠️ Writable root filesystem

### Medium Priority Issues
- ⚠️ Missing health checks
- ⚠️ No image scanning in CI/CD
- ⚠️ Excessive permissions
- ⚠️ Logging sensitive information
- ⚠️ No TLS/SSL for communication

## Security Scanning

### Image Vulnerability Scanning
Tools to use:
- **Trivy**: `trivy image python:3.11-slim`
- **IBM Cloud Container Registry**: Automatic scanning
- **Clair**: Open-source scanner
- **Snyk**: Commercial tool

### Dependency Scanning
```bash
# Python
pip-audit

# Node.js
npm audit
npm audit fix

# General
snyk test
```

### Static Code Analysis
```bash
# Python
bandit -r .
pylint app/

# Node.js
npm run lint
eslint .

# General
SonarQube
```

## Environment-Specific Security

### Development
- Can use relaxed security for faster iteration
- Still no hardcoded secrets
- Use test credentials only

### Staging
- Mirror production security settings
- Test security configurations
- Validate secrets management

### Production
- Enforce all security policies
- Enable audit logging
- Use pod security policies
- Implement network segmentation
- Regular security scans

## Secret Management Best Practices

### IBM Cloud Secrets Manager
```bash
# Store secrets in IBM Secrets Manager
ibmcloud secrets-manager secret-create \
  --secret-type=arbitrary \
  --name=api-key \
  --payload='{"secret":"value"}'
```

### GitHub Secrets for CI/CD
Store in repository Settings > Secrets:
- `IBM_CLOUD_API_KEY`
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`

### Never Commit Secrets
```bash
# Use git-secrets to prevent accidental commits
git secrets --scan
```

## Compliance Checks

### Must-Have for Production
1. ✅ No root user in containers
2. ✅ All secrets in secure storage (not in code)
3. ✅ TLS/SSL for all external communication
4. ✅ Regular vulnerability scanning
5. ✅ Resource limits on all containers
6. ✅ Network policies in place
7. ✅ Audit logging enabled
8. ✅ No `:latest` tags
9. ✅ Health checks configured
10. ✅ Minimal base images (Alpine, Slim)

## Quick Security Checklist

Before deploying, verify:
- [ ] Using specific image tags (not `:latest`)
- [ ] Running as non-root user
- [ ] No hardcoded secrets
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Dependencies up to date
- [ ] Image scanned for vulnerabilities
- [ ] Network policies in place
- [ ] Secrets stored securely
- [ ] TLS enabled for external access
- [ ] Logging configured (no sensitive data)
- [ ] Minimal permissions granted

## Security Tools Integration

### In CI/CD Pipeline
```yaml
- name: Security Scan
  run: |
    trivy image --severity HIGH,CRITICAL my-image:tag
    bandit -r ./src
    npm audit --audit-level=high
```

### Runtime Security
- Use IBM Cloud Security Advisor
- Enable Falco for runtime monitoring
- Implement WAF for web applications
- Use service mesh (Istio) for mTLS
