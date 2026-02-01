# IBM Code Engine Deployment Guide

## What is Code Engine?
IBM Code Engine is a fully managed, serverless platform that runs containerized workloads, including web apps, microservices, event-driven functions, and batch jobs.

## When to Use Code Engine

### Perfect For:
- Web applications with variable traffic
- Microservices and APIs
- Batch processing jobs
- Event-driven workloads
- Applications that scale to zero

### Not Ideal For:
- Long-running stateful services (use IKS instead)
- Applications requiring persistent storage
- Complex networking requirements
- GPU-intensive workloads (use IKS with GPU nodes)

## Deployment Methods

### Method 1: From Container Registry
```bash
ibmcloud ce application create \
  --name my-app \
  --image us.icr.io/namespace/my-app:v1.0.0 \
  --registry-secret my-registry-secret \
  --port 8080 \
  --cpu 0.5 \
  --memory 1G \
  --min-scale 0 \
  --max-scale 10
```

### Method 2: From Source Code (Buildpacks)
```bash
ibmcloud ce application create \
  --name my-app \
  --build-source https://github.com/user/repo \
  --build-context-dir /app \
  --port 8080
```

### Method 3: From Local Directory
```bash
ibmcloud ce application create \
  --name my-app \
  --build-source . \
  --port 8080
```

## Resource Configuration

### Small Application (API, Static Site)
```bash
--cpu 0.25 --memory 512M --min-scale 0 --max-scale 5
```

### Medium Application (Web App, Microservice)
```bash
--cpu 0.5 --memory 1G --min-scale 1 --max-scale 10
```

### Large Application (Data Processing, ML Inference)
```bash
--cpu 2 --memory 4G --min-scale 1 --max-scale 20
```

## Scaling Configuration

### Scale to Zero (Cost Optimization)
```bash
--min-scale 0 --max-scale 10 --concurrency 100
```
**Use when**: Low traffic, cost is priority
**Cost**: Pay only when processing requests

### Always-On (Low Latency)
```bash
--min-scale 2 --max-scale 10 --concurrency 100
```
**Use when**: Need consistent response times
**Cost**: Always running, higher cost

### Auto-Scale Based on Traffic
```bash
--min-scale 1 --max-scale 50 --concurrency 50 --scale-down-delay 30s
```
**Use when**: Variable traffic patterns
**Cost**: Scales with demand

## Environment Variables

### Set Environment Variables
```bash
ibmcloud ce application create \
  --name my-app \
  --image my-image:latest \
  --env LOG_LEVEL=info \
  --env NODE_ENV=production \
  --env-from-configmap my-config \
  --env-from-secret my-secret
```

### Using ConfigMaps
```bash
# Create ConfigMap
ibmcloud ce configmap create \
  --name app-config \
  --from-literal LOG_LEVEL=info \
  --from-literal PORT=8080

# Use in Application
ibmcloud ce application update \
  --name my-app \
  --env-from-configmap app-config
```

### Using Secrets
```bash
# Create Secret
ibmcloud ce secret create \
  --name app-secrets \
  --from-literal API_KEY=secret-value

# Use in Application
ibmcloud ce application update \
  --name my-app \
  --env-from-secret app-secrets
```

## Registry Secret for Private Images

### Create Registry Secret
```bash
ibmcloud ce registry create \
  --name my-registry-secret \
  --server us.icr.io \
  --username iamapikey \
  --password <IBM_CLOUD_API_KEY>
```

### Use Registry Secret
```bash
ibmcloud ce application create \
  --name my-app \
  --image us.icr.io/namespace/my-app:v1.0.0 \
  --registry-secret my-registry-secret
```

## Health Checks

Code Engine automatically performs health checks on port specified:
```bash
--port 8080
```

### Custom Health Endpoint
Ensure your app responds to GET requests on `/`:
```python
# Python Flask
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200
```

```javascript
// Node.js Express
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});
```

## Networking

### Public Endpoint
Default - app gets public URL:
```
https://my-app.random-hash.us-south.codeengine.appdomain.cloud
```

### Custom Domain
```bash
ibmcloud ce application update \
  --name my-app \
  --domain-mapping my-domain.com
```

### Private Endpoint (Project-Only)
```bash
ibmcloud ce application create \
  --name my-app \
  --cluster-local
```

## Jobs (Batch Processing)

### Create Job
```bash
ibmcloud ce job create \
  --name data-processor \
  --image us.icr.io/namespace/processor:v1 \
  --cpu 2 \
  --memory 4G \
  --array-indices 1-10
```

### Run Job
```bash
ibmcloud ce jobrun submit \
  --name process-data-run \
  --job data-processor
```

## Event-Driven Applications

### Subscribe to COS Events
```bash
ibmcloud ce subscription cos create \
  --name cos-sub \
  --destination my-app \
  --bucket my-bucket
```

### Subscribe to Cron Events
```bash
ibmcloud ce subscription cron create \
  --name daily-job \
  --destination my-app \
  --schedule '0 0 * * *' \
  --data '{"task":"daily-report"}'
```

## Best Practices

### Performance
1. Use proper health checks
2. Set appropriate concurrency (50-100 for most apps)
3. Use build caching for faster deployments
4. Enable scale-to-zero for cost savings

### Security
1. Always use registry secrets for private images
2. Store sensitive data in Secrets, not ConfigMaps
3. Use least-privilege IAM policies
4. Enable audit logging

### Cost Optimization
1. Set min-scale to 0 for dev/test
2. Use appropriate CPU/memory (don't over-provision)
3. Monitor usage with IBM Cloud Monitoring
4. Use jobs instead of applications for batch work

### Reliability
1. Set min-scale > 0 for production
2. Use multiple replicas (min 2)
3. Implement graceful shutdown
4. Use health checks

## Monitoring and Logging

### View Logs
```bash
ibmcloud ce application logs --name my-app --follow
```

### Metrics
View in IBM Cloud Console:
- Request count
- Response times
- Error rates
- Instance count
- CPU/Memory usage

## Common Issues and Solutions

### App Won't Start
- Check logs: `ibmcloud ce app logs --name my-app`
- Verify PORT environment variable
- Ensure health endpoint responds

### High Costs
- Reduce min-scale to 0
- Lower max-scale
- Optimize resource requests
- Use concurrency settings

### Slow Response Times
- Increase min-scale (avoid cold starts)
- Add more CPU/memory
- Check application performance

### Registry Pull Failures
- Verify registry secret
- Check image exists
- Ensure proper permissions

## Migration from Kubernetes

### Differences from K8s
- No need for Services (automatic)
- No need for Ingress (automatic)
- Simplified scaling configuration
- Built-in TLS certificates
- Serverless model (scale to zero)

### Converting K8s to Code Engine
```bash
# Instead of kubectl apply
ibmcloud ce application create \
  --name <from deployment name> \
  --image <from container image> \
  --port <from containerPort> \
  --env <from env vars>
```

## Pricing Model
- **vCPU-seconds**: Charged per second of CPU use
- **GB-seconds**: Charged per second of memory use
- **Requests**: Free tier included
- **Scale to zero**: No charges when not running

## Example: Python Flask App
```bash
# Create application
ibmcloud ce project create --name my-project
ibmcloud ce project select --name my-project

# Create registry secret
ibmcloud ce registry create --name icr-secret \
  --server us.icr.io \
  --username iamapikey \
  --password $IBM_CLOUD_API_KEY

# Deploy from registry
ibmcloud ce application create \
  --name flask-app \
  --image us.icr.io/namespace/flask-app:v1.0.0 \
  --registry-secret icr-secret \
  --port 8080 \
  --cpu 0.5 \
  --memory 1G \
  --min-scale 0 \
  --max-scale 10 \
  --env FLASK_ENV=production

# Get URL
ibmcloud ce application get --name flask-app
```
