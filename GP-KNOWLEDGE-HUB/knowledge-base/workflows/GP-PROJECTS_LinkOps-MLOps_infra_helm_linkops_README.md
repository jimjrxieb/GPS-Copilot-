# LinkOps MLOps Platform - Helm Chart

This Helm chart deploys the complete LinkOps MLOps Platform with all microservices, infrastructure components, and monitoring stack.

## 🏗️ Architecture

The chart deploys the following components:

### Core Services

- **MLOps Platform** - Main platform service with API endpoints
- **Frontend** - Vue.js web interface
- **Audit Assess** - Security and compliance scanning
- **Whis Services** - Data processing pipeline (data input, sanitize, smithing, enhance, webscraper)

### Infrastructure

- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **Platform Agent** - Go CLI agent for task execution

### Monitoring

- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards

## 📦 Installation

### Prerequisites

- Kubernetes cluster (1.20+)
- Helm 3.0+
- ArgoCD (for GitOps deployment)
- Ingress controller (nginx, traefik, etc.)
- Storage class for persistent volumes

### Quick Start

```bash
# Add the repository
helm repo add linkops https://jimjrxieb.github.io/shadow-link-industries

# Install the chart
helm install linkops ./helm/linkops \
  --namespace linkops \
  --create-namespace \
  --values values.yaml
```

### GitOps Deployment with ArgoCD

```bash
# Apply the ArgoCD Application
kubectl apply -f helm/argocd/Application.yaml
```

## ⚙️ Configuration

### Global Settings

```yaml
global:
  imagePullPolicy: IfNotPresent
  imageTag: latest
  imageRegistry: ghcr.io
  imageRepository: jimjrxieb
```

### Service Configuration

Each service can be enabled/disabled and configured independently:

```yaml
services:
  mlops_platform:
    enabled: true
    replicas: 2
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 1Gi
    ingress:
      enabled: true
      host: mlops.linkops.com
```

### Infrastructure Configuration

```yaml
infrastructure:
  postgres:
    enabled: true
    persistence:
      enabled: true
      size: 10Gi
      storageClass: fast-ssd
  redis:
    enabled: true
    persistence:
      enabled: true
      size: 5Gi
```

### Monitoring Configuration

```yaml
monitoring:
  prometheus:
    enabled: true
    persistence:
      enabled: true
      size: 10Gi
  grafana:
    enabled: true
    ingress:
      enabled: true
      host: grafana.linkops.com
```

## 🔐 Secrets Management

The chart creates the following secrets:

- `whis-secrets` - API keys for Whis services
- `audit-secrets` - Security scanner API keys
- `postgres-secrets` - Database credentials
- `grafana-secrets` - Grafana admin password

### Updating Secrets

```bash
# Update API keys
kubectl patch secret whis-secrets -n linkops --type='json' -p='[{"op": "replace", "path": "/data/api-key", "value":"<base64-encoded-key>"}]'

# Update audit scanner tokens
kubectl patch secret audit-secrets -n linkops --type='json' -p='[{"op": "replace", "path": "/data/gitguardian-api-key", "value":"<base64-encoded-key>"}]'
```

## 🌐 Ingress Configuration

The chart supports multiple ingress configurations:

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
  tls:
    enabled: true
    secretName: linkops-tls
```

## 📊 Autoscaling

Horizontal Pod Autoscaler is configured for all services:

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

## 🔒 Security

### Network Policies

Network policies are enabled by default to restrict inter-service communication.

### RBAC

Service accounts and roles are created for proper access control.

### Pod Security

Security contexts are configured for non-root execution.

## 📈 Monitoring & Observability

### Metrics Endpoints

- Prometheus: `http://prometheus:9090`
- Grafana: `http://grafana:3000`

### Health Checks

All services include liveness and readiness probes.

### Logging

Structured logging is configured for all services.

## 🚀 Deployment Strategies

### Development Environment

```yaml
# values-dev.yaml
global:
  imageTag: dev
services:
  mlops_platform:
    replicas: 1
  frontend:
    replicas: 1
autoscaling:
  enabled: false
monitoring:
  prometheus:
    enabled: false
  grafana:
    enabled: false
```

### Production Environment

```yaml
# values-prod.yaml
global:
  imageTag: latest
services:
  mlops_platform:
    replicas: 3
  frontend:
    replicas: 3
autoscaling:
  enabled: true
monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
```

## 🔧 Troubleshooting

### Common Issues

1. **Pods not starting**

   ```bash
   kubectl describe pod <pod-name> -n linkops
   kubectl logs <pod-name> -n linkops
   ```

2. **Services not accessible**

   ```bash
   kubectl get svc -n linkops
   kubectl describe svc <service-name> -n linkops
   ```

3. **Ingress issues**

   ```bash
   kubectl describe ingress -n linkops
   kubectl get events -n linkops
   ```

4. **Database connection issues**
   ```bash
   kubectl logs deployment/postgres -n linkops
   kubectl exec -it deployment/postgres -n linkops -- psql -U mlops -d mlops
   ```

### Health Checks

```bash
# Check all pods
kubectl get pods -n linkops

# Check services
kubectl get svc -n linkops

# Check ingress
kubectl get ingress -n linkops

# Check persistent volumes
kubectl get pvc -n linkops
```

## 📚 API Documentation

Once deployed, API documentation is available at:

- MLOps Platform: `http://mlops-platform:8000/docs`
- Audit Assess: `http://audit-assess:8003/docs`

## 🔄 Upgrades

### Helm Upgrade

```bash
helm upgrade linkops ./helm/linkops \
  --namespace linkops \
  --values values.yaml
```

### GitOps Upgrade

Simply update the values in your Git repository and ArgoCD will automatically sync the changes.

## 🗑️ Uninstallation

```bash
# Remove the release
helm uninstall linkops -n linkops

# Remove the namespace (optional)
kubectl delete namespace linkops
```

## 📋 Requirements

| Dependency | Version |
| ---------- | ------- |
| Kubernetes | >= 1.20 |
| Helm       | >= 3.0  |
| ArgoCD     | >= 2.0  |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `helm template`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
