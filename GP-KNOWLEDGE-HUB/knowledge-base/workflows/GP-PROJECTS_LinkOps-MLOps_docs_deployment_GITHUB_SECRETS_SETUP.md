# GitHub Secrets Setup Guide

This guide explains how to set up the required GitHub secrets for the LinkOps CI/CD pipeline.

## Required Secrets

### 1. Docker Hub Authentication
- **DOCKER_USER**: Your Docker Hub username
- **DOCKER_CRED**: Your Docker Hub password or access token

### 2. SonarCloud Integration
- **SONAR_TOKEN**: Your SonarCloud authentication token
- **SONAR_PROJECT_KEY**: Your SonarCloud project key
- **SONAR_ORG**: Your SonarCloud organization key

### 3. GitGuardian Secret Scanning
- **GITGUARDIAN_API_KEY**: Your GitGuardian API key

### 4. Infrastructure Secrets (Optional - for deployment)
- **GRAFANA_ADMIN_PASSWORD**: Admin password for Grafana
- **POSTGRES_PASSWORD**: PostgreSQL database password
- **ACR_LOGIN_SERVER**: Azure Container Registry login server
- **ACR_USERNAME**: Azure Container Registry username
- **ACR_PASSWORD**: Azure Container Registry password
- **KUBECONFIG**: Base64-encoded kubeconfig for cluster access

## How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value

## Security Best Practices

### For Docker Hub:
- Use Docker Hub access tokens instead of passwords
- Create tokens with minimal required permissions
- Rotate tokens regularly

### For SonarCloud:
- Generate project-specific tokens
- Use organization-level tokens for multiple projects
- Store project keys securely

### For GitGuardian:
- Use API keys with appropriate scopes
- Rotate keys periodically
- Monitor API usage

### For Infrastructure:
- Use strong, unique passwords
- Store passwords in a secure password manager
- Rotate passwords regularly
- Use environment-specific values

## Example Secret Values

```bash
# Generate base64 encoded values for Kubernetes secrets
echo -n "your_secure_password" | base64

# Example outputs:
# DOCKER_USER: your-dockerhub-username
# DOCKER_CRED: your-dockerhub-token
# SONAR_TOKEN: sqp_xxxxxxxxxxxxxxxxxxxx
# SONAR_PROJECT_KEY: your-org_your-project
# SONAR_ORG: your-org-key
# GITGUARDIAN_API_KEY: ggp_xxxxxxxxxxxxxxxxxxxx
# GRAFANA_ADMIN_PASSWORD: YourSecurePassword123!
# POSTGRES_PASSWORD: YourSecureDBPassword123!
```

## Verification

After adding secrets, you can verify they're working by:

1. Making a small change to any service
2. Pushing the change to trigger a workflow
3. Checking that the workflow completes successfully
4. Verifying that Docker images are pushed to the registry
5. Confirming SonarCloud scans are uploaded

## Troubleshooting

### Common Issues:
- **Secret not found**: Ensure the secret name matches exactly (case-sensitive)
- **Authentication failed**: Verify credentials are correct and not expired
- **Permission denied**: Check that tokens have appropriate permissions
- **Base64 encoding**: Ensure values are properly base64 encoded for Kubernetes secrets

### Debug Commands:
```bash
# Test Docker Hub login
docker login -u $DOCKER_USER -p $DOCKER_CRED

# Test SonarCloud connection
curl -u $SONAR_TOKEN: https://sonarcloud.io/api/authentication/validate

# Test GitGuardian API
curl -H "Authorization: Token $GITGUARDIAN_API_KEY" https://api.gitguardian.com/v1/health
``` 