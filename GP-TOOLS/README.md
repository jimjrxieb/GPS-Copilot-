# GP-TOOLS: Security Tool Binaries & Utilities

> **Purpose**: Centralized repository for security scanning tool binaries and helper utilities

## Overview

GP-TOOLS provides a curated collection of security tool binaries that are either:
- Not readily available via standard package managers
- Require specific versions for compatibility
- Needed for offline/air-gapped environments
- Large binaries excluded from git via .gitignore

**Total Size**: ~208MB (3 binaries)

---

## Directory Structure

```
GP-TOOLS/
├── binaries/              # Security tool executables (~208MB)
│   ├── gitleaks           # Secrets detection (6.8MB)
│   ├── kubescape          # Kubernetes security (164MB)
│   ├── tfsec              # Terraform scanner (38MB)
│   └── README.md          # Binary documentation
│
├── configs/               # Tool configuration files (empty - TBD)
├── scripts/               # Helper automation scripts (empty - TBD)
└── download-binaries.sh   # Automated download script
```

---

## Available Binaries

### 🔐 Secrets Detection

**gitleaks** (v8.18.0 | 6.8MB)
- **Purpose**: Detect hardcoded secrets, API keys, passwords in code/git history
- **Binary**: `binaries/gitleaks`
- **Symlink**: `bin/gitleaks` → `../GP-TOOLS/binaries/gitleaks`
- **Platform**: Linux x86_64
- **Source**: https://github.com/gitleaks/gitleaks
- **Usage**:
  ```bash
  gitleaks detect --source /path/to/repo
  gitleaks protect --staged  # Pre-commit hook
  ```
- **Detects**: AWS keys, GitHub tokens, private keys, JWTs, database credentials
- **Config**: Custom rules in `GP-CONSULTING/config/gitleaks.toml`

### ☸️ Kubernetes Security

**kubescape** (v3.0.3 | 164MB)
- **Purpose**: Kubernetes security posture management (KSPM)
- **Binary**: `binaries/kubescape`
- **Symlink**: `bin/kubescape` → `../GP-TOOLS/binaries/kubescape`
- **Platform**: Linux x86_64
- **Source**: https://github.com/kubescape/kubescape
- **Usage**:
  ```bash
  kubescape scan framework nsa /path/to/manifests
  kubescape scan framework mitre
  kubescape scan control C-0001  # Specific control
  ```
- **Frameworks**: NSA/CISA, MITRE ATT&CK, CIS Benchmarks
- **Note**: Update available (v3.0.15)

### 🏗️ Infrastructure-as-Code

**tfsec** (v1.28.1 | 38MB)
- **Purpose**: Static analysis for Terraform code security
- **Binary**: `binaries/tfsec`
- **Symlink**: `bin/tfsec` → `../GP-TOOLS/binaries/tfsec`
- **Platform**: Linux x86_64
- **Source**: https://github.com/aquasecurity/tfsec
- **Usage**:
  ```bash
  tfsec /path/to/terraform
  tfsec --format json > results.json
  tfsec --minimum-severity HIGH
  ```
- **Cloud Support**: AWS, Azure, GCP, Cloudflare, DigitalOcean
- **Checks**: 1000+ built-in security rules

---

## Why These Binaries?

### Benefits of Local Binaries

✅ **Version Control**: Pin exact versions for reproducibility
✅ **Offline Capability**: No internet required during scans
✅ **Speed**: Instant availability, no download time
✅ **Consistency**: Same version across dev/CI/prod
✅ **Air-Gap Support**: Works in isolated environments
✅ **No Dependencies**: Self-contained executables

### Why Not Package Managers?

| Package Manager | Issue |
|-----------------|-------|
| **apt/yum** | Often outdated versions |
| **snap** | Not available in all environments |
| **homebrew** | macOS-centric |
| **pip/npm** | Version conflicts with other tools |
| **docker** | Overhead of container runtime |

---

## Installation & Setup

### Download All Binaries

```bash
# Automated download (recommended)
cd /home/jimmie/linkops-industries/GP-copilot/GP-TOOLS
./download-binaries.sh

# Manual download (if script fails)
# Download from GitHub releases:
# - gitleaks: https://github.com/gitleaks/gitleaks/releases
# - kubescape: https://github.com/kubescape/kubescape/releases
# - tfsec: https://github.com/aquasecurity/tfsec/releases
```

### Verify Installations

```bash
# Check binaries exist
ls -lh binaries/

# Test each tool
gitleaks version      # via symlink in bin/
kubescape version
tfsec --version
```

### Create Symlinks (if needed)

```bash
# Symlinks should already exist in bin/
# If broken, recreate:
cd /home/jimmie/linkops-industries/GP-copilot
ln -sf GP-TOOLS/binaries/gitleaks bin/gitleaks
ln -sf GP-TOOLS/binaries/kubescape bin/kubescape
ln -sf GP-TOOLS/binaries/tfsec bin/tfsec
```

---

## Integration with Platform

### Workflow Integration

```
User Command
     ↓
jade scan <project>
     ↓
GP-CONSULTING/scanners/
  ├── gitleaks_scanner.py  ──→ Calls → bin/gitleaks (→ GP-TOOLS/binaries/gitleaks)
  ├── tfsec_scanner.py     ──→ Calls → bin/tfsec
  └── kubernetes_scanner.py ──→ Calls → bin/kubescape
     ↓
Results → GP-DATA/active/results/<project>/
     ↓
GP-AI/core/ai_security_engine.py
     ↓
AI-Enhanced Analysis
```

### Scanner Wrappers

Each binary has a Python wrapper in `GP-CONSULTING/scanners/`:

- **gitleaks_scanner.py** - Wraps gitleaks with result normalization
- **tfsec_scanner.py** - Wraps tfsec with JSON parsing
- **kubernetes_scanner.py** - Wraps kubescape + other K8s tools

### Fixer Integration

Fixers in `GP-CONSULTING/fixers/` use scan results:

- **gitleaks_fixer.py** - Auto-remediate secrets
- **tfsec_fixer.py** - Generate Terraform fixes

---

## Usage Examples

### Gitleaks - Secrets Detection

```bash
# Scan current repository
gitleaks detect --source .

# Scan specific directory
gitleaks detect --source /path/to/code

# Custom config
gitleaks detect --config GP-CONSULTING/config/gitleaks.toml

# JSON output for parsing
gitleaks detect --source . --report-path results.json --report-format json

# Pre-commit hook
gitleaks protect --staged
```

### Kubescape - Kubernetes Security

```bash
# Scan against NSA/CISA framework
kubescape scan framework nsa manifests/

# MITRE ATT&CK for Kubernetes
kubescape scan framework mitre

# Specific control check
kubescape scan control C-0001

# Scan live cluster (requires kubectl)
kubescape scan --enable-host-scan

# JSON output
kubescape scan framework nsa manifests/ --format json > results.json
```

### Tfsec - Terraform Security

```bash
# Scan Terraform directory
tfsec /path/to/terraform

# Minimum severity filter
tfsec . --minimum-severity HIGH

# Specific checks only
tfsec . --include-passed

# Exclude specific checks
tfsec . --exclude aws-s3-enable-versioning

# JSON output
tfsec . --format json > results.json

# With detailed explanations
tfsec . --verbose
```

---

## Configuration Files (Future)

### Planned configs/ Directory

```
configs/
├── gitleaks.toml          # Custom secret patterns
├── tfsec.yml              # Terraform rule overrides
├── kubescape-config.json  # K8s policy exceptions
└── README.md              # Configuration guide
```

Currently, configurations are in `GP-CONSULTING/config/`.

---

## Helper Scripts (Future)

### Planned scripts/ Directory

```
scripts/
├── update-all-binaries.sh      # Automated updates
├── verify-checksums.sh         # Security verification
├── benchmark-scanners.sh       # Performance testing
└── generate-configs.sh         # Config template generator
```

---

## Maintenance

### Checking for Updates

```bash
# Check current versions
gitleaks version
kubescape version
tfsec --version

# Check latest releases
# - gitleaks: https://github.com/gitleaks/gitleaks/releases/latest
# - kubescape: https://github.com/kubescape/kubescape/releases/latest
# - tfsec: https://github.com/aquasecurity/tfsec/releases/latest

# Kubescape can self-update
kubescape update
```

### Updating Binaries

```bash
# Option 1: Re-run download script
./download-binaries.sh

# Option 2: Manual update
cd binaries/
wget https://github.com/gitleaks/gitleaks/releases/download/vX.Y.Z/gitleaks_X.Y.Z_linux_x64.tar.gz
tar -xzf gitleaks_X.Y.Z_linux_x64.tar.gz
chmod +x gitleaks
```

### Verifying Integrity

```bash
# Check file hashes (if available)
sha256sum binaries/gitleaks
sha256sum binaries/kubescape
sha256sum binaries/tfsec

# Compare with official checksums from GitHub releases
```

---

## Adding New Binaries

### Step-by-Step Guide

1. **Download Binary**
   ```bash
   cd GP-TOOLS/binaries/
   wget <download-url>
   tar -xzf <archive> # if compressed
   chmod +x <binary-name>
   ```

2. **Create Symlink**
   ```bash
   cd ../../bin/
   ln -s ../GP-TOOLS/binaries/<binary-name> <binary-name>
   ```

3. **Create Scanner Wrapper**
   ```bash
   # Create GP-CONSULTING/scanners/<tool>_scanner.py
   # Follow existing scanner patterns
   ```

4. **Update Documentation**
   - Add to `GP-TOOLS/binaries/README.md`
   - Add to this README
   - Update `bin/README.md`

5. **Test Integration**
   ```bash
   <binary-name> --version
   python GP-CONSULTING/scanners/<tool>_scanner.py <test-target>
   ```

---

## Size & Performance

| Binary | Size | Scan Speed (avg) | Language |
|--------|------|------------------|----------|
| **gitleaks** | 6.8MB | ~500ms per repo | Go |
| **kubescape** | 164MB | ~5-10s per cluster | Go |
| **tfsec** | 38MB | ~1-2s per TF module | Go |
| **Total** | **208MB** | N/A | All Go |

### Why Go Binaries?

- ✅ Single-file executables (no dependencies)
- ✅ Fast execution (compiled, not interpreted)
- ✅ Cross-platform support
- ✅ Low memory footprint
- ✅ Security tooling standard

---

## Troubleshooting

### Binary Not Found

```bash
# Check if binary exists
ls -lh GP-TOOLS/binaries/

# Check symlink
ls -lh bin/gitleaks

# Re-download if missing
./GP-TOOLS/download-binaries.sh
```

### Permission Denied

```bash
# Make executable
chmod +x GP-TOOLS/binaries/*
```

### Wrong Architecture

```bash
# Check system architecture
uname -m  # Should be x86_64

# If ARM/M1 Mac, download appropriate binary
# Update download-binaries.sh accordingly
```

### Kubescape Update Warning

```bash
# Warning: "current version 'v3.0.3' is not updated..."
# Update kubescape
kubescape update

# Or download manually
wget https://github.com/kubescape/kubescape/releases/download/v3.0.15/kubescape-ubuntu-latest
mv kubescape-ubuntu-latest binaries/kubescape
chmod +x binaries/kubescape
```

---

## Security Considerations

### Binary Verification

- ✅ Download from official GitHub releases only
- ✅ Verify SHA256 checksums when available
- ✅ Use HTTPS for downloads
- ⚠️ Binaries are excluded from git (see `.gitignore`)

### Scanning Security

- Binaries run with user permissions (not root)
- Scan results stored in `GP-DATA/active/results/`
- Secrets are redacted in logs
- No network calls during scans (except kubescape live cluster)

---

## Related Components

- **[bin/](../bin/)** - Symlinks to these binaries (in PATH)
- **[GP-CONSULTING/scanners/](../GP-CONSULTING/scanners/)** - Python wrapper scripts
- **[GP-CONSULTING/fixers/](../GP-CONSULTING/fixers/)** - Automated remediations
- **[GP-DATA/active/results/](../GP-DATA/active/results/)** - Scan output storage
- **[GP-AI/integrations/](../GP-AI/integrations/)** - Tool registry

---

## Version History

| Tool | Current | Latest | Status |
|------|---------|--------|--------|
| gitleaks | 8.18.0 | 8.18.0 | ✅ Up to date |
| kubescape | 3.0.3 | 3.0.15 | ⚠️ Update available |
| tfsec | 1.28.1 | 1.28.1 | ✅ Up to date |

---

## Future Enhancements

### Planned Additions

- [ ] **conftest** - OPA policy testing (currently 40MB in bin/)
- [ ] **kube-bench** - CIS Kubernetes benchmark
- [ ] **polaris** - Kubernetes best practices
- [ ] **terrascan** - IaC security scanner
- [ ] **snyk CLI** - Dependency vulnerability scanner

### Planned Features

- [ ] Automated update checker script
- [ ] Checksum verification in download script
- [ ] Multi-arch support (x86_64, ARM64)
- [ ] Version pinning configuration
- [ ] Binary integrity monitoring

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-10-07
**Total Size**: 208MB (3 binaries)
**Maintained by**: LinkOps Industries - JADE AI Security Platform Team