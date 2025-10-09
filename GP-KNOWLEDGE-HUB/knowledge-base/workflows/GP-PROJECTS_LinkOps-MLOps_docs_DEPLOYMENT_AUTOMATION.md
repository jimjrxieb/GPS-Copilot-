# 🚀 Deployment Automation Guide

This document provides a complete guide to the automated deployment pipeline for the LinkOps MLOps platform using GitHub Actions and ArgoCD.

---

## 🔄 **Complete CI/CD Pipeline**

### 📋 **Pipeline Overview**

```
Code Push → GitHub Actions → Docker Build → ArgoCD Sync → Kubernetes Deployment
```

### 🏗️ **Pipeline Components**

1. **GitHub Actions Workflows** - Automated testing, building, and deployment
2. **Docker Registry** - Container image storage (GitHub Container Registry)
3. **ArgoCD Applications** - GitOps deployment to Kubernetes
4. **AKS Cluster** - Production Kubernetes environment

---

## 🔧 **GitHub Actions Workflows**

### 📦 **MLOps Platform Workflow** (`.github/workflows/mlops-platform.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Changes in `mlops/mlops_platform/**` or `helm/mlops-platform/**`

**Jobs:**
1. **Lint** - Code quality checks (flake8, black, isort)
2. **Test** - Unit and integration tests with coverage
3. **Security Scan** - Trivy, Semgrep, GitGuardian scanning
4. **Build** - Docker image build and push
5. **Helm Package** - Helm chart packaging and release
6. **Deploy ArgoCD** - GitOps deployment trigger
7. **Notify** - Deployment status notifications

### 🎨 **Frontend Workflow** (`.github/workflows/frontend.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Changes in `frontend/**` or `helm/frontend/**`

**Jobs:**
1. **Lint** - ESLint and Prettier checks
2. **Test** - Unit and E2E tests
3. **Security Scan** - Snyk and Trivy scanning
4. **Build** - Docker image build and push
5. **Deploy** - ArgoCD deployment trigger
6. **Notify** - Deployment status notifications

---

## 🌊 **ArgoCD GitOps Deployment**

### 📋 **Application Structure**

```yaml
# helm/argocd/Application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: linkops-platform
  namespace: argocd
spec:
  destination:
    server: https://kubernetes.default.svc
    namespace: linkops
  source:
    repoURL: https://github.com/jimjrxieb/shadow-link-industries
    targetRevision: HEAD
    path: helm/linkops-full
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### 🎯 **Deployed Applications**

| Application | Purpose | Status |
|-------------|---------|--------|
| **linkops-platform** | Complete platform deployment | ✅ Active |
| **mlops-platform** | Core MLOps service | ✅ Active |
| **audit-assess** | Security and compliance | ✅ Active |
| **frontend** | Vue.js user interface | ✅ Active |
| **whis-data-input** | Data collection service | ✅ Active |
| **whis-enhance** | Content enhancement | ✅ Active |

---

## 🚀 **Deployment Commands**

### 🔧 **Manual Deployment (Fallback)**

```bash
# Deploy complete platform
helm upgrade --install linkops-full ./helm/linkops-full \
  --namespace linkops \
  --create-namespace \
  --set mlops-platform.enabled=true \
  --set audit-assess.enabled=true \
  --set frontend.enabled=true

# Deploy individual services
helm upgrade --install mlops-platform ./helm/mlops-platform \
  --namespace linkops \
  --create-namespace

helm upgrade --install frontend ./helm/frontend \
  --namespace linkops \
  --create-namespace
```

### 🌊 **ArgoCD Deployment**

```bash
# Apply ArgoCD applications
kubectl apply -f helm/argocd/Application.yaml

# Check application status
argocd app list
argocd app get linkops-platform

# Sync applications
argocd app sync linkops-platform
argocd app sync frontend

# Monitor sync status
argocd app wait linkops-platform --health --timeout 300
```

### 🔄 **Automated Deployment Flow**

1. **Code Push** → GitHub Actions triggered
2. **Build & Test** → Docker images built and tested
3. **Security Scan** → Vulnerabilities checked
4. **Image Push** → Images pushed to registry
5. **Helm Update** → Chart values updated with new image tags
6. **Git Commit** → Changes committed to repository
7. **ArgoCD Sync** → ArgoCD detects changes and syncs
8. **Kubernetes Deploy** → Applications deployed to AKS

---

## 🔒 **Security Integration**

### 🛡️ **Security Scanning Pipeline**

```yaml
# Security scanning in GitHub Actions
security-scan:
  runs-on: ubuntu-latest
  steps:
    # Trivy vulnerability scanner
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: 'mlops/mlops_platform'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    # Semgrep SAST
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/secrets
          p/owasp-top-ten
    
    # GitGuardian secrets detection
    - name: GitGuardian scan
      uses: GitGuardian/gg-shield-action@main
```

### 🔍 **Security Tools**

- ✅ **Trivy** - Container and filesystem vulnerability scanning
- ✅ **Semgrep** - Static analysis security testing (SAST)
- ✅ **GitGuardian** - Secret detection and prevention
- ✅ **Snyk** - Dependency vulnerability scanning

---

## 📊 **Monitoring & Observability**

### 🔍 **Deployment Monitoring**

```bash
# Check deployment status
kubectl get pods -n linkops
kubectl get services -n linkops
kubectl get ingress -n linkops

# Check ArgoCD application health
argocd app get linkops-platform
argocd app logs linkops-platform

# Monitor application logs
kubectl logs -l app=mlops-platform -n linkops
kubectl logs -l app=frontend -n linkops
```

### 📈 **Health Checks**

```bash
# Service health endpoints
curl http://mlops-platform-service/health
curl http://audit-assess-service/health
curl http://frontend-service/health

# ArgoCD health status
argocd app get linkops-platform --output wide
```

---

## 🔧 **Configuration Management**

### 📝 **Environment Variables**

```yaml
# values.yaml for different environments
# Development
dev:
  mlops-platform:
    image:
      repository: ghcr.io/jimjrxieb/mlops-platform
      tag: dev
    replicas: 1
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"

# Production
prod:
  mlops-platform:
    image:
      repository: ghcr.io/jimjrxieb/mlops-platform
      tag: latest
    replicas: 3
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
```

### 🔄 **Secrets Management**

```yaml
# External secrets for secure configuration
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mlops-secrets
spec:
  secretStoreRef:
    name: vault-backend
  target:
    name: mlops-secrets
  data:
  - secretKey: database-url
    remoteRef:
      key: mlops/database-url
  - secretKey: api-key
    remoteRef:
      key: mlops/api-key
```

---

## 🚨 **Troubleshooting**

### 🔍 **Common Issues**

1. **Build Failures**
   ```bash
   # Check build logs
   docker build -t test-image .
   docker run test-image
   ```

2. **Deployment Failures**
   ```bash
   # Check pod status
   kubectl describe pod <pod-name> -n linkops
   kubectl logs <pod-name> -n linkops
   ```

3. **ArgoCD Sync Issues**
   ```bash
   # Check application status
   argocd app get linkops-platform
   argocd app logs linkops-platform
   
   # Force sync
   argocd app sync linkops-platform --force
   ```

4. **Image Pull Issues**
   ```bash
   # Check image availability
   docker pull ghcr.io/jimjrxieb/mlops-platform:latest
   
   # Verify registry access
   kubectl get secrets -n linkops
   ```

### 🔧 **Debug Commands**

```bash
# Check all resources
kubectl get all -n linkops

# Check events
kubectl get events -n linkops --sort-by='.lastTimestamp'

# Check ArgoCD applications
argocd app list
argocd app get linkops-platform --output yaml

# Check Helm releases
helm list -n linkops
helm status linkops-platform -n linkops
```

---

## 🎉 **Deployment Success Criteria**

### ✅ **Verification Checklist**

- [ ] **GitHub Actions** - All workflows pass successfully
- [ ] **Docker Images** - Images built and pushed to registry
- [ ] **ArgoCD Sync** - Applications sync without errors
- [ ] **Pod Health** - All pods running and healthy
- [ ] **Service Access** - Services accessible via ingress
- [ ] **Health Checks** - All health endpoints responding
- [ ] **Frontend Load** - Vue.js application loads correctly
- [ ] **API Integration** - Frontend can call backend APIs
- [ ] **Monitoring** - Metrics and logs flowing correctly

### 🚀 **Success Indicators**

```bash
# All pods running
kubectl get pods -n linkops
# NAME                    READY   STATUS    RESTARTS   AGE
# mlops-platform-xxx      1/1     Running   0          5m
# frontend-xxx            1/1     Running   0          5m
# audit-assess-xxx        1/1     Running   0          5m

# All services accessible
curl -f http://mlops-platform-service/health
curl -f http://frontend-service/

# ArgoCD applications healthy
argocd app list
# NAME                CLUSTER                         NAMESPACE  PROJECT  STATUS  HEALTH   SYNCPOLICY  CONDITIONS  REPO  PATH  TARGET
# linkops-platform    https://kubernetes.default.svc  linkops    default  Synced  Healthy  Auto-Prune  <none>      ...   ...   HEAD
```

---

## 🎯 **Next Steps**

### 🔮 **Advanced Features**

- [ ] **Blue-Green Deployments** - Zero-downtime deployment strategy
- [ ] **Canary Deployments** - Gradual rollout with monitoring
- [ ] **Multi-Environment** - Dev, staging, production environments
- [ ] **Advanced Monitoring** - Prometheus, Grafana, alerting
- [ ] **Disaster Recovery** - Backup and restore automation

### 🔧 **Optimization**

- [ ] **Resource Optimization** - CPU and memory tuning
- [ ] **Performance Testing** - Load testing and optimization
- [ ] **Cost Optimization** - Resource usage optimization
- [ ] **Security Hardening** - Additional security measures

---

## 🎉 **Deployment Automation Complete!**

Your LinkOps MLOps platform now has **complete deployment automation** with:

- ✅ **GitHub Actions CI/CD** - Automated testing, building, and deployment
- ✅ **ArgoCD GitOps** - Declarative deployment to Kubernetes
- ✅ **Security Scanning** - Comprehensive vulnerability management
- ✅ **Monitoring** - Health checks and observability
- ✅ **Troubleshooting** - Complete debugging and recovery procedures

**The platform is ready for production deployment with full automation! 🚀** 