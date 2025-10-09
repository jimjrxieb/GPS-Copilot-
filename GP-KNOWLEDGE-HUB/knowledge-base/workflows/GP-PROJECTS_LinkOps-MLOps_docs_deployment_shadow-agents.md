# 🛡️ Shadow Agents Deployment Guide

## Overview

Shadow Agents are deployable AI agents built from logic sources using Helm charts and ArgoCD. This guide covers the complete deployment process for all LinkOps shadow agents.

## Architecture

```
Logic Sources → Agent Registry → Agent Launcher → Helm Charts → ArgoCD → Kubernetes
```

### Components

- **Logic Sources**: `igris_logic`, `katie_logic`, `whis_logic`, `james_logic`
- **Agent Registry**: Maps logic sources to agent configurations
- **Agent Launcher**: Deploys agents using Helm and ArgoCD
- **Helm Charts**: Kubernetes manifests for each agent
- **ArgoCD**: GitOps deployment automation

## Available Shadow Agents

### 🏗️ Igris Logic
- **Role**: Platform Engineering Agent
- **Capabilities**: Infrastructure Analysis, Security Assessment, OpenDevin Integration
- **Helm Chart**: `igris_logic`
- **Port**: 8000

### 🛡️ Katie Logic
- **Role**: Kubernetes AI Agent & Cluster Guardian
- **Capabilities**: Cluster Management, Resource Scaling, Log Analysis, K8GPT Integration
- **Helm Chart**: `katie_logic`
- **Port**: 8000
- **Special**: Requires kubeconfig access

### 🧠 Whis Logic
- **Role**: Intelligence Processing & Analysis Agent
- **Capabilities**: Data Processing, Intelligence Analysis, Pattern Recognition
- **Helm Chart**: `whis_logic`
- **Port**: 8000
- **Special**: Persistent storage for intelligence data

### 🎯 James Logic
- **Role**: Personal AI Assistant & Executive Agent
- **Capabilities**: Voice Interaction, Image Processing, Executive Assistance
- **Helm Chart**: `james_logic`
- **Port**: 8000
- **Special**: Voice and image processing capabilities

## Prerequisites

### 1. Kubernetes Cluster
```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

### 2. ArgoCD Installation
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 3. Required Secrets
```bash
# Create OpenAI secret
kubectl create secret generic openai-secret \
  --from-literal=key=your-openai-api-key \
  -n linkops

# Create Katie kubeconfig secret (for Katie Logic)
kubectl create secret generic katie-kubeconfig \
  --from-file=config=$HOME/.kube/config \
  -n linkops
```

## Deployment Methods

### Method 1: Using FickNury Deploy (Recommended)

#### 1. Deploy FickNury Deploy Service
```bash
# Deploy the deployment service
kubectl apply -f shadows/ficknury_deploy/k8s/
```

#### 2. Deploy Agents via API
```bash
# Deploy Igris Logic
curl -X POST http://ficknury-deploy:8000/deploy/agent \
  -H "Content-Type: application/json" \
  -d '{
    "logic_source": "igris_logic",
    "deployment_config": {
      "env": {
        "LOG_LEVEL": "INFO",
        "OPENAI_MODEL": "gpt-4"
      }
    }
  }'

# Deploy Katie Logic
curl -X POST http://ficknury-deploy:8000/deploy/agent \
  -H "Content-Type: application/json" \
  -d '{
    "logic_source": "katie_logic",
    "deployment_config": {
      "env": {
        "LOG_LEVEL": "INFO",
        "K8GPT_ENABLED": "true"
      }
    }
  }'

# Deploy Whis Logic
curl -X POST http://ficknury-deploy:8000/deploy/agent \
  -H "Content-Type: application/json" \
  -d '{
    "logic_source": "whis_logic",
    "deployment_config": {
      "env": {
        "LOG_LEVEL": "INFO",
        "PROCESSING_MODE": "intelligence"
      }
    }
  }'

# Deploy James Logic
curl -X POST http://ficknury-deploy:8000/deploy/agent \
  -H "Content-Type: application/json" \
  -d '{
    "logic_source": "james_logic",
    "deployment_config": {
      "env": {
        "LOG_LEVEL": "INFO",
        "VOICE_ENABLED": "true"
      }
    }
  }'
```

#### 3. Check Deployment Status
```bash
# List all deployed agents
curl http://ficknury-deploy:8000/deploy/agents

# Check specific agent status
curl http://ficknury-deploy:8000/deploy/agent/igris/status
```

### Method 2: Direct ArgoCD Application

#### 1. Apply ArgoCD Applications
```bash
# Apply all agent applications
kubectl apply -f LinkOps-Manifests/shadows/

# Or apply individually
kubectl apply -f LinkOps-Manifests/shadows/igris_logic.yaml
kubectl apply -f LinkOps-Manifests/shadows/katie_logic.yaml
kubectl apply -f LinkOps-Manifests/shadows/whis_logic.yaml
kubectl apply -f LinkOps-Manifests/shadows/james_logic.yaml
```

#### 2. Monitor in ArgoCD UI
```bash
# Port forward ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access at https://localhost:8080
# Username: admin
# Password: (from prerequisites)
```

### Method 3: Helm Direct Deployment

#### 1. Add Helm Repository
```bash
helm repo add linkops https://github.com/shadow-link-industries/LinkOps-Helm.git
helm repo update
```

#### 2. Deploy Agents
```bash
# Create namespace
kubectl create namespace linkops

# Deploy Igris Logic
helm install igris-logic linkops/igris_logic \
  --namespace linkops \
  --set image.repository=ghcr.io/shadow-link-industries/igris_logic \
  --set image.tag=latest

# Deploy Katie Logic
helm install katie-logic linkops/katie_logic \
  --namespace linkops \
  --set image.repository=ghcr.io/shadow-link-industries/katie_logic \
  --set image.tag=latest

# Deploy Whis Logic
helm install whis-logic linkops/whis_logic \
  --namespace linkops \
  --set image.repository=ghcr.io/shadow-link-industries/whis_logic \
  --set image.tag=latest

# Deploy James Logic
helm install james-logic linkops/james_logic \
  --namespace linkops \
  --set image.repository=ghcr.io/shadow-link-industries/james_logic \
  --set image.tag=latest
```

## Configuration

### Environment Variables

#### Common Variables
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `OPENAI_MODEL`: OpenAI model to use (gpt-4, gpt-3.5-turbo)
- `OPENAI_API_KEY`: OpenAI API key (from secret)

#### Agent-Specific Variables

**Katie Logic:**
- `K8GPT_ENABLED`: Enable K8GPT integration (true/false)
- `K8GPT_API_URL`: K8GPT API endpoint

**Whis Logic:**
- `PROCESSING_MODE`: Processing mode (intelligence, analysis)
- `BATCH_SIZE`: Batch processing size
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests

**James Logic:**
- `VOICE_ENABLED`: Enable voice capabilities (true/false)
- `IMAGE_PROCESSING_ENABLED`: Enable image processing (true/false)
- `ASSISTANT_PERSONALITY`: Assistant personality (calm_powerful)

### Resource Configuration

#### Default Resources
```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi
```

#### Whis Logic (Higher Resources)
```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

### Persistence

#### Whis Logic Data Persistence
```yaml
persistence:
  enabled: true
  size: 10Gi
  storageClass: ""
  accessMode: ReadWriteOnce
```

## Monitoring & Troubleshooting

### Check Agent Status
```bash
# Check all deployments
kubectl get deployments -n linkops

# Check pods
kubectl get pods -n linkops

# Check services
kubectl get services -n linkops

# Check ArgoCD applications
kubectl get applications -n argocd
```

### View Logs
```bash
# View agent logs
kubectl logs -f deployment/igris-logic -n linkops
kubectl logs -f deployment/katie-logic -n linkops
kubectl logs -f deployment/whis-logic -n linkops
kubectl logs -f deployment/james-logic -n linkops
```

### Health Checks
```bash
# Check agent health endpoints
curl http://igris-logic:8000/health
curl http://katie-logic:8000/health
curl http://whis-logic:8000/health
curl http://james-logic:8000/health
```

### Common Issues

#### 1. Image Pull Errors
```bash
# Check image availability
docker pull ghcr.io/shadow-link-industries/igris_logic:latest

# Verify image credentials
kubectl get secrets -n linkops
```

#### 2. Resource Constraints
```bash
# Check resource usage
kubectl top pods -n linkops

# Scale up resources if needed
kubectl patch deployment igris-logic -n linkops \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"igris","resources":{"limits":{"cpu":"1000m","memory":"1Gi"}}}]}}}}'
```

#### 3. ArgoCD Sync Issues
```bash
# Check ArgoCD application status
kubectl describe application igris-logic -n argocd

# Force sync
kubectl patch application igris-logic -n argocd \
  -p '{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true}}}}'
```

## Scaling & High Availability

### Horizontal Pod Autoscaling
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### Multi-Node Deployment
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - igris-logic
        topologyKey: kubernetes.io/hostname
```

## Security

### RBAC Configuration
- Each agent has its own ServiceAccount
- Katie Logic has cluster-wide permissions for Kubernetes management
- Other agents have namespace-scoped permissions

### Network Policies
```yaml
# Example network policy for Igris Logic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: igris-logic-network-policy
  namespace: linkops
spec:
  podSelector:
    matchLabels:
      app: igris-logic
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: linkops
    ports:
    - protocol: TCP
      port: 8000
```

## Backup & Recovery

### Backup Agent Configurations
```bash
# Export agent registry
curl http://ficknury-deploy:8000/registry/export?format=yaml > agent_registry_backup.yaml

# Backup ArgoCD applications
kubectl get applications -n argocd -o yaml > argocd_apps_backup.yaml
```

### Restore Agents
```bash
# Restore ArgoCD applications
kubectl apply -f argocd_apps_backup.yaml

# Restore agent registry
kubectl apply -f agent_registry_backup.yaml
```

## Next Steps

1. **Customize Configurations**: Modify values.yaml for your environment
2. **Set Up Monitoring**: Configure Prometheus and Grafana
3. **Implement CI/CD**: Set up automated deployments
4. **Security Hardening**: Apply network policies and RBAC
5. **Performance Tuning**: Optimize resource allocations

## Support

For issues and questions:
- Check the troubleshooting section above
- Review agent-specific documentation
- Open an issue in the LinkOps repository
- Contact the Shadow Link Industries team 