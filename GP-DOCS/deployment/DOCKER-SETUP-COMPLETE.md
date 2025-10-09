# GP-JADE Docker Setup Complete ✅

## What's Been Created

### Core Docker Files
- ✅ `docker-compose.yml` - Multi-service orchestration (GP-JADE + OPA + Gatekeeper)
- ✅ `Dockerfile` - GP-JADE container with CUDA support
- ✅ `docker-entrypoint.sh` - Smart initialization script
- ✅ `docker-start.sh` - Interactive deployment script
- ✅ `requirements-docker.txt` - All Python dependencies
- ✅ `.dockerignore` - Optimized build context
- ✅ `.gitignore` - Proper exclusions

### API & Services
- ✅ `GP-AI/api/main.py` - FastAPI server with endpoints
- ✅ OPA policies in `opa-policies/`
- ✅ Gatekeeper constraints in `gatekeeper-policies/`

### Documentation
- ✅ `README-DOCKER.md` - Comprehensive Docker guide

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  gp-jade container                          │
│  ├─ Qwen2.5-7B (auto-downloads)            │
│  ├─ ChromaDB vector-db (persistent)        │
│  ├─ FastAPI (port 8000)                    │
│  ├─ RAG Engine                              │
│  └─ Security scanners (Trivy/Bandit)       │
└─────────────────────────────────────────────┘
           │                │
           ▼                ▼
    ┌──────────┐    ┌──────────────┐
    │   OPA    │    │  Gatekeeper  │
    │  :8181   │    │  (optional)  │
    └──────────┘    └──────────────┘
```

---

## What Gets Pushed to GitHub ✅

### Committed to Git:
```
✅ docker-compose.yml
✅ Dockerfile
✅ docker-entrypoint.sh
✅ docker-start.sh
✅ requirements-docker.txt
✅ .dockerignore
✅ .gitignore
✅ GP-AI/ (all code)
✅ opa-policies/
✅ gatekeeper-policies/
✅ GP-DATA/vector-db/      ← Vector embeddings (small, ~MBs)
✅ README-DOCKER.md
```

### NOT Committed (downloads locally):
```
❌ GP-DATA/ai-models/       ← Qwen2.5-7B (~15GB)
❌ .cache/huggingface/      ← Model cache
❌ Docker volumes
❌ __pycache__/
❌ *.pyc
```

---

## Quick Start

### 1. Interactive Deployment (Recommended)
```bash
./docker-start.sh
```

This script will:
- Check prerequisites (Docker, GPU)
- Create directories
- Let you choose deployment type
- Build and start services
- Show access points

### 2. Manual Deployment
```bash
# Build
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f gp-jade
```

### 3. Test the API
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

---

## Deployment on Another Computer

### Steps for New Machine:

1. **Clone repository:**
```bash
git clone <your-repo>
cd GP-copilot
```

2. **Install Docker + NVIDIA toolkit:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install NVIDIA Container Toolkit (if GPU available)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

3. **Start services:**
```bash
./docker-start.sh
```

4. **On first run:**
   - Qwen2.5-7B will auto-download (~15GB, 10-30 min)
   - Vector database loads from git (already embedded)
   - Subsequent runs use cached model (30-60 sec startup)

---

## Data Portability

### Vector Database (✅ Portable via Git)
```bash
# Vector embeddings are stored here and committed to git
GP-DATA/vector-db/
├── chroma.sqlite3           # Database file
├── <uuid>/                  # Collection data
│   ├── data_level0.bin
│   ├── header.bin
│   └── length.bin
```

**Size:** ~1-50MB (depends on knowledge ingested)
**Git-friendly:** Yes, binary but small enough

### AI Model (❌ Not in Git)
```bash
# Model downloads to container volume
/root/.cache/huggingface/hub/
└── models--Qwen--Qwen2.5-7B-Instruct/
    └── snapshots/<hash>/
        ├── model-00001-of-00004.safetensors
        ├── model-00002-of-00004.safetensors
        └── ...
```

**Size:** ~15GB
**Git-friendly:** No, auto-downloads via Hugging Face

---

## Adding New Knowledge to Vector DB

### Option 1: Via API
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/app/GP-PROJECTS/my-project",
    "client": "client-name"
  }'
```

### Option 2: Via Python
```bash
docker exec -it gp-jade python3

>>> import sys
>>> sys.path.append('/app/GP-AI')
>>> from engines.rag_engine import rag_engine
>>> rag_engine.ingest_client_project('/app/GP-PROJECTS/INTERVIEW-DEMO', 'demo-client')
>>> exit()
```

### Option 3: Via CLI
```bash
docker exec -it gp-jade bash
cd /app
python3 -c "
import sys
sys.path.append('/app/GP-AI')
from engines.rag_engine import rag_engine
rag_engine.ingest_client_project('/app/GP-PROJECTS/INTERVIEW-DEMO', 'demo')
"
```

### Commit Changes
```bash
# Exit container
exit

# Commit updated vector database
git add GP-DATA/vector-db/
git commit -m "Add demo client knowledge embeddings"
git push
```

---

## OPA & Gatekeeper Integration

### Test OPA Policy
```bash
curl -X POST http://localhost:8181/v1/data/gp/security/decision \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "code": "password = \"hardcoded123\"",
      "file": "main.tf"
    }
  }'
```

Response:
```json
{
  "result": {
    "allow": false,
    "violations": ["Potential hardcoded password detected"],
    "compliance": {
      "cis": false,
      "soc2": false
    }
  }
}
```

### Add Custom OPA Policy
```bash
# Edit or create new policy
vim opa-policies/custom-policy.rego

# Restart OPA
docker-compose restart opa
```

### Kubernetes Gatekeeper (Optional)
```bash
# Start with Gatekeeper
docker-compose --profile kubernetes up -d

# Apply constraints to K8s cluster
kubectl apply -f gatekeeper-policies/
```

---

## Performance Expectations

### First Run (Model Download):
- Download time: 10-30 minutes (15GB)
- Extraction: 2-5 minutes
- Initialization: 30-60 seconds
- **Total: 15-35 minutes**

### Subsequent Runs:
- Container start: 10-20 seconds
- Model load: 20-40 seconds
- Ready: 30-60 seconds
- **Total: <1 minute**

### Inference Performance:
- **With GPU:** 5-15 sec per file scan
- **Without GPU:** 30-90 sec per file scan
- **RAG query:** 1-3 seconds
- **Full project scan:** 1-5 minutes

---

## Troubleshooting

### Model Download Stuck
```bash
# Check logs
docker-compose logs -f gp-jade | grep "Downloading"

# Manual download
docker exec -it gp-jade python3 -c "
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct', trust_remote_code=True)
print('✅ Model downloaded')
"
```

### GPU Not Detected
```bash
# Verify GPU
nvidia-smi

# Test Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If fails, reinstall NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### OPA Connection Failed
```bash
# Check OPA logs
docker-compose logs opa

# Test OPA directly
curl http://localhost:8181/health

# Restart OPA
docker-compose restart opa
```

### Vector DB Not Loading
```bash
# Check directory
ls -la GP-DATA/vector-db/

# Reinitialize
docker exec -it gp-jade python3 -c "
import sys
sys.path.append('/app/GP-AI')
from engines.rag_engine import rag_engine
rag_engine.load_cks_knowledge()
rag_engine.load_compliance_frameworks()
print(rag_engine.get_stats())
"
```

---

## API Endpoints

### Health & Status
```bash
GET  /health                    # Service health
GET  /api/v1/knowledge/stats    # Vector DB stats
```

### Security Analysis
```bash
POST /api/v1/scan               # Scan project
POST /api/v1/query              # Query AI expert
```

### Knowledge Management
```bash
POST /api/v1/ingest             # Ingest project docs
POST /api/v1/knowledge/load/{type}  # Load built-in knowledge
```

### Policy Validation
```bash
GET  /api/v1/opa/validate       # Check OPA status
```

**Full API docs:** http://localhost:8000/docs

---

## Production Deployment

### AWS (ECS with GPU)
```bash
# Use g4dn.xlarge or larger
# Install nvidia-docker on host
# Deploy docker-compose to ECS
```

### GCP (Cloud Run with GPU)
```bash
# Use n1-standard-4 + Tesla T4
# Enable GPU support in Cloud Run
# Deploy container image
```

### Azure (ACI with GPU)
```bash
# Use NC-series VMs
# Install nvidia-docker
# Deploy via ACI
```

---

## Security Considerations

### Secrets Management
- ❌ Never commit `.env` files
- ✅ Use Docker secrets or AWS Secrets Manager
- ✅ Rotate API keys regularly

### Network Security
- ✅ Use reverse proxy (nginx) in production
- ✅ Enable HTTPS/TLS
- ✅ Restrict OPA access to internal network

### Container Security
- ✅ Run as non-root user (add to Dockerfile for production)
- ✅ Scan images with Trivy
- ✅ Keep base images updated

---

## Next Steps

1. **Start the system:**
   ```bash
   ./docker-start.sh
   ```

2. **Test basic functionality:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Run a security scan:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/scan \
     -H "Content-Type: application/json" \
     -d '{"project_path": "/app/GP-PROJECTS/INTERVIEW-DEMO", "client": "demo"}'
   ```

4. **Add your project knowledge:**
   ```bash
   # Mount your project as volume in docker-compose.yml
   volumes:
     - /path/to/your/project:/app/projects/your-project

   # Ingest it
   curl -X POST http://localhost:8000/api/v1/ingest \
     -d '{"project_path": "/app/projects/your-project", "client": "your-client"}'
   ```

5. **Commit vector DB:**
   ```bash
   git add GP-DATA/vector-db/
   git commit -m "Add project embeddings"
   git push
   ```

---

## Support

- 📖 Full Docker guide: [README-DOCKER.md](README-DOCKER.md)
- 🐛 Issues: Create GitHub issue
- 📧 Questions: Contact maintainer

---

**Status:** ✅ Ready for deployment
**Last Updated:** 2025-09-29