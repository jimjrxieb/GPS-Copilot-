# Katie - Kubernetes AI Agent & Cluster Guardian

Katie is the intelligent Kubernetes AI agent and cluster guardian for the LinkOps MLOps platform. She provides comprehensive Kubernetes operations with intelligent analysis, K8GPT integration, and SRE best practices.

## 🚀 Features

### Core Capabilities
- **Resource Description**: Detailed analysis of pods, deployments, services, and namespaces
- **Intelligent Scaling**: Smart scaling operations with recommendations
- **Log Analysis**: Advanced log search, error pattern analysis, and summaries
- **Resource Patching**: Safe resource updates with validation
- **Manifest Application**: Apply and manage Kubernetes manifests
- **Rollback Operations**: Intelligent rollback with analysis
- **K8GPT Integration**: AI-powered error analysis and insights

### SRE & Security
- **CKA/CKS Certified**: Kubernetes best practices embedded
- **Security Hardened**: Non-root containers, read-only filesystems
- **RBAC Integration**: Proper Kubernetes permissions
- **Health Monitoring**: Comprehensive health checks and probes
- **Auto-scaling**: HPA support for dynamic scaling

## 🏗️ Architecture

```
Katie Service (Port 8008)
├── FastAPI Application
├── Kubernetes Operations
│   ├── kubeops.describe - Resource analysis
│   ├── kubeops.scale - Scaling operations
│   ├── kubeops.logs - Log management
│   └── kubeops.patch - Resource updates
├── K8GPT Integration
└── SRE Best Practices
```

## 📋 Prerequisites

- Kubernetes cluster (1.19+)
- kubectl configured
- Helm 3.x (for Helm deployment)
- Python 3.10+ (for local development)

## 🚀 Quick Start

### Using Helm (Recommended)

```bash
# Add the LinkOps Helm repository
helm repo add linkops https://shadow-link-industries.github.io/linkops-helm

# Install Katie
helm install katie linkops/katie \
  --namespace default \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=katie.your-domain.com
```

### Using Kustomize

```bash
# Deploy using kustomize
kubectl apply -k LinkOps-Manifests/shadows/katie/

# Or apply individual manifests
kubectl apply -f LinkOps-Manifests/shadows/katie/
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/shadow-link-industries/linkops-mlops.git
cd linkops-mlops/shadows/katie

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```

### Execute Operations
```bash
POST /execute
{
  "task_id": "task-001",
  "task_type": "describe",
  "resource_type": "pod",
  "resource_name": "my-pod",
  "namespace": "default"
}
```

### Resource Description
```bash
GET /describe/pod/{namespace}/{pod_name}
GET /describe/deployment/{namespace}/{deployment_name}
GET /describe/service/{namespace}/{service_name}
GET /describe/namespace/{namespace}
GET /describe/pods/{namespace}
```

### Scaling Operations
```bash
POST /scale/deployment/{namespace}/{deployment_name}?replicas=3
POST /scale/statefulset/{namespace}/{statefulset_name}?replicas=5
POST /scale/autoscale/{namespace}/{deployment_name}?min_replicas=2&max_replicas=10
```

### Log Analysis
```bash
GET /logs/pod/{namespace}/{pod_name}?tail_lines=100
GET /logs/deployment/{namespace}/{deployment_name}
POST /logs/search/{namespace}?search_pattern=error
GET /logs/errors/{namespace}?hours_back=24
GET /logs/summary/{namespace}
```

### Resource Patching
```bash
POST /patch/deployment/{namespace}/{deployment_name}
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "app",
          "image": "new-image:latest"
        }]
      }
    }
  }
}
```

### Manifest Operations
```bash
POST /apply/manifest
{
  "manifest_yaml": "apiVersion: v1\nkind: Pod\n...",
  "namespace": "default",
  "dry_run": false
}
```

### Rollback Operations
```bash
POST /rollback/deployment/{namespace}/{deployment_name}?revision=2
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `K8GPT_ENABLED` | `true` | Enable K8GPT integration |
| `K8GPT_API_URL` | `https://api.k8gpt.ai/v1/analyze` | K8GPT API endpoint |

### Kubernetes RBAC

Katie requires the following permissions:
- Pod operations (get, list, watch, create, update, patch, delete)
- Deployment operations (including scale and rollback)
- Service operations
- Namespace operations (read-only)
- ConfigMap and Secret operations
- HPA operations
- Event monitoring
- Node analysis

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_katie.py::TestHealthEndpoint
pytest tests/test_katie.py::TestExecuteEndpoint
pytest tests/test_katie.py::TestDescribeEndpoints

# Run with coverage
pytest --cov=. tests/
```

## 📊 Monitoring

### Health Checks
- **Liveness Probe**: `/health` endpoint
- **Readiness Probe**: `/health` endpoint
- **Startup Probe**: Not configured (FastAPI handles startup)

### Metrics
- Request latency
- Error rates
- Kubernetes operation success rates
- K8GPT integration metrics

### Logging
- Structured JSON logging
- Kubernetes operation audit trails
- Error analysis and insights

## 🔒 Security

### Container Security
- Non-root user (UID 1000)
- Read-only root filesystem
- Dropped capabilities
- No privilege escalation

### Network Security
- ClusterIP service type
- Ingress with TLS termination
- Network policies (if configured)

### RBAC Security
- Least privilege principle
- Service account with specific permissions
- Cluster role binding for operations

## 🚀 Production Deployment

### High Availability
- Multiple replicas (default: 2)
- Pod anti-affinity rules
- Horizontal Pod Autoscaler

### Resource Management
- CPU: 200m request, 500m limit
- Memory: 256Mi request, 512Mi limit
- Storage: No persistent storage required

### Backup & Recovery
- No persistent data to backup
- Configuration in GitOps manifests
- State stored in Kubernetes API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [LinkOps Docs](https://docs.linkops.local)
- **Issues**: [GitHub Issues](https://github.com/shadow-link-industries/linkops-mlops/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shadow-link-industries/linkops-mlops/discussions)

---

**Katie** - Your Kubernetes AI Agent & Cluster Guardian 🛡️ 