#!/bin/bash

# ============================================================================
# CD FIXER: Kubernetes Hardcoded Secrets Removal
# ============================================================================
# LAYER: CD (Deployment Infrastructure)
# WHEN: Pre-deployment, Infrastructure scan
# FIXES:
#   - CRITICAL: Hardcoded secrets in Kubernetes YAML
#   - CRITICAL: API keys in deployment manifests
#   - CRITICAL: AWS credentials in pod specs
#   - PCI-DSS 8.2.1: Don't use hardcoded credentials
#   - CIS Kubernetes Benchmark 5.4.1: Use Secrets for sensitive data
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CD FIXER: Kubernetes Hardcoded Secrets Removal"
echo "═══════════════════════════════════════════════════════"
echo "Layer: CD (Deployment Infrastructure)"
echo "When: Pre-deployment, Infrastructure scan"
echo ""

# Get project root
if [ -z "$PROJECT_ROOT" ]; then
    PROJECT_ROOT="$1"
fi

if [ -z "$PROJECT_ROOT" ]; then
    echo "❌ ERROR: PROJECT_ROOT not set"
    echo "Usage: $0 /path/to/project"
    exit 1
fi

K8S_DIR="$PROJECT_ROOT/infrastructure/k8s"
BACKUP_DIR="$PROJECT_ROOT/backup/k8s-$TIMESTAMP"

echo "Project: $PROJECT_ROOT"
echo "K8s Directory: $K8S_DIR"
echo ""

# Validation
if [ ! -d "$K8S_DIR" ]; then
    echo "❌ ERROR: Kubernetes directory not found: $K8S_DIR"
    exit 1
fi

# Create backup
echo "→ Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$K8S_DIR"/* "$BACKUP_DIR/"
echo "✅ Backup created: $BACKUP_DIR"
echo ""

# Process deployment.yaml
DEPLOYMENT_FILE="$K8S_DIR/deployment.yaml"

if [ ! -f "$DEPLOYMENT_FILE" ]; then
    echo "❌ ERROR: deployment.yaml not found"
    exit 1
fi

echo "→ Processing: $DEPLOYMENT_FILE"
echo ""

# Extract hardcoded secrets
echo "  📋 Found hardcoded secrets:"
grep -E "value: (AKIA|sk_live|aws_secret|weak-secret)" "$DEPLOYMENT_FILE" | head -10 || true
echo ""

# Create Kubernetes Secret manifest
SECRET_FILE="$K8S_DIR/secrets.yaml"

cat > "$SECRET_FILE" << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: securebank-secrets
  namespace: default
type: Opaque
stringData:
  # Database credentials
  DB_USERNAME: "postgres"
  DB_PASSWORD: "REPLACE_WITH_REAL_PASSWORD"
  DB_NAME: "securebank"
  DB_HOST: "postgres-service"

  # JWT Secret
  JWT_SECRET: "REPLACE_WITH_STRONG_SECRET_32_CHARS"

  # AWS Credentials (Better: Use IAM roles instead!)
  AWS_ACCESS_KEY_ID: "REPLACE_WITH_IAM_ROLE"
  AWS_SECRET_ACCESS_KEY: "REPLACE_WITH_IAM_ROLE"

  # Stripe API Key
  REACT_APP_API_KEY: "REPLACE_WITH_REAL_STRIPE_KEY"

  # Payment Gateway
  PAYMENT_API_KEY: "REPLACE_WITH_PAYMENT_GATEWAY_KEY"

---
# Alternative: Use External Secrets Operator with AWS Secrets Manager
# apiVersion: external-secrets.io/v1beta1
# kind: ExternalSecret
# metadata:
#   name: securebank-secrets
# spec:
#   refreshInterval: 1h
#   secretStoreRef:
#     name: aws-secrets-manager
#     kind: SecretStore
#   target:
#     name: securebank-secrets
#   data:
#   - secretKey: DB_PASSWORD
#     remoteRef:
#       key: securebank/production/db
#       property: password
EOF

echo "  ✅ Created: secrets.yaml (Kubernetes Secret manifest)"
echo ""

# Update deployment.yaml to use Secrets
echo "→ Updating deployment.yaml to reference Kubernetes Secrets..."

# Create updated deployment with secret references
cat > "$DEPLOYMENT_FILE" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: securebank-backend
  namespace: default
  labels:
    app: securebank
    component: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: securebank
      component: backend
  template:
    metadata:
      labels:
        app: securebank
        component: backend
    spec:
      serviceAccountName: securebank-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: backend
        image: securebank/backend:latest
        ports:
        - containerPort: 3000
          protocol: TCP
        env:
        # ✅ FIXED: Using Kubernetes Secrets instead of hardcoded values
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: DB_USERNAME
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: DB_PASSWORD
        - name: DB_NAME
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: DB_NAME
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: DB_HOST
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: JWT_SECRET
        - name: AWS_REGION
          value: us-east-1
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: AWS_ACCESS_KEY_ID
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: AWS_SECRET_ACCESS_KEY
        - name: S3_PAYMENT_BUCKET
          value: securebank-payment-receipts-production
        - name: S3_AUDIT_BUCKET
          value: securebank-audit-logs-production
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: securebank-frontend
  namespace: default
  labels:
    app: securebank
    component: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: securebank
      component: frontend
  template:
    metadata:
      labels:
        app: securebank
        component: frontend
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: frontend
        image: securebank/frontend:latest
        ports:
        - containerPort: 80
          protocol: TCP
        env:
        - name: REACT_APP_API_URL
          value: http://securebank-backend-service:3000
        # ✅ FIXED: Stripe key moved to Secret
        - name: REACT_APP_API_KEY
          valueFrom:
            secretKeyRef:
              name: securebank-secrets
              key: REACT_APP_API_KEY
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
EOF

echo "  ✅ Updated: deployment.yaml (now uses secretKeyRef)"
echo ""

# Create README with instructions
README_FILE="$K8S_DIR/SECRETS-README.md"

cat > "$README_FILE" << 'EOF'
# Kubernetes Secrets Setup

## ⚠️ IMPORTANT: Secrets Were Removed

Hardcoded secrets have been removed from `deployment.yaml` and moved to `secrets.yaml`.

## Setup Instructions

### Option 1: Manual Secrets (Development)

```bash
# 1. Edit secrets.yaml and replace placeholder values
vi infrastructure/k8s/secrets.yaml

# 2. Apply the secret
kubectl apply -f infrastructure/k8s/secrets.yaml

# 3. Deploy the application
kubectl apply -f infrastructure/k8s/deployment.yaml
```

### Option 2: Base64 Encoded (Production)

```bash
# Create secret from literal values
kubectl create secret generic securebank-secrets \
  --from-literal=DB_PASSWORD='your-strong-password' \
  --from-literal=JWT_SECRET='your-32-char-secret' \
  --from-literal=AWS_ACCESS_KEY_ID='AKIAXXXXX' \
  --from-literal=AWS_SECRET_ACCESS_KEY='xxxxx' \
  --from-literal=REACT_APP_API_KEY='sk_live_xxxxx' \
  --from-literal=PAYMENT_API_KEY='xxxxx' \
  --dry-run=client -o yaml > infrastructure/k8s/secrets.yaml

# Apply
kubectl apply -f infrastructure/k8s/secrets.yaml
```

### Option 3: External Secrets Operator (RECOMMENDED)

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets

# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name securebank/production/credentials \
  --secret-string '{
    "DB_PASSWORD": "xxx",
    "JWT_SECRET": "xxx",
    "AWS_ACCESS_KEY_ID": "xxx",
    "AWS_SECRET_ACCESS_KEY": "xxx",
    "REACT_APP_API_KEY": "sk_live_xxx",
    "PAYMENT_API_KEY": "xxx"
  }'

# Create SecretStore
kubectl apply -f infrastructure/k8s/secret-store.yaml

# External Secrets Operator will sync automatically
```

## Best Practices

✅ **DO:**
- Use IAM roles for AWS (remove AWS_ACCESS_KEY_ID/SECRET)
- Rotate secrets regularly
- Use External Secrets Operator for production
- Enable encryption at rest for secrets
- Audit secret access

❌ **DON'T:**
- Commit `secrets.yaml` with real values to git
- Use weak passwords
- Share secrets in Slack/email
- Hardcode secrets in deployment YAML

## Security Checklist

- [ ] Secrets stored in Kubernetes Secrets (not in YAML)
- [ ] secrets.yaml added to .gitignore
- [ ] Using IAM roles instead of AWS keys (when possible)
- [ ] Secrets rotated within last 90 days
- [ ] Access to secrets restricted by RBAC
- [ ] Encryption at rest enabled
EOF

echo "  ✅ Created: SECRETS-README.md (setup instructions)"
echo ""

# Update .gitignore
GITIGNORE="$PROJECT_ROOT/.gitignore"
if [ -f "$GITIGNORE" ]; then
    if ! grep -q "secrets.yaml" "$GITIGNORE"; then
        echo "" >> "$GITIGNORE"
        echo "# Kubernetes Secrets (contains sensitive data)" >> "$GITIGNORE"
        echo "infrastructure/k8s/secrets.yaml" >> "$GITIGNORE"
        echo "k8s/secrets.yaml" >> "$GITIGNORE"
        echo "  ✅ Updated: .gitignore (excludes secrets.yaml)"
    else
        echo "  ✅ .gitignore already excludes secrets.yaml"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CD FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ Hardcoded secrets removed from deployment.yaml"
echo "  ✅ Created secrets.yaml (Kubernetes Secret manifest)"
echo "  ✅ Updated deployment to use secretKeyRef"
echo "  ✅ Created SECRETS-README.md with setup instructions"
echo "  ✅ Updated .gitignore"
echo ""
echo "⚠️  NEXT STEPS (REQUIRED):"
echo "  1. Edit infrastructure/k8s/secrets.yaml"
echo "  2. Replace placeholder values with real secrets"
echo "  3. Apply: kubectl apply -f infrastructure/k8s/secrets.yaml"
echo "  4. Deploy: kubectl apply -f infrastructure/k8s/deployment.yaml"
echo ""
echo "📚 See: infrastructure/k8s/SECRETS-README.md for details"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-k8s-hardcoded-secrets.sh"
echo "Layer: CD (Deployment Infrastructure)"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Hardcoded secrets removed: YES"
echo "Kubernetes Secrets created: YES"
echo ""
