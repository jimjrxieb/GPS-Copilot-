# CI/CD Setup Across LinkOps Repositories

## Overview
This document describes the CI/CD setup across all three LinkOps repositories with centralized dispatch capabilities.

## Repository Structure

### 1. LinkOps-Arise (Infrastructure)
**Purpose:** Terraform infrastructure management for demo and personal environments

**CI Workflow:** `.github/workflows/ci.yml`
- Runs on: `push`, `pull_request`
- Validates both demo and personal environments
- Steps:
  - Terraform init, format check, validate, plan
  - Matrix strategy for demo/personal environments

**Destroy Workflow:** `.github/workflows/destroy-demo.yml`
- Runs on: `workflow_dispatch`
- Requires confirmation input: "DESTROY"
- Destroys demo environment only (personal protected)

### 2. LinkOps-Manifests (Kubernetes/Helm)
**Purpose:** Kubernetes manifests and Helm charts for GitOps deployment

**CI Workflow:** `.github/workflows/ci.yml`
- Runs on: `push`, `pull_request`
- Validates:
  - Kubernetes YAML files (yamllint)
  - Helm charts (helm lint)
  - ArgoCD application manifests

### 3. LinkOps-MLOps (Application Deployment)
**Purpose:** Microservice builds, Docker images, and deployment orchestration

**Existing Workflows:**
- `deploy-aks.yml` - Multi-service deployment to AKS
- `update-manifests.yml` - GitOps manifest updates for personal environment
- Individual service workflows (whis, auditguard, etc.)

**New Dispatch Workflow:** `.github/workflows/dispatch-all.yml`
- Centralized orchestration across all repositories
- Manual trigger with environment and action selection

## Master Dispatch Workflow

### Location: `LinkOps-MLOps/.github/workflows/dispatch-all.yml`

### Features:
- **Manual Trigger:** `workflow_dispatch`
- **Input Parameters:**
  - `environment`: demo | personal
  - `action`: deploy | ci | destroy

### Actions:

#### 1. CI Action
Triggers CI workflows in all repositories:
```bash
# LinkOps-Arise CI
gh workflow run ci.yml --repo jimjrxieb/LinkOps-Arise --ref main

# LinkOps-Manifests CI  
gh workflow run ci.yml --repo jimjrxieb/LinkOps-Manifests --ref main
```

#### 2. Deploy Action
Deploys to specified environment:
```bash
# LinkOps-MLOps Deploy
gh workflow run deploy-aks.yml --repo jimjrxieb/LinkOps-MLOps --ref main --field environment=demo

# LinkOps-MLOps Update Manifests (personal only)
gh workflow run update-manifests.yml --repo jimjrxieb/LinkOps-MLOps --ref main
```

#### 3. Destroy Action
Destroys demo environment only:
```bash
# LinkOps-Arise Destroy (demo only)
gh workflow run destroy-demo.yml --repo jimjrxieb/LinkOps-Arise --ref main --field confirm=DESTROY
```

## Required GitHub Secrets

### LinkOps-Arise
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CREDENTIALS`

### LinkOps-MLOps
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CREDENTIALS`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `GITHUB_TOKEN` (for cross-repo dispatch)

### LinkOps-Manifests
- No secrets required (validation only)

## Usage Examples

### Run CI on All Repositories
1. Go to LinkOps-MLOps Actions
2. Select "Dispatch All Microservices"
3. Choose:
   - Environment: `demo` (or any)
   - Action: `ci`
4. Click "Run workflow"

### Deploy to Demo Environment
1. Go to LinkOps-MLOps Actions
2. Select "Dispatch All Microservices"
3. Choose:
   - Environment: `demo`
   - Action: `deploy`
4. Click "Run workflow"

### Deploy to Personal Environment (GitOps)
1. Go to LinkOps-MLOps Actions
2. Select "Dispatch All Microservices"
3. Choose:
   - Environment: `personal`
   - Action: `deploy`
4. Click "Run workflow"
   - This triggers both deploy-aks.yml and update-manifests.yml

### Destroy Demo Environment
1. Go to LinkOps-MLOps Actions
2. Select "Dispatch All Microservices"
3. Choose:
   - Environment: `demo`
   - Action: `destroy`
4. Click "Run workflow"
   - This triggers the destroy-demo.yml workflow in LinkOps-Arise

## Security Considerations

1. **Personal Environment Protection:** Cannot be destroyed via workflows
2. **Demo Environment Safety:** Requires explicit confirmation
3. **Cross-Repository Access:** Uses GitHub token with appropriate permissions
4. **Azure Credentials:** Stored as GitHub secrets, rotated regularly

## Troubleshooting

### Common Issues:
1. **GitHub CLI Authentication:** Ensure `GITHUB_TOKEN` has repo permissions
2. **Azure Authentication:** Verify credentials are valid and not expired
3. **Workflow Not Found:** Check if target workflow exists in repository
4. **Permission Denied:** Verify repository access and token permissions

### Debug Steps:
1. Check workflow run logs in each repository
2. Verify GitHub secrets are properly configured
3. Test individual workflows before using dispatch
4. Check Azure subscription and resource group permissions 