# LinkOps Services Reference

This document provides a quick reference for all services in the LinkOps platform.

## 🗄️ Infrastructure Services

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| **PostgreSQL** | 5432 | Main database | `pg_isready -U linkops` |
| **Redis** | 6379 | Caching & session store | `redis-cli ping` |
| **Zookeeper** | 2181 | Kafka coordination | `echo ruok \| nc localhost 2181` |
| **Kafka** | 9092 | Message broker | `kafka-topics --bootstrap-server localhost:9092 --list` |

## 🧠 Core Services

| Service | Port | Description | Dependencies |
|---------|------|-------------|--------------|
| **Frontend** | 3000 | JamesOS Vue.js frontend | james-platform |
| **James Platform** | 8000 | Main API platform | db, redis, kafka |
| **QA Generator** | 8020 | QA generation & scoring | db, redis |
| **HTC** | 8021 | Hyperbolic Time Chamber training | db, redis |
| **Auditor** | 8022 | Security audit service | db, redis |
| **Task Evaluator** | 8023 | ML model evaluation | db, redis |

## 🏗️ James Pipeline Services

| Service | Port | Description | Dependencies |
|---------|------|-------------|--------------|
| **James Data Input** | 8030 | Data ingestion service | db, kafka |
| **James Sanitize** | 8031 | Data sanitization | db, kafka |
| **James Smithing** | 8032 | Data processing | db, kafka |
| **James Enhance** | 8033 | AI enhancement service | db, kafka |
| **James Logic** | 8034 | Core logic processing | db, kafka |
| **James ML** | 8035 | Machine learning service | db, kafka |
| **MLOps Utils** | 8036 | Utility services | db, kafka |

## 🎯 Job Category Services

| Service | Port | Description | Dependencies |
|---------|------|-------------|--------------|
| **DevOps Engineer** | 8040 | DevOps MCPs & tools | db, redis |
| **Data Scientist** | 8041 | Data science MCPs & tools | db, redis |
| **Platform Engineer** | 8042 | Platform engineering MCPs | db, redis |
| **Kubernetes Specialist** | 8043 | K8s MCPs & tools | db, redis |
| **Cloud Migration** | 8044 | Cloud migration MCPs | db, redis |

## 🚀 Quick Start Commands

### Start All Services
```bash
docker-compose up -d
```

### Start Core Services Only
```bash
docker-compose up -d db redis zookeeper kafka james-platform frontend
```

### Start Specific Service Group
```bash
# James Pipeline
docker-compose up -d james-data-input james-sanitize james-smithing james-enhance james-logic james-ml

# Job Categories
docker-compose up -d devops-engineer data-scientist platform-engineer kubernetes-specialist cloud-migration

# AI Services
docker-compose up -d qa-generator htc auditor task-evaluator
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f james-platform

# Multiple services
docker-compose logs -f james-platform frontend qa-generator
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific services
docker-compose stop james-platform frontend
```

## 🔧 Environment Variables

Create a `.env` file in the LinkOps-Host directory:

```env
# Database
POSTGRES_PASSWORD=your_secure_password

# AI Services
OPENAI_API_KEY=your_openai_key

# Security
GITGUARDIAN_API_KEY=your_gitguardian_key
SNYK_TOKEN=your_snyk_token

# Cloud (for Platform Engineer)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-east-1
```

## 📊 Service Health Monitoring

### Check All Services
```bash
docker-compose ps
```

### Health Check Endpoints
- **James Platform**: `http://localhost:8000/health`
- **QA Generator**: `http://localhost:8020/health`
- **HTC**: `http://localhost:8021/health`
- **Auditor**: `http://localhost:8022/health`

### Database Connection
```bash
# Connect to PostgreSQL
docker exec -it linkops-postgres psql -U linkops -d linkops

# Connect to Redis
docker exec -it linkops-redis redis-cli
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using a port
   sudo lsof -i :8000
   
   # Kill process using port
   sudo kill -9 <PID>
   ```

2. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose logs <service-name>
   
   # Rebuild service
   docker-compose build <service-name>
   docker-compose up -d <service-name>
   ```

3. **Database Connection Issues**
   ```bash
   # Check if database is running
   docker-compose ps db
   
   # Restart database
   docker-compose restart db
   ```

### Resource Usage
```bash
# Check resource usage
docker stats

# Check disk usage
docker system df
```

## 🔄 Development Workflow

### Hot Reload Development
All services are configured with volume mounts for hot reloading:
- Code changes are automatically reflected
- No need to rebuild containers for most changes
- Frontend has polling enabled for file watching

### Adding New Services
1. Create service directory with Dockerfile
2. Add service to docker-compose.yml
3. Update this SERVICES.md file
4. Test with `docker-compose up -d <new-service>`

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale specific service
docker-compose up -d --scale james-logic=3

# Scale multiple services
docker-compose up -d --scale james-data-input=2 --scale james-sanitize=2
```

### Resource Limits
Add to docker-compose.yml for production:
```yaml
services:
  james-platform:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

**Last Updated**: $(date)
**Total Services**: 22
**Total Ports Used**: 15 