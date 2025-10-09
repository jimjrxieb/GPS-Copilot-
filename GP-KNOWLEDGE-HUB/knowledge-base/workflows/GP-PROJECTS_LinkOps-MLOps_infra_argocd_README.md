# 🚀 LinkOps ArgoCD Deployment

This directory contains the ArgoCD Application manifests for deploying the LinkOps MLOps platform across multiple environments.

## 📋 Overview

The LinkOps platform is deployed using ArgoCD with GitOps principles, providing:
- **Automated deployments** from Git repository
- **Multi-environment support** (dev, staging, production)
- **Self-healing** capabilities
- **Rollback** functionality
- **Health monitoring** and status tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│   ArgoCD        │───▶│   Kubernetes    │
│   (Source of    │    │   (GitOps       │    │   (Target       │
│    Truth)       │    │    Controller)  │    │    Cluster)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
argocd/
├── linkops-application.yaml    # Main ArgoCD Application manifests
├── README.md                   # This documentation
└── deploy-argocd.sh           # Deployment script
```

## 🎯 Environments

### Production (`linkops-platform`)
- **Namespace**: `linkops`
- **Replicas**: 2 per service
- **Autoscaling**: Enabled
- **Monitoring**: Full monitoring stack
- **Persistence**: Enabled for databases
- **Image Tag**: `latest`

### Staging (`linkops-platform-staging`)
- **Namespace**: `linkops-staging`
- **Replicas**: 1 per service
- **Autoscaling**: Enabled
- **Monitoring**: Basic monitoring
- **Persistence**: Enabled
- **Image Tag**: `staging`

### Development (`linkops-platform-dev`)
- **Namespace**: `linkops-dev`
- **Replicas**: 1 per service
- **Autoscaling**: Disabled
- **Monitoring**: Disabled
- **Persistence**: Disabled (ephemeral)
- **Image Tag**: `dev`

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster** with ArgoCD installed
2. **kubectl** configured to access the cluster
3. **Helm** (optional, for ArgoCD installation)

### Deployment Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jimjrxieb/shadow-link-industries.git
   cd LinkOps-Host
   ```

2. **Run the deployment script**:
   ```bash
   ./deploy-argocd.sh deploy
   ```

3. **Access ArgoCD UI**:
   - URL: `http://argocd.local`
   - Username: `admin`
   - Password: (displayed by deployment script)

### Manual Deployment

If you prefer manual deployment:

```bash
# 1. Create namespaces
kubectl create namespace linkops
kubectl create namespace linkops-dev
kubectl create namespace linkops-staging

# 2. Apply ArgoCD applications
kubectl apply -f argocd/linkops-application.yaml

# 3. Check application status
kubectl get applications -n argocd
```

## 🔧 Configuration

### Helm Values Override

The ArgoCD applications use Helm parameters to override values for different environments:

```yaml
helm:
  parameters:
    - name: global.imageTag
      value: "latest"
    - name: services.mlops_platform.replicas
      value: "2"
    - name: autoscaling.enabled
      value: "true"
```

### Environment-Specific Settings

| Setting | Production | Staging | Development |
|---------|------------|---------|-------------|
| Replicas | 2 | 1 | 1 |
| Autoscaling | ✅ | ✅ | ❌ |
| Monitoring | ✅ | ✅ | ❌ |
| Persistence | ✅ | ✅ | ❌ |
| Image Tag | `latest` | `staging` | `dev` |

## 📊 Monitoring

### ArgoCD Application Status

```bash
# Check all applications
kubectl get applications -n argocd

# Check specific application
kubectl get application linkops-platform -n argocd

# Get detailed status
kubectl describe application linkops-platform -n argocd
```

### Application Health

ArgoCD provides health status for each application:
- **Healthy**: All resources are synced and healthy
- **Progressing**: Application is being deployed
- **Degraded**: Some resources are unhealthy
- **Suspended**: Application sync is suspended

### Sync Status

```bash
# Check sync status
kubectl get applications -n argocd -o custom-columns=NAME:.metadata.name,STATUS:.status.sync.status,HEALTH:.status.health.status

# Force sync an application
kubectl patch application linkops-platform -n argocd --type='merge' -p='{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true}}}}'
```

## 🔄 Sync Policy

### Automated Sync

All environments use automated sync with:
- **Prune**: Remove resources not in Git
- **Self-heal**: Automatically fix drift
- **Retry**: Automatic retry on failure

### Sync Options

```yaml
syncOptions:
  - CreateNamespace=true          # Create namespace if missing
  - PrunePropagationPolicy=foreground  # Safe deletion
  - PruneLast=true               # Prune after sync
  - RespectIgnoreDifferences=true # Respect ignore differences
```

## 🛡️ Security

### RBAC

ArgoCD applications run with appropriate RBAC:
- **Service accounts** for each namespace
- **Role-based access** control
- **Network policies** for service isolation

### Secrets Management

- **Kubernetes secrets** for sensitive data
- **External secret operators** (optional)
- **Sealed secrets** for Git storage (optional)

## 🔍 Troubleshooting

### Common Issues

1. **Application stuck in Progressing**:
   ```bash
   kubectl describe application <app-name> -n argocd
   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
   ```

2. **Sync failed**:
   ```bash
   kubectl get events -n <namespace> --sort-by='.lastTimestamp'
   kubectl describe pod <pod-name> -n <namespace>
   ```

3. **Image pull errors**:
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   kubectl logs <pod-name> -n <namespace>
   ```

### Debug Commands

```bash
# Check ArgoCD server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server

# Check application controller logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller

# Check repo server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-repo-server

# Port forward to ArgoCD server
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## 📈 Scaling

### Horizontal Pod Autoscaling

Production and staging environments have HPA enabled:

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Manual Scaling

```bash
# Scale specific service
kubectl scale deployment mlops-platform -n linkops --replicas=3

# Scale all services in namespace
kubectl scale deployment --all -n linkops --replicas=3
```

## 🔄 Updates and Rollbacks

### Updating Applications

1. **Git-based updates**: Push changes to Git repository
2. **ArgoCD auto-sync**: Applications sync automatically
3. **Manual sync**: Use ArgoCD UI or CLI

### Rollbacks

```bash
# Rollback to previous revision
kubectl patch application linkops-platform -n argocd --type='merge' -p='{"spec":{"source":{"targetRevision":"HEAD~1"}}}'

# Rollback to specific revision
kubectl patch application linkops-platform -n argocd --type='merge' -p='{"spec":{"source":{"targetRevision":"abc123"}}}'
```

## 📚 Additional Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [LinkOps Platform Documentation](../README.md)
- [Helm Chart Documentation](../helm/linkops/README.md)

## 🤝 Contributing

To contribute to the ArgoCD configuration:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test the deployment**
5. **Submit a pull request**

## 📞 Support

For issues and questions:
- **GitHub Issues**: [LinkOps Repository](https://github.com/jimjrxieb/shadow-link-industries)
- **Documentation**: [LinkOps Docs](../docs/)
- **Team**: team@linkops.com

---

**"Deploy with confidence, scale with ease"** 🚀 