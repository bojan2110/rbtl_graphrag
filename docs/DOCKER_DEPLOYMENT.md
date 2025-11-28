# Docker Deployment Guide

This guide explains how to build and deploy the RBTL GraphRAG application using Docker.

## Architecture

The application consists of two Docker containers:

- **Backend**: FastAPI application (Python 3.13)
- **Frontend**: Next.js application (Node.js 18)

## Prerequisites

- Docker and Docker Compose installed
- `.env` file with all required environment variables

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The application will be available at:
- Frontend: http://localhost:3003 (port 3003 to avoid conflicts)
- Backend API: http://localhost:8001 (port 8001 to avoid conflicts)
- API Docs: http://localhost:8001/docs

**Note:** Ports are mapped to avoid conflicts with:
- Local development (backend: 8000, frontend: 3002)
- Langfuse (3001)

### 2. Stop Services

```bash
docker-compose down
```

## Building Individual Images

### Backend Image

```bash
docker build -f backend/Dockerfile -t rbtl-graphrag-backend:latest .
```

### Frontend Image

```bash
docker build -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -t rbtl-graphrag-frontend:latest .
```

## Environment Variables

Create a `.env` file in the project root with:

```bash
# Neo4j
NEO4J_URI=neo4j+s://your-db-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

# Langfuse
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
PROMPT_LABEL=production

# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=graphrag

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
ENABLE_ANALYTICS_AGENT=false
```

## Cloud Deployment

### Push to Container Registry

```bash
# Tag images
docker tag rbtl-graphrag-backend:latest your-registry/rbtl-graphrag-backend:latest
docker tag rbtl-graphrag-frontend:latest your-registry/rbtl-graphrag-frontend:latest

# Push to registry
docker push your-registry/rbtl-graphrag-backend:latest
docker push your-registry/rbtl-graphrag-frontend:latest
```

### Azure Container Apps

The images can be deployed to Azure Container Apps as described in the [Azure Deployment Guide](operations/azure-deployment.md).

### Kubernetes

Example deployment manifests:

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rbtl-graphrag-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rbtl-graphrag-backend
  template:
    metadata:
      labels:
        app: rbtl-graphrag-backend
    spec:
      containers:
      - name: backend
        image: your-registry/rbtl-graphrag-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: rbtl-graphrag-secrets
```

## Troubleshooting

### Backend won't start

- Check environment variables are set correctly
- Verify Neo4j connection: `docker-compose logs backend`
- Check health endpoint: `curl http://localhost:8000/api/health`

### Frontend can't connect to backend

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend container is running: `docker-compose ps`

### Build fails

- Clear Docker cache: `docker-compose build --no-cache`
- Check Dockerfile paths are correct
- Verify all required files exist

## Development vs Production

### Development (with Hot Reload)

For active development with automatic code reloading:

```bash
# Start with development overrides (hot-reload enabled)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**Features:**
- ✅ Backend auto-reloads on Python file changes (via `--reload` flag)
- ✅ Frontend hot-reloads on React/TypeScript changes
- ✅ Source code mounted as volumes (no rebuild needed for code changes)
- ⚠️ Still need to rebuild if you change `requirements.txt` or `package.json`

**Note:** Code changes are reflected immediately without restarting containers!

### Production

```bash
# Standard production build
docker-compose up --build
```

- No volume mounts (code baked into image)
- Optimized builds
- Production-ready configuration

### Production Best Practices

- Use multi-stage builds (already configured)
- Set `NODE_ENV=production`
- Use production-ready base images
- Configure proper health checks
- Set up logging and monitoring

## Image Sizes

Expected image sizes:
- Backend: ~500-800 MB
- Frontend: ~200-400 MB

To reduce size:
- Use `.dockerignore` (already configured)
- Multi-stage builds (already configured)
- Alpine base images (frontend uses alpine)

