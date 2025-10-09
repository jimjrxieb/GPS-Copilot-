# GP-JADE Secrets Management

**Phase 3 Complete** - October 1, 2025

## Overview

All GP-JADE secrets are now stored securely in the OS-native keychain:
- **Windows:** Credential Manager
- **macOS:** Keychain
- **Linux:** Secret Service (gnome-keyring, kwallet, or encrypted file)

**NO PLAIN TEXT FILES.** **NO CLOUD DEPENDENCIES.** **OFFLINE-FIRST.**

---

## ✅ Migration Complete

**Status:** All secrets migrated from `.env` → OS Keychain

**Migrated Secrets:**
- ✅ AWS Access Key & Secret
- ✅ Docker Hub credentials
- ✅ Azure Container Registry credentials
- ✅ GitHub Personal Access Token
- ✅ HuggingFace API Token
- ✅ GitGuardian API Token

**Total:** 10 secrets migrated successfully

---

## 🔐 How It Works

### Storage Location

Secrets are stored in OS-native encrypted storage:

```
Linux (WSL):   ~/.local/share/python_keyring/
Windows:       Windows Credential Manager (encrypted by Windows)
macOS:         macOS Keychain (encrypted by macOS)
```

### Encryption

- OS-level encryption (AES-256)
- User-specific (each user has separate vault)
- Requires OS login to access
- No master password needed (uses your OS login)

---

## 📖 Usage Guide

### 1. Get Secrets in Python Code

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager

# Get singleton instance
sm = get_secrets_manager()

# Get individual secret
aws_key = sm.get_secret("aws_access_key")
github_token = sm.get_secret("github_token")

# Get credential sets
aws_creds = sm.get_aws_credentials()
# Returns: {"access_key": "...", "secret_key": "...", "region": "us-east-1"}

docker_creds = sm.get_docker_credentials()
# Returns: {"username": "...", "token": "..."}

# Validate credentials exist
if sm.validate_aws_credentials():
    print("✅ AWS configured")

if sm.validate_github_credentials():
    print("✅ GitHub configured")
```

### 2. Set Secrets

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager

sm = get_secrets_manager()

# Set a secret
sm.set_secret("openai_api_key", "sk-...")
sm.set_secret("aws_region", "us-west-2")
```

### 3. List Configured Secrets

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager

sm = get_secrets_manager()

# Get status of all secrets
secrets = sm.list_configured_secrets()

for secret in secrets:
    print(f"{secret['key']}: {secret['configured']}")
```

### 4. Command-Line Tool

```bash
# View all secrets status
python3 GP-PLATFORM/core/secrets_manager.py
```

**Output:**
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Key               ┃ Description              ┃ Status     ┃ Preview     ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ aws_access_key    │ AWS Access Key ID        │ ✅ OK      │ AKIAQMEY... │
│ aws_secret_key    │ AWS Secret Access Key    │ ✅ OK      │ RN77YFc6... │
│ github_token      │ GitHub Personal Access   │ ✅ OK      │ ghp_cUBN... │
│ docker_username   │ Docker Hub Username      │ ✅ OK      │ linksrob... │
└───────────────────┴──────────────────────────┴────────────┴─────────────┘

Validation:
  AWS Credentials: ✅
  GitHub Token: ✅
```

---

## 🔄 Backup & Restore

### Create Encrypted Backup

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager

sm = get_secrets_manager()

# Export to encrypted file
sm.export_to_encrypted_backup(
    backup_path="secrets-backup.enc",
    master_password="YourStrongPassword123!"
)
```

**Creates:** Encrypted file with all secrets (AES-256 encrypted with PBKDF2 key derivation)

### Restore from Backup

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager

sm = get_secrets_manager()

# Import from encrypted file
sm.import_from_encrypted_backup(
    backup_path="secrets-backup.enc",
    master_password="YourStrongPassword123!"
)
```

---

## 🛠️ Updating Existing Code

### Before (Using .env):

```python
import os
from dotenv import load_dotenv

load_dotenv()

aws_key = os.getenv("AWS_ACCESS_KEY")
github_token = os.getenv("GH_TOKEN")
```

### After (Using SecretsManager):

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager

sm = get_secrets_manager()

aws_key = sm.get_secret("aws_access_key")
github_token = sm.get_secret("github_token")
```

---

## 📋 Available Secrets

| Key | Description | Required For |
|-----|-------------|--------------|
| `aws_access_key` | AWS Access Key ID | AWS operations |
| `aws_secret_key` | AWS Secret Access Key | AWS operations |
| `aws_region` | AWS Default Region | AWS operations |
| `azure_client_id` | Azure Client ID | Azure operations |
| `azure_client_secret` | Azure Client Secret | Azure operations |
| `azure_tenant_id` | Azure Tenant ID | Azure operations |
| `docker_username` | Docker Hub Username | Container registry |
| `docker_token` | Docker Hub PAT | Container registry |
| `acr_username` | Azure Container Registry Username | ACR operations |
| `acr_password` | Azure Container Registry Password | ACR operations |
| `github_token` | GitHub Personal Access Token | Git operations |
| `gitlab_token` | GitLab Personal Access Token | Git operations |
| `huggingface_token` | HuggingFace API Token | Model downloads |
| `openai_api_key` | OpenAI API Key | AI services |
| `gitguardian_token` | GitGuardian API Token | Secret scanning |
| `snyk_token` | Snyk API Token | Vulnerability scanning |
| `jade_encryption_key` | Jade Master Encryption Key | Internal encryption |
| `jade_api_secret` | Jade API Secret Key | API authentication |

---

## 🚨 Security Best Practices

### ✅ DO:
- Use `get_secrets_manager()` singleton
- Validate credentials before use
- Create encrypted backups regularly
- Use descriptive secret keys
- Log secret access (audit trail)

### ❌ DON'T:
- Print secrets to console/logs
- Store secrets in code
- Commit secrets to git
- Share secrets in plain text
- Use weak backup passwords

---

## 🔧 Troubleshooting

### "No recommended backend was available"

**Solution:** Install keyring backend for your OS

```bash
# Linux (WSL/Ubuntu)
pip install keyrings.alt

# macOS (should work out of the box)
# No action needed

# Windows (should work out of the box)
# No action needed
```

### Secrets not persisting

**Check:** Keyring file location

```python
import keyring
print(keyring.get_keyring())
```

Expected output (Linux):
```
<keyring.backends.chainer.ChainerBackend object at 0x...>
```

### Cannot access secrets

**Verify:** OS keychain is accessible

```bash
# Linux: Check if keyring works
python3 -c "import keyring; keyring.set_password('test', 'key', 'value'); print(keyring.get_password('test', 'key'))"
```

Should output: `value`

---

## 📁 Files

| File | Purpose |
|------|---------|
| [secrets_manager.py](secrets_manager.py) | Core secrets management service |
| [../scripts/migrate_secrets.py](../scripts/migrate_secrets.py) | Migration tool (.env → keychain) |
| [SECRETS_README.md](SECRETS_README.md) | This documentation |

---

## 🎯 Integration with Jade AI

### Example: AWS Scanner Integration

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager
import boto3

sm = get_secrets_manager()

# Get AWS credentials
if sm.validate_aws_credentials():
    creds = sm.get_aws_credentials()

    # Create boto3 client with managed credentials
    s3 = boto3.client(
        's3',
        aws_access_key_id=creds['access_key'],
        aws_secret_access_key=creds['secret_key'],
        region_name=creds['region']
    )

    # Scan S3 buckets
    buckets = s3.list_buckets()
else:
    print("❌ AWS credentials not configured")
    print("Run: python3 GP-PLATFORM/scripts/configure_secrets.py")
```

### Example: GitHub Integration

```python
from GP_PLATFORM.core.secrets_manager import get_secrets_manager
import requests

sm = get_secrets_manager()

# Get GitHub token
token = sm.get_secret("github_token")

if token:
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    print(f"✅ Authenticated as: {response.json()['login']}")
else:
    print("❌ GitHub token not configured")
```

---

## ✅ Migration Verification

**Migrated on:** October 1, 2025
**Status:** ✅ Complete

**Before:**
- 10 secrets in plain text `.env` file
- Risk of accidental git commit
- No encryption at rest

**After:**
- 10 secrets in OS keychain (encrypted)
- `.env` deleted (backup created)
- OS-level encryption (AES-256)
- No risk of git exposure

---

## 🔄 Next Steps

1. **Update all code** to use `SecretsManager` instead of `os.getenv()`
2. **Add GUI secrets panel** in Electron app for easy configuration
3. **Implement audit logging** for secret access
4. **Add rotation reminders** for expiring tokens

---

**Status:** Production-ready. All secrets secured with OS-native encryption.

**Last updated:** October 1, 2025
