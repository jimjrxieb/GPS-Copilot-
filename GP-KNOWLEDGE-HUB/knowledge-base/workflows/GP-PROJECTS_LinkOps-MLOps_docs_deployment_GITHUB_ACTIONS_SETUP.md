# GitHub Actions Setup for AKS Deployment

This document provides a complete guide for setting up GitHub Actions to deploy your LinkOps-MLOps services to Azure Kubernetes Service (AKS).

## Overview

The GitHub Actions pipeline provides:
- **Security Scanning**: SAST, container scanning, and secrets detection
- **Multi-Service Build**: Builds Docker images for all services
- **Multi-Environment Deployment**: Deploy to demo and personal AKS clusters
- **Helm-based Deployment**: Uses Helm charts for Kubernetes deployments

## Prerequisites

### 1. Azure Setup
- Azure subscription with AKS clusters deployed
- Service Principal with appropriate permissions
- OIDC (OpenID Connect) configured for GitHub Actions

### 2. GitHub Repository Setup
- Repository secrets configured
- GitHub Container Registry access

## Required GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AZURE_CLIENT_ID` | Service Principal Client ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_TENANT_ID` | Azure Tenant ID | `87654321-4321-4321-4321-210987654321` |
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID | `11111111-2222-3333-4444-555555555555` |
| `GITGUARDIAN_API_KEY` | GitGuardian API key for secrets scanning | `ggp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `SONAR_TOKEN` | SonarCloud token for code analysis | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `SONAR_ORG` | SonarCloud organization | `your-org` |
| `SONAR_PROJECT_KEY` | SonarCloud project key | `your-org_LinkOps-MLOps` |

## Azure Service Principal Setup

### 1. Create Service Principal
```bash
# Create service principal
az ad sp create-for-rbac --name "LinkOps-MLOps-GitHubActions" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

### 2. Configure OIDC (Recommended)
```bash
# Create OIDC provider
az ad app federated-credential create \
  --id YOUR_APP_ID \
  --parameters "{\"name\":\"github-actions\",\"issuer\":\"https://token.actions.githubusercontent.com\",\"subject\":\"repo:your-org/LinkOps-MLOps:ref:refs/heads/main\",\"audience\":\"api://AzureADTokenExchange\"}"
```

### 3. Assign Permissions
```bash
# Assign AKS permissions
az role assignment create \
  --assignee YOUR_CLIENT_ID \
  --role "Azure Kubernetes Service Cluster User Role" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/linkops-demo-rg/providers/Microsoft.ContainerService/managedClusters/linkops-demo-aks

az role assignment create \
  --assignee YOUR_CLIENT_ID \
  --role "Azure Kubernetes Service Cluster User Role" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/linkops-personal-rg/providers/Microsoft.ContainerService/managedClusters/linkops-personal-aks
```

## Workflow Configuration

### 1. Automatic Deployment
The workflow automatically triggers on:
- Push to `main` branch
- Changes to `shadows/`, `helm/`, or workflow files
- Manual workflow dispatch

### 2. Manual Deployment
You can manually trigger deployments with specific parameters:
- **Environment**: `demo` or `personal`
- **Service**: Specific service name (optional, deploys all if empty)

### 3. Environment Protection
- `demo` environment: Deploys automatically on main branch
- `personal` environment: Requires manual approval

## Helm Chart Structure

Each service has its own Helm chart in the `helm/` directory:

```
helm/
├── whis/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── serviceaccount.yaml
│       └── _helpers.tpl
├── james/
├── katie/
└── ...
```

### Generate Helm Charts
```bash
# Generate charts for all services
./scripts/generate-helm-charts.sh
```

## Deployment Process

### 1. Security Scanning
- **SAST**: Bandit for Python code analysis
- **Container Scanning**: Trivy for vulnerability scanning
- **Secrets Detection**: TruffleHog and GitGuardian
- **Code Quality**: SonarCloud analysis

### 2. Build Process
- Multi-service matrix build
- Docker image building with Buildx
- Container registry push (GitHub Container Registry)
- Image vulnerability scanning

### 3. Deployment Process
- Azure authentication via OIDC
- AKS cluster connection
- Helm chart deployment
- Health verification

## Environment-Specific Configuration

### Demo Environment
- **Resource Group**: `linkops-demo-rg`
- **Cluster**: `linkops-demo-aks`
- **Purpose**: Testing and demonstrations
- **Auto-deploy**: Yes (on main branch)

### Personal Environment
- **Resource Group**: `linkops-personal-rg`
- **Cluster**: `linkops-personal-aks`
- **Purpose**: Development and experimentation
- **Auto-deploy**: No (manual only)

## Monitoring and Verification

### 1. Deployment Verification
```bash
# Check deployment status
kubectl get pods -n default
kubectl get services -n default
kubectl get deployments -n default
```

### 2. Service Access
- **Demo**: `https://linkops-demo-aks.eastus.cloudapp.azure.com`
- **Personal**: `https://linkops-personal-aks.eastus.cloudapp.azure.com`

### 3. Logs and Debugging
```bash
# View service logs
kubectl logs -f deployment/whis-demo -n default

# Check Helm releases
helm list -n default
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures
```bash
# Verify Azure credentials
az account show
az aks get-credentials --resource-group linkops-demo-rg --name linkops-demo-aks
```

#### 2. Image Pull Errors
- Check container registry permissions
- Verify image tags and repositories
- Ensure secrets are properly configured

#### 3. Helm Deployment Failures
```bash
# Check Helm chart syntax
helm lint ./helm/whis

# Dry run deployment
helm install --dry-run --debug test-release ./helm/whis
```

#### 4. Resource Quotas
```bash
# Check cluster resources
kubectl describe nodes
kubectl get resourcequota -A
```

### Debug Commands
```bash
# Get workflow logs
gh run list --workflow=deploy-aks.yml

# View specific run
gh run view RUN_ID --log

# Rerun failed workflow
gh run rerun RUN_ID
```

## Security Best Practices

### 1. Secrets Management
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly
- Use OIDC instead of service principal secrets

### 2. Network Security
- Configure network policies in AKS
- Use private endpoints where possible
- Implement proper ingress/egress rules

### 3. Container Security
- Scan images for vulnerabilities
- Use minimal base images
- Implement security contexts

### 4. Access Control
- Use RBAC in Kubernetes
- Implement least privilege principle
- Regular access reviews

## Cost Optimization

### 1. Demo Environment
- Use smaller VM sizes
- Implement auto-scaling
- Schedule shutdown during off-hours

### 2. Personal Environment
- Manual deployment only
- Resource limits and requests
- Monitor usage patterns

## Next Steps

1. **Customize Helm Charts**: Update values.yaml for your specific needs
2. **Add Monitoring**: Integrate with Azure Monitor and Prometheus
3. **Implement CI/CD**: Add testing and staging environments
4. **Security Hardening**: Implement additional security measures
5. **Documentation**: Create service-specific deployment guides

## Support

For issues and questions:
1. Check the workflow logs in GitHub Actions
2. Review the troubleshooting section
3. Consult the LinkOps team documentation
4. Create an issue in the repository 