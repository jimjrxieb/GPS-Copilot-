# GP-JADE Docker Deployment

Dockerized GP-JADE AI Security Engine with OPA and Gatekeeper integration.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  GP-JADE Container                                  │
│  ├─ Qwen2.5-7B (downloads on first run)           │
│  ├─ ChromaDB (vector embeddings - persistent)      │
│  ├─ RAG Engine                                      │
│  ├─ Security Scanners (Trivy, Bandit, Gitleaks)    │
│  └─ FastAPI endpoint (port 8000)                   │
└─────────────────────────────────────────────────────┘
           │                    │
           │                    │
           ▼                    ▼
┌──────────────────┐   ┌──────────────────┐
│  OPA Container   │   │  Gatekeeper      │
│  port 8181       │   │  (K8s optional)  │
└──────────────────┘   └──────────────────┘
```

## What Gets Pushed to GitHub

✅ **Pushed to GitHub:**
- `GP-DATA/vector-db/` - Vector embeddings (small, ~MBs)
- All Python code
- OPA policies
- Gatekeeper constraints
- Docker configs

❌ **NOT pushed (downloads locally):**
- `GP-DATA/ai-models/` - Qwen2.5-7B model (~15GB)
- Hugging Face cache
- Docker volumes

## Prerequisites

1. **Docker & Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **NVIDIA GPU (recommended)**
   ```bash
   # Install NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

3. **Verify GPU access**
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
   ```

## Quick Start

### 1. Build and Start Services

```bash
# Start GP-JADE with OPA
docker-compose up -d

# View logs
docker-compose logs -f gp-jade
```

### 2. First Run (Model Download)

On first run, Qwen2.5-7B (~15GB) will download automatically:

```bash
# Monitor download progress
docker-compose logs -f gp-jade | grep "Downloading"
```

This takes 10-30 minutes depending on internet speed. Subsequent runs use cached model.

### 3. Verify Services

```bash
# Check all services are running
docker-compose ps

# Test GP-JADE
docker exec -it gp-jade python3 -c "
import sys; sys.path.append('/app/GP-AI')
from engines.rag_engine import rag_engine
print(rag_engine.get_stats())
"

# Test OPA
curl http://localhost:8181/health
```

## Usage

### CLI Usage (Inside Container)

```bash
# Enter container
docker exec -it gp-jade bash

# Run security scans
cd /app
python3 GP-AI/cli/gp-jade.py scan /app/GP-PROJECTS/INTERVIEW-DEMO --client=demo

# Query AI security expert
python3 GP-AI/cli/gp-jade.py query "What are CKS pod security requirements?"
```

### API Usage

```bash
# Health check
curl http://localhost:8000/health

# Scan project via API
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/app/GP-PROJECTS/INTERVIEW-DEMO",
    "client": "demo",
    "scan_type": "comprehensive"
  }'

# Query security expert
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Kubernetes security best practices?",
    "context": "CKS exam preparation"
  }'
```

### OPA Policy Testing

```bash
# Test OPA policy
curl -X POST http://localhost:8181/v1/data/gp/security/decision \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "code": "password = \"hardcoded123\"",
      "file": "test.tf"
    }
  }'
```

## Development Workflow

### Local Development with Hot Reload

```bash
# Start with volume mounts
docker-compose up -d

# Changes to GP-AI/ are immediately reflected
# Edit GP-AI/engines/rag_engine.py locally
# Restart service to apply
docker-compose restart gp-jade
```

### Add New Vector Embeddings

```bash
# Enter container
docker exec -it gp-jade python3

# Python shell
import sys
sys.path.append('/app/GP-AI')
from engines.rag_engine import rag_engine

# Add custom knowledge
rag_engine.ingest_client_project('/app/GP-PROJECTS/YOUR-PROJECT', 'client-name')

# Exit and commit
exit

# Commit vector database to git
git add GP-DATA/vector-db/
git commit -m "Add client project embeddings"
git push
```

## Kubernetes Deployment (with Gatekeeper)

For Kubernetes environments with Gatekeeper:

```bash
# Start all services including Gatekeeper
docker-compose --profile kubernetes up -d

# Apply Gatekeeper constraints
kubectl apply -f gatekeeper-policies/
```

## Configuration

### Environment Variables

Edit `docker-compose.yml`:

```yaml
environment:
  - CUDA_VISIBLE_DEVICES=0  # GPU device ID
  - OPA_URL=http://opa:8181
  - GATEKEEPER_ENABLED=true
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      memory: 32G
      cpus: '8'
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## Troubleshooting

### Model Download Issues

```bash
# Manual download
docker exec -it gp-jade python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = 'Qwen/Qwen2.5-7B-Instruct'
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
"
```

### GPU Not Detected

```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If fails, check NVIDIA Container Toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### OPA Connection Failed

```bash
# Check OPA logs
docker-compose logs opa

# Test OPA directly
docker exec -it gp-opa opa version
```

## Maintenance

### Update Models

```bash
# Clear model cache and re-download
docker-compose down
docker volume rm gp-copilot_huggingface-cache
docker-compose up -d
```

### Backup Vector Database

```bash
# Backup before major changes
tar -czf vector-db-backup-$(date +%Y%m%d).tar.gz GP-DATA/vector-db/
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (including model cache)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Production Deployment

### AWS ECS / EC2 with GPU

```bash
# Use g4dn.xlarge or larger
# Ensure NVIDIA drivers installed
# Deploy docker-compose with ECS CLI
```

### GCP with GPU

```bash
# Use n1-standard-4 with Tesla T4
# Install NVIDIA drivers via startup script
# Deploy via Cloud Run with GPU support
```

## Performance

**Initial Startup:**
- First run: 10-30 min (model download)
- Subsequent runs: 30-60 seconds
- GPU warm-up: 5-10 seconds

**Inference:**
- Security scan: 5-15 seconds per file
- RAG query: 1-3 seconds
- Full project analysis: 1-5 minutes

## Security Notes

⚠️ **Never commit:**
- `.env` files with secrets
- API keys or tokens
- Client confidential data

✅ **Safe to commit:**
- Vector embeddings (anonymized)
- OPA policies
- Gatekeeper constraints
- Public project analyses