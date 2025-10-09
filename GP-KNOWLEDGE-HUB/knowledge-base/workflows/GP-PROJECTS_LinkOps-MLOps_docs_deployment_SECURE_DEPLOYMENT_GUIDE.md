# 🔐 Secure Deployment Guide

This guide ensures secure deployment of LinkOps without any hardcoded secrets.

## 🚨 Critical Security Requirements

### Environment Variables Required

**Before running any deployment scripts, set these environment variables:**

```bash
# Required for all deployments
export GRAFANA_ADMIN_PASSWORD="your-secure-grafana-password"
export POSTGRES_PASSWORD="your-secure-postgres-password"
export OPENAI_API_KEY="your-openai-api-key"
```

## 🛡️ Deployment Methods

### Method 1: Environment Variables (Recommended)

```bash
# Set environment variables
export GRAFANA_ADMIN_PASSWORD="YourSecurePassword123!"
export POSTGRES_PASSWORD="YourSecureDBPassword123!"

# Run deployment
./infrastructure/deploy.sh
```

## 🔧 Script Security Features

### Environment Variable Validation

All scripts now validate required environment variables:

```bash
# Scripts will fail if these are not set
: "${GRAFANA_ADMIN_PASSWORD:?Environment variable GRAFANA_ADMIN_PASSWORD not set}"
: "${POSTGRES_PASSWORD:?Environment variable POSTGRES_PASSWORD not set}"
```

### No Hardcoded Defaults

- ❌ No more `LinkOps2024!` defaults
- ❌ No more `postgres` defaults
- ✅ All passwords must be explicitly provided
- ✅ Scripts fail fast if secrets are missing
