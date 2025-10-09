# LinkOps-Host Architecture Summary

## 🏗️ JamesOS / LinkOps Production Platform

This document outlines the complete architecture of the LinkOps-Host platform after the comprehensive restructure.

## 📁 Directory Structure

```
LinkOps-Host/
├── htc/                  # Training & testbed (model development)
│   └── models/           # Training variants (smithing, forging, etc.)
├── links-pipeline/       # Production inference models
│   ├── data-intake/      # Entry point for AI pipeline
│   ├── links-preprocess/ # Data cleaning & categorization
│   ├── links-smithing/   # Tool generation
│   ├── links-forging/    # Resource generation
│   ├── links-evaluator/  # Quality evaluation
│   ├── links-ranker/     # Autonomy assessment
│   ├── links-save-to-db/ # Memory storage
│   └── pipeline_orchestrator.py # Main pipeline controller
├── db/                   # MCP memory storage (job categories)
│   └── job-categories/   # Structured knowledge by role
├── james-logic/          # AI brain & orchestrator
├── james-rag/            # RAG vector memory search
├── frontend/             # Vue.js GUI
├── infra/                # Infrastructure (Helm, ArgoCD, Docker)
│   ├── helm/             # Kubernetes Helm charts
│   ├── argocd/           # GitOps manifests
│   ├── docker-compose.yml # Local development
│   └── helmfile.yaml     # Helm orchestration
├── scripts/              # CI/CD, linting, helpers
│   ├── ci/               # Security & CI scripts
│   ├── linting/          # Code quality scripts
│   └── helpers/          # Validation & utilities
├── tools/cli/            # CLI utilities
├── shared/               # Common utilities & models
└── docs/                 # Documentation
    ├── CONFIGURATION.md
    ├── DEPLOYMENT_FIXED.md
    ├── SERVICES.md
    └── *Tree.txt         # Architecture trees
```

## 🔄 Data Flow Architecture

### 1. Training Flow (HTC)
```
htc/models/ → Experimentation → Model Validation → Production Ready
```

### 2. Production Inference Flow (Links Pipeline)
```
Input → data-intake → preprocess → (smithing + forging) → evaluator + ranker → save-to-db
```

### 3. Memory & Retrieval Flow (James Brain)
```
Query → james-rag → Vector Search → james-logic → Decision/Action
```

### 4. Knowledge Storage Flow (DB)
```
save-to-db → Structured Storage → job-categories/ → MCP Memory
```

## 🧠 JamesOS Components

### Core AI Services
- **James Logic**: Core reasoning, task matching, agent orchestration
- **James RAG**: Semantic memory, vector search, knowledge retrieval
- **Links Pipeline**: Production AI inference chain with quality gates

### Training & Development
- **HTC**: Model training, experimentation, validation
- **Scripts**: CI/CD, linting, security, automation

### Infrastructure
- **Infra**: Kubernetes, Helm, ArgoCD, Docker orchestration
- **Frontend**: Vue.js GUI for platform management

### Knowledge Management
- **DB**: Structured MCP memory storage by job categories
- **Shared**: Common utilities, models, and configurations

## 🚀 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| data-intake | 8000 | Pipeline entry point |
| links-preprocess | 8082 | Data cleaning |
| links-smithing | 8080 | Tool generation |
| links-forging | 8081 | Resource generation |
| links-evaluator | 8085 | Quality evaluation |
| links-ranker | 8084 | Autonomy assessment |
| links-save-to-db | 8000 | Memory storage |
| james-logic | 8004 | AI reasoning |
| james-rag | 8008 | Vector search |
| frontend | 3000 | Web GUI |

## 🔧 Development Workflow

### Local Development
```bash
# Start complete platform
cd infra
docker-compose up --build

# Run linting
./scripts/linting/fix_*.py

# Validate structure
./scripts/helpers/validate_structure.py

# Security checks
./scripts/ci/security_*.py
```

### Production Deployment
```bash
# Deploy to Kubernetes
cd infra
helmfile apply

# Monitor with ArgoCD
kubectl get applications -n argocd
```

## 📚 Key Principles

1. **Separation of Concerns**: Training (HTC) vs Inference (Pipeline) vs Memory (DB/RAG)
2. **Modular Architecture**: Each service has a single responsibility
3. **Quality Gates**: Evaluation and ranking ensure production readiness
4. **Knowledge Persistence**: Structured storage enables continuous learning
5. **Scalable Infrastructure**: Kubernetes + GitOps for production deployment

## 🎯 Next Steps

1. **Model Integration**: Drop trained models into pipeline services
2. **RAG Enhancement**: Build comprehensive vector search capabilities
3. **CLI Tools**: Create command-line interfaces for common tasks
4. **Monitoring**: Add observability and alerting
5. **Documentation**: Expand user guides and API documentation

---

*This architecture represents a production-ready AI platform for autonomous task execution and continuous learning.* 