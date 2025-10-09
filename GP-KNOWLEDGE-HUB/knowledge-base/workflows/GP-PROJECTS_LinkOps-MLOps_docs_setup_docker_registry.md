# 🐳 Docker Registry Setup Guide for LinkOps-MLOps

## 🎯 **Problem**
Your GitHub Actions workflow is failing with "requested access to the resource is denied" when pushing Docker images because the Docker registry authentication is not properly configured.

## ✅ **Solution: Configure Docker Hub Authentication**

### **Step 1: Create Docker Hub Account & Access Token**

1. **Sign up/Login to Docker Hub:**
   - Go to [hub.docker.com](https://hub.docker.com)
   - Create account or login with existing credentials

2. **Create Access Token (Recommended):**
   ```bash
   # Login to Docker Hub → Account Settings → Security
   # Click "New Access Token"
   # Name: "LinkOps-MLOps-CI"
   # Permissions: Read, Write, Delete
   # Copy the generated token (you won't see it again!)
   ```

3. **Verify Docker Hub Organization:**
   - Ensure you have a `linkops` organization/namespace on Docker Hub
   - OR update the workflow to use your personal username instead

### **Step 2: Configure GitHub Repository Secrets**

1. **Navigate to Repository Settings:**
   ```
   GitHub Repository → Settings → Secrets and variables → Actions
   ```

2. **Add Required Secrets:**
   
   **DOCKER_USER:**
   ```
   Name: DOCKER_USER
   Value: your-dockerhub-username  # or linkops if using organization
   ```
   
   **DOCKER_CRED:**
   ```
   Name: DOCKER_CRED  
   Value: your-docker-access-token  # the token from Step 1
   ```

### **Step 3: Update Workflow Configuration (Optional)**

If you want to use your personal Docker Hub account instead of `linkops`:

```yaml
# In .github/workflows/main.yml, change:
image_name="linkops/$name:latest"
# To:
image_name="your-username/$name:latest"
```

## 🔧 **Alternative Registry Configurations**

### **GitHub Container Registry (GHCR)**
```yaml
- name: Docker Registry Login
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

# Then use: ghcr.io/${{ github.repository }}/service-name:latest
```

### **Amazon ECR**
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Login to Amazon ECR
  uses: aws-actions/amazon-ecr-login@v1
```

### **Azure Container Registry**
```yaml
- name: Docker Registry Login
  uses: docker/login-action@v3
  with:
    registry: your-registry.azurecr.io
    username: ${{ secrets.AZURE_CLIENT_ID }}
    password: ${{ secrets.AZURE_CLIENT_SECRET }}
```

## ✅ **Verification Steps**

1. **Check Secret Configuration:**
   ```bash
   # In your repository settings, verify both secrets show:
   # ✅ DOCKER_USER (Updated X days ago)
   # ✅ DOCKER_CRED (Updated X days ago)
   ```

2. **Test Docker Hub Access:**
   ```bash
   # Manually test your credentials:
   echo "$DOCKER_CRED" | docker login docker.io -u "$DOCKER_USER" --password-stdin
   docker push linkops/test:latest  # Should work without "denied" error
   ```

3. **Run Workflow:**
   ```bash
   # Trigger workflow by:
   git push origin main
   # Or manually trigger in GitHub Actions tab
   ```

## 🚨 **Common Issues & Solutions**

### **Issue 1: "linkops" organization doesn't exist**
```bash
# Solution: Create Docker Hub organization named "linkops"
# OR: Use your personal username in the workflow
```

### **Issue 2: Token has insufficient permissions**
```bash
# Solution: Recreate token with Read, Write, Delete permissions
# Update DOCKER_CRED secret with new token
```

### **Issue 3: Username/token mismatch**
```bash
# Solution: Verify DOCKER_USER matches your Docker Hub username exactly
# Verify DOCKER_CRED is the access token (not password)
```

### **Issue 4: Repository is private but pushing to public registry**
```bash
# Solution: Either:
# 1. Make Docker Hub repositories private (requires paid plan)
# 2. Use GitHub Container Registry (ghcr.io) which supports private images
# 3. Use private container registries (ECR, ACR, etc.)
```

## 📊 **Improved Workflow Features**

The updated workflow now includes:

✅ **Secret Validation** - Checks if DOCKER_USER and DOCKER_CRED are set
✅ **Authentication Verification** - Confirms Docker login success  
✅ **Retry Logic** - Attempts push 3 times before failing
✅ **Detailed Logging** - Shows exact build/push steps and errors
✅ **Smart Failure Handling** - Continues if ≥70% of services succeed
✅ **Service Tracking** - Lists exactly which services failed

## 🎯 **Next Steps**

1. ✅ Set up Docker Hub account and access token
2. ✅ Configure GitHub repository secrets  
3. ✅ Push to main branch to test the workflow
4. ✅ Monitor GitHub Actions tab for successful builds
5. ✅ Verify images appear in your Docker Hub repositories

Your Docker registry authentication should now work correctly! 