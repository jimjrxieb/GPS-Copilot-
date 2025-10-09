# Igris - Platform Engineering Microservice

Igris is a specialized microservice for platform engineering and DevSecOps automation. It provides intelligent infrastructure management, security recommendations, and multi-cloud solutions.

## 🏗️ Architecture

Igris is modularized into focused components:

```
shadows/igris/
├── main.py              # FastAPI application & routing
├── analyzer.py          # Platform component analysis
├── infrastructure.py    # Infrastructure solution generation
├── security.py          # Security recommendations
├── opendevin.py         # OpenDevin integration
├── tests/               # Test suite
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Features

### Core Capabilities
- **Infrastructure as Code**: Terraform automation and configuration
- **DevSecOps Practices**: Security-first infrastructure deployment
- **Multi-Cloud Support**: AWS, Azure, GCP, and Kubernetes
- **Platform Engineering**: Automated infrastructure management
- **OpenDevin Integration**: AI-powered automation insights
- **Security Scanning**: Compliance and vulnerability assessment

### API Endpoints

#### `/health`
Health check endpoint returning service status and capabilities.

#### `/execute`
Main task execution endpoint for platform engineering tasks.

**Request:**
```json
{
  "task_id": "task-001",
  "task_text": "Deploy Kubernetes cluster with security policies",
  "platform": "kubernetes",
  "action_type": "deploy"
}
```

**Response:**
```json
{
  "agent": "igris",
  "task": "Deploy Kubernetes cluster with security policies",
  "response": "Igris analyzed the kubernetes platform task with Infrastructure as Code approach including security best practices.",
  "infrastructure_solution": {
    "approach": "platform-native",
    "platform": "kubernetes",
    "components": [
      "Infrastructure as Code with Terraform",
      "Kubernetes Cluster Management",
      "Security & Compliance Framework"
    ],
    "security_level": "high",
    "automation_level": "full"
  },
  "generated_configs": ["# Terraform config ...", "# Kubernetes config ..."],
  "security_recommendations": [
    "Enable pod security policies",
    "Implement network policies",
    "Use RBAC for access control"
  ],
  "confidence_score": 0.85
}
```

#### `/opendevin/automate`
OpenDevin integration for intelligent automation.

#### `/api/enhance`
Whis integration endpoint for agent enhancement with new Orbs and Runes.

#### `/capabilities`
Returns current service capabilities and specializations.

## 🛠️ Development

### Prerequisites
- Python 3.11+
- Docker
- Kubernetes (for deployment)

### Local Development

1. **Clone and setup:**
```bash
cd shadows/igris
pip install -r requirements.txt
```

2. **Run locally:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Run tests:**
```bash
pytest tests/ -v
```

4. **Lint code:**
```bash
black .
flake8 . --max-line-length=88 --extend-ignore=E203
```

### Docker Development

```bash
# Build image
docker build -t igris:dev .

# Run container
docker run -p 8000:8000 igris:dev
```

## 🚀 Deployment

### Kubernetes Deployment

1. **Apply manifests:**
```bash
kubectl apply -f LinkOps-Manifests/shadows/igris/
```

2. **Verify deployment:**
```bash
kubectl get pods -l app=igris
kubectl get svc igris-service
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `production` |

## 🔧 Configuration

### Platform Support

Igris supports multiple platforms with specialized handling:

- **Kubernetes**: Pod security, RBAC, network policies
- **AWS**: IAM, CloudTrail, VPC security groups
- **Azure**: RBAC, Security Center, NSGs
- **GCP**: IAM, VPC, security policies
- **Terraform**: State management, modules, validation

### Security Features

- Infrastructure security scanning
- Compliance policy enforcement
- Vulnerability assessment
- Access control management
- Audit logging

## 🤝 Integration

### Whis Integration
Igris can be enhanced by Whis with new capabilities:

```bash
curl -X POST http://igris:8000/api/enhance \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "igris",
    "orb_id": "terraform-orb",
    "rune_patch": "enhanced-terraform-capabilities",
    "training_notes": "Added advanced Terraform modules"
  }'
```

### OpenDevin Integration
Leverage AI for intelligent automation:

```bash
curl -X POST http://igris:8000/opendevin/automate \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Automate infrastructure deployment",
    "platform": "kubernetes"
  }'
```

## 📊 Monitoring

### Health Checks
- Endpoint: `/health`
- Kubernetes probes configured
- Docker healthcheck enabled

### Metrics
- Request/response times
- Error rates
- Platform-specific metrics
- Security scan results

## 🔒 Security

- Non-root container execution
- Read-only filesystem
- Security context enforcement
- TLS encryption
- RBAC integration

## 📝 License

Part of the Shadow Link Industries platform engineering suite.

## 🤝 Contributing

1. Follow the modular architecture
2. Add tests for new features
3. Update documentation
4. Ensure security best practices
5. Run linting and tests before PR 