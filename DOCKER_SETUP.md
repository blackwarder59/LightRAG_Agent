# Docker Setup Guide for LightRAG Agent

This guide explains how to run the LightRAG Agent using Docker and Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- At least 4GB of available RAM
- 2GB of available disk space

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd LightRAG_Agent
   ```

2. **Create environment file:**
   ```bash
   cp .env.docker.example .env
   ```

3. **Edit the .env file and add your OpenAI API key:**
   ```bash
   # Edit this line in .env:
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

4. **Start all services:**
   ```bash
   docker-compose up -d
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Neo4j Browser: http://localhost:7474
   - Redis: localhost:6379

## Environment Variables

### Required Variables
```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration (Updated for GPT-4o-mini - 90% cost savings!)
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# LightRAG Configuration
LIGHTRAG_WORKING_DIR=./lightrag_data
LIGHTRAG_MODEL=gpt-4o-mini
LIGHTRAG_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Database Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=lightrag123
REDIS_URL=redis://redis:6379/0

# Application Configuration
DEBUG=false
LOG_LEVEL=info
MAX_UPLOAD_SIZE=10485760  # 10MB
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Frontend Configuration
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://backend:8000
NEXT_PUBLIC_WS_URL=ws://backend:8000
NEXT_PUBLIC_OPENAI_MODEL=gpt-4o-mini
NEXT_PUBLIC_EMBEDDING_MODEL=text-embedding-3-small
```

## Services Overview

### Frontend (Next.js)
- **Port:** 3000
- **Description:** React/Next.js web interface with ChatGPT-like UI
- **Health Check:** `/api/health`

### Backend (FastAPI)
- **Port:** 8000
- **Description:** Python FastAPI server with LightRAG integration
- **Health Check:** `/health`
- **API Docs:** http://localhost:8000/docs

### Neo4j (Graph Database)
- **Ports:** 7474 (HTTP), 7687 (Bolt)
- **Description:** Graph database for knowledge relationships
- **Username:** neo4j
- **Password:** lightrag123
- **Browser:** http://localhost:7474

### Redis (Cache & Sessions)
- **Port:** 6379
- **Description:** In-memory cache and session storage
- **Password:** lightrag123

### ChromaDB (Vector Database)
- **Port:** 8001
- **Description:** Vector database for embeddings
- **Health Check:** `/api/v1/heartbeat`

## Docker Commands

### Start all services:
```bash
docker-compose up -d
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop all services:
```bash
docker-compose down
```

### Rebuild services:
```bash
docker-compose build
docker-compose up -d
```

### Reset data (WARNING: Deletes all data):
```bash
docker-compose down -v
docker volume prune
```

## Development Mode

For development with hot reloading, use the override file:

```bash
# Start in development mode
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Or simply (override is automatically applied)
docker-compose up -d
```

Development mode features:
- Hot reloading for both frontend and backend
- Volume mounts for live code changes
- Debug logging enabled
- Simplified passwords

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check if ports are in use
   lsof -i :3000
   lsof -i :8000
   lsof -i :7474
   ```

2. **Services failing to start:**
   ```bash
   # Check service health
   docker-compose ps
   
   # View detailed logs
   docker-compose logs [service-name]
   ```

3. **Database connection issues:**
   ```bash
   # Reset databases
   docker-compose down
   docker volume rm lightrag_agent_neo4j_data lightrag_agent_redis_data
   docker-compose up -d
   ```

4. **Memory issues:**
   ```bash
   # Increase Docker memory limit to at least 4GB
   # Check Docker Desktop settings
   ```

### Health Checks

All services include health checks. Check status:
```bash
docker-compose ps
```

Healthy services show "Up" status. Unhealthy services show "Up (unhealthy)".

## Production Deployment

For production:

1. **Use production docker-compose:**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

2. **Set strong passwords:**
   ```bash
   # Update these in .env:
   NEO4J_PASSWORD=your_strong_password
   REDIS_PASSWORD=your_strong_password
   ```

3. **Enable HTTPS:**
   - Add SSL certificates
   - Configure reverse proxy (nginx/traefik)
   - Update CORS_ORIGINS

4. **Monitor resources:**
   ```bash
   docker stats
   ```

## Data Persistence

Data is persisted in Docker volumes:
- `neo4j_data`: Graph database data
- `redis_data`: Cache and session data
- `chroma_data`: Vector embeddings
- Local directories: `uploads/`, `lightrag_data/`, `logs/`

## Cost Optimization

This setup uses **GPT-4o-mini** which provides:
- ✅ **90% cost reduction** vs GPT-4
- ✅ **Faster response times**
- ✅ **Same quality for most tasks**
- ✅ **~$0.0006 per 1K tokens** vs $0.030 for GPT-4

For a typical development session: **$0.10-0.50** instead of $2-10!

## Next Steps

1. Upload documents through the web interface
2. Chat with your knowledge base
3. Explore the Neo4j graph visualization
4. Monitor logs for optimization opportunities

## Support

- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart [service]`
- Reset everything: `docker-compose down -v && docker-compose up -d` 