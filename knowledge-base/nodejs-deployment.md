# Node.js Application Deployment Guide

## Overview
Best practices for deploying Node.js applications using containers and IBM Cloud.

## Recommended Dockerfile Structure

### For Express/Fastify Applications
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Start application
CMD ["node", "server.js"]
```

### For Next.js Applications
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000
CMD ["npm", "start"]
```

## Resource Recommendations

### Small Express API
- **CPU**: 0.25 vCPU
- **Memory**: 256MB
- **Replicas**: 2
- **Auto-scaling**: 2-5 pods

### Next.js Web Application
- **CPU**: 0.5 vCPU
- **Memory**: 512MB - 1GB
- **Replicas**: 2
- **Auto-scaling**: 2-8 pods

### Real-time Socket.io Server
- **CPU**: 1 vCPU
- **Memory**: 1GB
- **Replicas**: 3+
- **Sticky sessions**: Required

## Common Dependencies
- **Express**: Lightweight, use PM2 or clustering
- **Fastify**: High performance, built-in clustering
- **Next.js**: Use production build
- **Socket.io**: Needs sticky sessions for scaling
- **GraphQL**: May need more memory

## Environment Variables
- `NODE_ENV`: Set to 'production'
- `PORT`: Application port (default 3000)
- `LOG_LEVEL`: info or error
- `MAX_OLD_SPACE_SIZE`: Memory limit for Node

## IBM Code Engine Settings
- Use Node.js buildpack auto-detection
- Set NODE_ENV=production
- Enable clustering for better performance
- Use CDN for static assets (Next.js)
- Consider serverless for low-traffic apps

## Performance Tips
- Use `npm ci` instead of `npm install`
- Remove dev dependencies in production
- Use Alpine Linux for smaller images
- Enable gzip compression
- Implement proper logging
