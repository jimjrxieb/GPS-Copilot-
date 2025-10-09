# LinkOps-Host

JamesOS / LinkOps Production Platform
=====================================

## 🏗️ Architecture Overview

```
LinkOps-Host/
├── htc/                  # Training & testbed (model development)
├── links-pipeline/       # Production inference models
├── db/                   # MCP memory storage (job categories)
├── james-logic/          # AI brain & orchestrator
├── james-rag/            # RAG vector memory search
├── frontend/             # Vue.js GUI
├── infra/                # Infrastructure (Helm, ArgoCD, Docker)
├── scripts/              # CI/CD, linting, helpers
├── tools/cli/            # CLI utilities
├── shared/               # Common utilities & models
└── docs/                 # Documentation
```

## 🚀 Quick Start

```bash
# Start the complete platform
cd infra
docker-compose up --build

# Access the GUI
open http://localhost:3000
```

## 📚 Documentation

- [Configuration](docs/CONFIGURATION.md)
- [Deployment](docs/DEPLOYMENT_FIXED.md)
- [Services](docs/SERVICES.md)
- [Architecture Trees](docs/*Tree.txt)

## 🔧 Development

```bash
# Run linting
./scripts/linting/fix_*.py

# Validate structure
./scripts/helpers/validate_structure.py

# Security checks
./scripts/ci/security_*.py
```

## 🧠 JamesOS Components

- **James Logic**: Core reasoning and orchestration
- **James RAG**: Semantic memory and retrieval
- **Links Pipeline**: Production AI inference chain
- **HTC**: Model training and experimentation
- **DB**: Structured knowledge storage
