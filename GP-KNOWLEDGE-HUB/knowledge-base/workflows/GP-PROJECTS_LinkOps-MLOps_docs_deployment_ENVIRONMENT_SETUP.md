# Environment Setup Guide

## 🔐 **Secure Environment Configuration**

This guide explains how to set up environment variables securely for the LinkOps-MLOps platform.

## 📋 **Required Environment Variables**

### **1. Database Configuration**
```bash
# PostgreSQL
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_USER=linkops
POSTGRES_DB=linkops

# pgAdmin
PGADMIN_EMAIL=your_email@domain.com
PGADMIN_PASSWORD=your_secure_pgadmin_password
```

### **2. API Keys**
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### **3. Security Keys**
```bash
# Application Secret Key (generate a secure random key)
SECRET_KEY=your_secure_secret_key_here
```

### **4. Azure Configuration**
```bash
# Azure Service Principal
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_SUBSCRIPTION_ID=your-azure-subscription-id

# Azure Resources
AZURE_RESOURCE_GROUP=your-resource-group-name
AZURE_ACR_NAME=your-acr-name
AZURE_KEY_VAULT_NAME=your-key-vault-name
AZURE_AKS_CLUSTER_NAME=your-aks-cluster-name
AZURE_AKS_RESOURCE_GROUP=your-aks-resource-group
```

## 🚀 **Setup Instructions**

### **Step 1: Copy Environment Template**
```bash
# Copy the template to create your .env file
cp .env.template .env
```

### **Step 2: Update Environment Variables**
Edit the `.env` file and replace all placeholder values with your actual credentials:

```bash
# Example .env file structure
POSTGRES_PASSWORD=MySecurePassword123!
PGADMIN_EMAIL=admin@yourdomain.com
PGADMIN_PASSWORD=MyPgAdminPassword456!
OPENAI_API_KEY=sk-proj-your-actual-openai-key
SECRET_KEY=MySecureSecretKey789!
AZURE_CLIENT_ID=your-actual-azure-client-id
AZURE_CLIENT_SECRET=your-actual-azure-client-secret
# ... etc
```

### **Step 3: Verify Configuration**
```bash
# Check that all placeholders are replaced
grep -E "\$\{" .env
# Should return no results if all placeholders are replaced
```

## 🔒 **Security Best Practices**

### **1. Never Commit .env Files**
- ✅ `.env` is already in `.gitignore`
- ✅ `.env.backup` is already in `.gitignore`
- ❌ Never commit actual credentials to git

### **2. Use Strong Passwords**
- Use at least 16 characters
- Include uppercase, lowercase, numbers, and symbols
- Avoid common patterns or dictionary words

### **3. Rotate Credentials Regularly**
- Change passwords every 90 days
- Rotate API keys quarterly
- Monitor for unauthorized access

### **4. Environment-Specific Configuration**
```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

## 🐳 **Docker Environment Variables**

### **Local Development**
```bash
# Use .env file
docker-compose up -d
```

### **Production Deployment**
```bash
# Set environment variables directly
export POSTGRES_PASSWORD=your_production_password
export OPENAI_API_KEY=your_production_api_key
docker-compose -f docker-compose.prod.yml up -d
```

### **Kubernetes Secrets**
```yaml
# Create Kubernetes secrets for production
apiVersion: v1
kind: Secret
metadata:
  name: linkops-secrets
type: Opaque
data:
  postgres-password: <base64-encoded-password>
  openai-api-key: <base64-encoded-api-key>
  secret-key: <base64-encoded-secret-key>
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Environment Variables Not Loading**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify file permissions
   chmod 600 .env
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   docker-compose exec postgres psql -U linkops -d linkops
   ```

3. **API Key Issues**
   ```bash
   # Test OpenAI API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### **Validation Script**
```bash
#!/bin/bash
# validate_env.sh
echo "🔍 Validating environment configuration..."

# Check required variables
required_vars=(
  "POSTGRES_PASSWORD"
  "OPENAI_API_KEY"
  "SECRET_KEY"
  "AZURE_CLIENT_ID"
  "AZURE_CLIENT_SECRET"
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ Missing: $var"
  else
    echo "✅ Found: $var"
  fi
done

echo "🎯 Environment validation complete!"
```

## 📚 **Additional Resources**

- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Azure Service Principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

## 🎯 **Quick Start**

1. Copy `.env.template` to `.env`
2. Update all placeholder values with your credentials
3. Run `docker-compose up -d`
4. Verify all services are healthy with `python tools/health_check.py`

**Your LinkOps-MLOps environment is now securely configured!** 🔐 