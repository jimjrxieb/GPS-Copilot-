# AuditGuard Service

A production-ready security and compliance microservice for the LinkOps platform, providing comprehensive security scanning, repository auditing, and compliance framework validation.

## 🚀 Features

### Security Scanning
- **Trivy**: Container and filesystem vulnerability scanning
- **Bandit**: Python security linting and static analysis
- **Checkov**: Infrastructure as Code (IaC) security scanning
- **Snyk**: Dependency vulnerability scanning
- **Semgrep**: Static code analysis and pattern matching

### Repository Auditing
- Secret detection and credential scanning
- Sensitive file identification
- Risk scoring and remediation recommendations
- Compliance metadata tagging

### Compliance Frameworks
- **SOC2**: Service Organization Control 2 compliance
- **GDPR**: General Data Protection Regulation
- **ISO27001**: Information Security Management
- **NIST**: National Institute of Standards and Technology
- **HIPAA**: Health Insurance Portability and Accountability Act
- **PCI-DSS**: Payment Card Industry Data Security Standard

## 🏗️ Architecture

```
auditguard/
├── routes/
│   ├── __init__.py          # Route aggregation
│   ├── audit.py            # Repository auditing
│   ├── compliance.py       # Compliance framework validation
│   └── security.py         # Security scanning tools
├── tests/
│   ├── __init__.py
│   └── test_routes.py      # Unit tests
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── README.md              # This file
```

## 🛠️ Quick Start

### Local Development

1. **Clone and navigate to the service:**
   ```bash
   cd shadows/auditguard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t auditguard:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 auditguard:latest
   ```

## 📡 API Endpoints

### Health Checks
- `GET /` - Service information
- `GET /audit/health` - Audit module health
- `GET /compliance/health` - Compliance module health
- `GET /security/health` - Security module health

### Security Scanning
- `POST /security/scan` - Execute security scans (Trivy, Bandit, Checkov, Snyk, Semgrep)

### Repository Auditing
- `POST /audit/repository` - Comprehensive repository security audit

### Compliance Validation
- `POST /compliance/audit` - Compliance framework validation

## 🔧 Configuration

### Environment Variables
- `LOG_LEVEL`: Logging level (default: INFO)
- `ENVIRONMENT`: Deployment environment (default: production)

### Security Tools
The service includes the following security scanning tools:
- **Trivy**: Installed via official repository
- **Checkov**: Installed via pip
- **Semgrep**: Installed via pip
- **Bandit**: Installed via pip

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

## 🚀 CI/CD Pipeline

The service includes a comprehensive GitHub Actions workflow that:
1. **Tests**: Runs linting, security checks, and unit tests
2. **Builds**: Creates Docker image with security scanning
3. **Deploys**: Updates Kubernetes manifests for GitOps deployment

## 🐳 Kubernetes Deployment

The service is designed for Kubernetes deployment with:
- **Deployment**: Multi-replica deployment with health checks
- **Service**: ClusterIP service for internal communication
- **Security**: Non-root user, read-only filesystem, resource limits

### Deploy to Kubernetes:
```bash
kubectl apply -f ../../LinkOps-Manifests/shadows/auditguard/
```

## 🔒 Security Features

- **Non-root container**: Runs as unprivileged user
- **Read-only filesystem**: Enhanced security posture
- **Resource limits**: Prevents resource exhaustion
- **Health checks**: Liveness and readiness probes
- **Security scanning**: Built-in vulnerability scanning

## 📊 Monitoring

The service provides comprehensive health endpoints for monitoring:
- Application health status
- Service capabilities
- Endpoint availability

## 🤝 Contributing

1. Follow the established code style (Black + Flake8)
2. Add tests for new features
3. Update documentation as needed
4. Ensure all security scans pass

## 📄 License

Part of the LinkOps platform - see main repository for license information. 