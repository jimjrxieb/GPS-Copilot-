# Security Scanning Binaries

These binaries are too large for git (>100MB). They're downloaded automatically by Docker or you can download them manually.

## Auto-download

### Docker (recommended)
Binaries are downloaded automatically during Docker build:
```bash
docker-compose build
```

### Manual Download
```bash
cd GP-TOOLS
./download-binaries.sh
```

## Binaries

### Gitleaks (6.8MB)
- **Version:** 8.18.0
- **Purpose:** Secret scanning
- **URL:** https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz

### TFSec (38MB)
- **Version:** 1.28.1
- **Purpose:** Terraform security scanning
- **URL:** https://github.com/aquasecurity/tfsec/releases/download/v1.28.1/tfsec-linux-amd64

### Kubescape (164MB)
- **Version:** Latest
- **Purpose:** Kubernetes security scanning
- **URL:** https://github.com/kubescape/kubescape/releases/latest/download/kubescape-ubuntu-latest

## Why Not in Git?

GitHub has a 100MB file size limit. Kubescape alone is 164MB. These tools are:
- ✅ Downloaded automatically in Docker
- ✅ Can be downloaded with provided script
- ✅ Verified in Dockerfile build process

## Verification

After download, verify binaries:
```bash
ls -lh GP-TOOLS/binaries/
./GP-TOOLS/binaries/gitleaks version
./GP-TOOLS/binaries/tfsec --version
./GP-TOOLS/binaries/kubescape version
```