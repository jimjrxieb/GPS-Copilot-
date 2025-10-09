# LinkOps MLOps Platform

This directory contains the **Whis** AI training and data processing pipeline, plus comprehensive **audit and migration** services for the LinkOps MLOps platform.

## 🎯 Purpose

This platform allows engineers to capture, refine, and automate everything they want to learn and execute across DevOps, MLOps, GitOps, and platform engineering domains.

## 🔍 Audit & Migration Services

### Audit Assess (`audit_assess`)
- **Input**: Public GitHub repository URL
- **Output**:
  - Security vulnerabilities (Trivy, Snyk, Semgrep)
  - Secrets detection (GitGuardian patterns)
  - Microservice structure report
  - GitOps compliance score (0-100)
  - Comprehensive security analysis

### Audit Migrate (`audit_migrate`)
- **Input**: Audit report from `audit_assess`
- **Output**:
  - Helm chart scaffolding
  - Dockerfile patch suggestions
  - GitOps directory layout
  - ArgoCD-ready templates

## 🧠 LinkOps Pipeline Overview

The LinkOps pipeline is the production inference system that processes tasks through a complete autonomous learning and execution flow.

### Pipeline Flow

```
Input → Preprocess → Generate (parallel) → Evaluate → Autonomy → Store/Enhance
  ↓         ↓              ↓                ↓          ↓           ↓
Data    Clean &      Tools + Resources   Quality   Can Execute   Memory or
Intake  Categorize   (Smithing/Forging)   Check     Autonomously  Human Review
```

## 📁 Directory Structure

```
links-pipeline/
├── links-data-intake/     # Receives and processes input data
├── links-preprocess/      # Cleans and categorizes input
├── links-smithing/        # Generates tools (production inference)
├── links-forging/         # Generates resources (production inference)
├── links-evaluator/       # Evaluates generated tools
├── links-ranker/          # Determines autonomy level
├── links-enhance/         # Human review and improvement
├── james-logic/           # Memory storage and RAG
├── james-agent-packager/  # Creates downloadable agents
├── mlops-utils/           # Shared utilities
└── pipeline_orchestrator.py # Main pipeline controller
```

### Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| links-data-intake | 8001 | Data ingestion |
| links-preprocess | 8082 | Data cleaning |
| links-smithing | 8080 | Tool generation |
| links-forging | 8081 | Resource generation |
| links-evaluator | 8085 | Quality evaluation |
| links-ranker | 8084 | Autonomy assessment |
| links-enhance | 8083 | Human review |
| james-logic | 8004 | Memory and RAG |
| james-agent-packager | 8007 | Agent packaging |
| mlops-utils | 8000 | Utilities |

## 🔄 Pipeline Stages

### 1. Data Intake (`links-data-intake`)
- **Purpose**: Receives and processes various types of input data
- **Input**: Text, images, documents, web content, etc.
- **Output**: Structured data ready for processing
- **Port**: 8001

### 2. Preprocess (`links-preprocess`)
- **Purpose**: Cleans, categorizes, and standardizes input data
- **Input**: Raw input data
- **Output**: Cleaned and categorized data
- **Port**: 8082

### 3. Generate (`links-smithing` + `links-forging`)
- **Purpose**: Generates tools and resources in parallel
- **Input**: Cleaned and categorized data
- **Output**: 
  - **Tools**: Generated code and scripts
  - **Resources**: Configuration and deployment files
- **Ports**: 8080 (smithing), 8081 (forging)

### 4. Evaluate (`links-evaluator`)
- **Purpose**: Evaluates quality and safety of generated tools
- **Input**: Generated tool code and metadata
- **Output**: Quality score and pass/fail decision
- **Port**: 8085

### 5. Autonomy (`links-ranker`)
- **Purpose**: Determines if task can be executed autonomously
- **Input**: Task description and category
- **Output**: Autonomy score and execution decision
- **Port**: 8084

### 6. Store/Enhance (`james-logic` + `links-enhance`)
- **Purpose**: Stores approved items or sends for human review
- **Input**: Evaluated tools and resources
- **Output**: Stored in memory or enhanced through human review
- **Ports**: 8004 (logic), 8083 (enhance)

### 7. Memory Search (`james-rag`)
- **Purpose**: Semantic vector search for tools/resources
- **Input**: Query string
- **Output**: Best-matching tools/resources
- **Port**: 8008

### Example Query

```bash
curl -X POST http://localhost:8008/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to restrict egress traffic in Kubernetes?"}'
```

## 🚀 Usage

### Start the Complete Pipeline

```bash
# Start all services
docker-compose up --build

# Or start individual services
docker-compose up links-preprocess links-smithing links-forging
```

### Run the Pipeline Orchestrator

```bash
# Test the complete pipeline
python pipeline_orchestrator.py

# Or use the orchestrator programmatically
from pipeline_orchestrator import run_pipeline

result = await run_pipeline("Deploy a Python web application to Kubernetes")
print(result)
```

### Test Individual Services

```bash
# Test preprocessing
curl -X POST http://localhost:8082/sanitize \
  --json '{"task_text": "Deploy a web app"}'

# Test tool generation
curl -X POST http://localhost:8080/generate-tool \
  --json '{"task_text": "Deploy a web app"}'

# Test resource generation
curl -X POST http://localhost:8081/generate-resource \
  --json '{"task_text": "Deploy a web app"}'

# Test evaluation
curl -X POST http://localhost:8085/evaluate-tool \
  --json '{"tool_code": "# Tool code here", "tags": ["deployment"]}'

# Test autonomy ranking
curl -X POST http://localhost:8084/autonomy-score \
  --json '{"task_text": "Deploy a web app", "category": "deployment"}'
```

### Check Service Health

```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:8082/health
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8085/health
curl http://localhost:8084/health
curl http://localhost:8083/health
curl http://localhost:8004/health
```

## 🧪 Testing

Each service has its own test suite:
```bash
# Test individual services
cd mlops/whis_data_input && python -m pytest tests/
cd mlops/whis_sanitize && python -m pytest tests/
# ... etc

# Test full pipeline
python scripts/test_complete_pipeline.py
```

## 📊 Monitoring

- Health checks: `GET /health` on each service
- Metrics: Prometheus endpoints available
- Logs: Structured logging with correlation IDs

## 🔧 Development

### Adding a New Service
1. Create directory in `mlops/`
2. Add `main.py`, `Dockerfile`, `README.md`
3. Update docker-compose files
4. Add Helm chart in `helm/`
5. Add tests in `tests/`

### Modifying the Pipeline
1. Update service logic
2. Test with sample data
3. Validate with integration tests
4. Deploy with Helm

## 🎯 Integration with Agents

The Whis pipeline feeds into the shadow agents in `../shadows/`:
- **Igris**: Platform engineering logic
- **Katie**: Kubernetes and cluster management
- **Auditguard**: Security and compliance
- **Ficknury**: Task evaluation and routing

## 📈 Continuous Learning

Whis learns from:
- Human engineer feedback
- Successful deployments
- Failed attempts
- External data sources
- Agent performance metrics

This creates a continuously improving MLOps platform that gets smarter with every interaction. 