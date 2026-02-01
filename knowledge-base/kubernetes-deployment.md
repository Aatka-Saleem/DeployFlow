# Kubernetes Deployment Guide

## Basic Deployment Structure

### Minimal Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-name
  labels:
    app: app-name
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-name
  template:
    metadata:
      labels:
        app: app-name
    spec:
      containers:
      - name: app-name
        image: registry.example.com/app-name:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### Service Definition
```yaml
apiVersion: v1
kind: Service
metadata:
  name: app-name-service
spec:
  selector:
    app: app-name
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

## Resource Requests and Limits

### Small Application
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Medium Application
```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 2Gi
```

### Large/ML Application
```yaml
resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 4000m
    memory: 8Gi
```

## Auto-Scaling

### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-name-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-name
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Health Checks

### Liveness and Readiness Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## Configuration Management

### ConfigMap for Environment Variables
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  PORT: "8080"
  ENVIRONMENT: "production"
```

### Using ConfigMap in Deployment
```yaml
spec:
  containers:
  - name: app-name
    envFrom:
    - configMapRef:
        name: app-config
```

### Secrets for Sensitive Data
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  API_KEY: base64encodedvalue
  DB_PASSWORD: base64encodedvalue
```

## Best Practices

### Replica Count
- **Development**: 1 replica
- **Staging**: 2 replicas
- **Production**: 3+ replicas (odd numbers for quorum)

### Update Strategy
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### Labels and Selectors
Always use consistent labels:
```yaml
labels:
  app: app-name
  version: v1.0.0
  environment: production
  tier: backend
```

### Resource Naming
- Use lowercase with hyphens: `my-app-deployment`
- Include environment: `my-app-prod-deployment`
- Be descriptive and consistent

## IBM Cloud Kubernetes Service (IKS)

### Use IBM Container Registry
```yaml
spec:
  containers:
  - name: app
    image: us.icr.io/namespace/app-name:v1.0.0
```

### Storage Classes
- `ibmc-block-silver`: Standard block storage
- `ibmc-file-bronze`: Shared file storage
- Use persistent volumes for databases

### Load Balancer
IKS automatically provisions IBM Cloud Load Balancer for `type: LoadBalancer` services.

## Common Patterns

### Sidecar Container
```yaml
containers:
- name: app
  image: app:v1
- name: logging-sidecar
  image: fluent-bit:latest
```

### Init Container
```yaml
initContainers:
- name: migration
  image: app:v1
  command: ['python', 'migrate.py']
```

### Multiple Replicas for HA
For critical services, always run minimum 3 replicas across availability zones.
