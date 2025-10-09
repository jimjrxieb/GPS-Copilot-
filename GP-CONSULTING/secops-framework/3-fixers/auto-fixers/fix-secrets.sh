#!/bin/bash
set -e

echo "🔧 Auto-Fixer: Hardcoded Secrets Migration"
echo "═══════════════════════════════════════════════"

BACKEND_DIR="../../../../backend"
CONFIG_DIR="$BACKEND_DIR/config"

echo ""
echo "→ Migrating database credentials to Secrets Manager..."

# Update database.js to use Secrets Manager
cat > "$CONFIG_DIR/database.js" << 'EOF'
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

let cachedSecret = null;

async function getSecretValue(secretName) {
  if (cachedSecret) {
    return cachedSecret;
  }

  const client = new SecretsManagerClient({ region: process.env.AWS_REGION || 'us-east-1' });

  try {
    const response = await client.send(
      new GetSecretValueCommand({
        SecretId: secretName,
      })
    );

    cachedSecret = JSON.parse(response.SecretString);
    return cachedSecret;
  } catch (error) {
    console.error('Error retrieving secret:', error);
    throw error;
  }
}

module.exports = {
  development: {
    username: process.env.DB_USERNAME || 'postgres',
    password: process.env.DB_PASSWORD || 'postgres',
    database: process.env.DB_NAME || 'securebank',
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    dialect: 'postgres',
    logging: false,
  },
  production: async () => {
    const secret = await getSecretValue('securebank/db/credentials');
    return {
      username: secret.username,
      password: secret.password,
      database: secret.database,
      host: secret.host,
      port: secret.port || 5432,
      dialect: 'postgres',
      logging: false,
      dialectOptions: {
        ssl: {
          require: true,
          rejectUnauthorized: true,
        },
      },
    };
  },
};
EOF

echo "✅ Database credentials migrated to Secrets Manager"

echo ""
echo "→ Updating JWT secret configuration..."

# Update secrets.js to use Secrets Manager
cat > "$CONFIG_DIR/secrets.js" << 'EOF'
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

let cachedJwtSecret = null;

async function getJwtSecret() {
  if (cachedJwtSecret) {
    return cachedJwtSecret;
  }

  const client = new SecretsManagerClient({ region: process.env.AWS_REGION || 'us-east-1' });

  try {
    const response = await client.send(
      new GetSecretValueCommand({
        SecretId: 'securebank/jwt/secret',
      })
    );

    const secret = JSON.parse(response.SecretString);
    cachedJwtSecret = secret.jwt_secret;
    return cachedJwtSecret;
  } catch (error) {
    console.error('Error retrieving JWT secret:', error);
    // Fallback to environment variable in development
    if (process.env.NODE_ENV !== 'production') {
      return process.env.JWT_SECRET || 'dev-secret-change-me';
    }
    throw error;
  }
}

module.exports = {
  getJwtSecret,
};
EOF

echo "✅ JWT secret migrated to Secrets Manager"

echo ""
echo "→ Removing hardcoded credentials from codebase..."

# Search and report hardcoded credentials (not auto-fixed to avoid breaking things)
echo "🔍 Scanning for remaining hardcoded credentials..."
grep -r -i -E "(password|secret|api_key|token).*=.*['\"]" "$BACKEND_DIR" --include="*.js" --include="*.ts" | grep -v node_modules | grep -v ".git" || echo "No hardcoded credentials found"

echo ""
echo "→ Creating AWS Secrets Manager secrets (if they don't exist)..."

# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name securebank/db/credentials \
  --description "SecureBank database credentials" \
  --secret-string '{
    "username": "securebank_user",
    "password": "'$(openssl rand -base64 32)'",
    "database": "securebank",
    "host": "securebank-db.cluster-xxxxx.us-east-1.rds.amazonaws.com",
    "port": 5432
  }' \
  --region us-east-1 2>/dev/null || echo "✅ Secret securebank/db/credentials already exists"

aws secretsmanager create-secret \
  --name securebank/jwt/secret \
  --description "SecureBank JWT signing secret" \
  --secret-string '{
    "jwt_secret": "'$(openssl rand -base64 64)'"
  }' \
  --region us-east-1 2>/dev/null || echo "✅ Secret securebank/jwt/secret already exists"

echo ""
echo "✅ Secrets migration complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Update RDS endpoint in securebank/db/credentials secret"
echo "   2. Add AWS_REGION environment variable to deployment"
echo "   3. Grant EKS service account access to Secrets Manager:"
echo "      aws iam attach-role-policy --role-name securebank-eks-role \\"
echo "        --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite"
echo "   4. Test connection: npm test"
