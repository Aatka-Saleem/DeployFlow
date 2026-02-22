# Node.js Deployment Patterns – DeployFlow Recommendations

## Recommended patterns

1. Express / Fastify
   - Base image: node:20-alpine or node:22-alpine
   - Use npm ci --only=production
   - CMD: ["node", "server.js"] or ["npm", "start"]
   - Consider PM2 in larger apps (but adds complexity)

2. Next.js
   - Two main patterns:
     a) Full server (SSR/API routes)
        - Build with next build
        - CMD: ["npm", "start"] or ["node", ".next/standalone/server.js"]
     b) Static export (when no server needed)
        - next export → out/
        - Serve with nginx or caddy

3. Vite / React SPA
   - Build → dist/
   - Serve with nginx (recommended) or simple node static server

## Common environment variables

- NODE_ENV=production
- PORT (fallback 3000)
- NEXT_PUBLIC_ variables (client-side)
- DATABASE_URL / REDIS_URL