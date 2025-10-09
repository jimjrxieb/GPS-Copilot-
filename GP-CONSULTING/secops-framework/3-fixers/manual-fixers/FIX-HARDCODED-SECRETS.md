# Manual Fix Guide: Hardcoded Secrets Migration

## Problem

**PCI-DSS Violation:** Hardcoded credentials in source code
- **Requirement:** PCI-DSS 8.2.1 - Strong authentication
- **Risk:** HIGH - Credential exposure in Git history
- **Current State:** JWT secrets, API keys, database passwords in code

## Solution

Migrate all secrets to AWS Secrets Manager with IRSA (IAM Roles for Service Accounts) in EKS.

## Prerequisites

- AWS Secrets Manager enabled
- EKS cluster with OIDC provider configured
- IAM roles created for service accounts

## Step-by-Step Instructions

### Step 1: Identify All Hardcoded Secrets

```bash
# Run Gitleaks scan
gitleaks detect --source . --report-format json --report-path secrets-report.json

# Review findings
jq '.[] | {file: .File, secret: .Description}' secrets-report.json
```

### Step 2: Create Secrets in AWS Secrets Manager

```bash
# Database credentials
aws secretsmanager create-secret \
  --name securebank/db/credentials \
  --secret-string '{
    "username": "securebank_user",
    "password": "'$(openssl rand -base64 32)'",
    "host": "securebank-db.cluster-xxxxx.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "database": "securebank"
  }'

# JWT secret
aws secretsmanager create-secret \
  --name securebank/jwt/secret \
  --secret-string '{"jwt_secret": "'$(openssl rand -base64 64)'"}'

# API keys
aws secretsmanager create-secret \
  --name securebank/api/keys \
  --secret-string '{
    "stripe_key": "sk_live_xxxxx",
    "sendgrid_key": "SG.xxxxx"
  }'
```

### Step 3: Configure IRSA (IAM Roles for Service Accounts)

```bash
# Create IAM policy for Secrets Manager access
cat > /tmp/secrets-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:*:secret:securebank/*"
      ]
    }
  ]
}
EOF

# Create IAM role with OIDC trust relationship
eksctl create iamserviceaccount \
  --name securebank-backend \
  --namespace securebank \
  --cluster securebank-cluster \
  --attach-policy-arn arn:aws:iam::ACCOUNT_ID:policy/SecureBankSecretsPolicy \
  --approve
```

### Step 4: Update Backend to Use Secrets Manager

See: `secops/3-fixers/auto-fixers/fix-secrets.sh`

### Step 5: Remove Secrets from Git History

```bash
# Use BFG Repo-Cleaner
brew install bfg

# Remove secrets from entire Git history
bfg --replace-text secrets.txt .git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (DANGEROUS - coordinate with team)
git push --force --all
```

## Validation

```bash
# Verify no hardcoded secrets remain
gitleaks detect --source . --no-git

# Test Secrets Manager integration
kubectl exec -it deployment/securebank-backend -- node -e "
  const AWS = require('aws-sdk');
  const sm = new AWS.SecretsManager();
  sm.getSecretValue({SecretId: 'securebank/db/credentials'}, (err, data) => {
    if (err) console.error(err);
    else console.log('✅ Secrets Manager working:', JSON.parse(data.SecretString).database);
  });
"
```

## Compliance Impact

**Before:**
- ❌ PCI-DSS 8.2.1 - FAIL
- ❌ SOC2 CC6.1 - FAIL

**After:**
- ✅ PCI-DSS 8.2.1 - PASS
- ✅ SOC2 CC6.1 - PASS

---

**Severity:** HIGH | **Effort:** 2 hours
