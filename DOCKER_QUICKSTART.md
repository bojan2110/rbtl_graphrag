# Docker Quick Start

## First Time Setup

1. **Ensure `.env` file exists** with all required variables
2. **Build and start:**
   ```bash
   docker-compose up --build
   ```

## Daily Usage

### Start Services
```bash
# Production mode
docker-compose up

# Development mode (with hot-reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart a Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild After Dependency Changes
```bash
# Rebuild and restart
docker-compose up --build

# Or rebuild specific service
docker-compose build backend
docker-compose up backend
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8001
lsof -i :3003

# Stop conflicting services or change ports in docker-compose.yml
```

### Clean Start
```bash
# Stop and remove containers, volumes, networks
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full clean rebuild
docker-compose down -v --rmi all
docker-compose up --build
```

### Check Container Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh
```

