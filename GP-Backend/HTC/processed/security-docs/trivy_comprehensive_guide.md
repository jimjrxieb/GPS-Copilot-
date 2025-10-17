# Trivy Comprehensive Security Scanner Guide

## Overview
Trivy is a comprehensive security scanner for containers, Infrastructure as Code (IaC), and filesystems. It detects vulnerabilities in OS packages, application dependencies, container images, Kubernetes clusters, and misconfigurations in IaC files.

## Core Capabilities

### Vulnerability Scanning
- **OS Packages**: Detects vulnerabilities in Alpine, RHEL, CentOS, Oracle Linux, Debian, Ubuntu, Amazon Linux, openSUSE, SLES, Photon OS
- **Application Dependencies**: Supports 20+ languages including Go, Java, Python, Ruby, Node.js, .NET, PHP, Rust
- **Container Images**: Multi-layer analysis for Docker images and OCI artifacts
- **Filesystem Scanning**: Direct filesystem vulnerability detection

### Misconfiguration Detection
- **Kubernetes**: YAML manifest analysis against security best practices
- **Docker**: Dockerfile security analysis
- **Terraform**: HCL file security scanning
- **CloudFormation**: AWS infrastructure security checks
- **Ansible**: Playbook security analysis

### Secret Detection
- **Hardcoded Secrets**: API keys, passwords, tokens in code
- **Configuration Files**: Database credentials, cloud access keys
- **Git History**: Historical secret exposure detection

## Command Line Usage

### Basic Container Scanning
```bash
# Scan Docker image
trivy image nginx:latest

# Scan with specific severity
trivy image --severity HIGH,CRITICAL nginx:latest

# Output formats
trivy image --format json nginx:latest
trivy image --format table nginx:latest
trivy image --format sarif nginx:latest

# Save results to file
trivy image --output results.json --format json nginx:latest
```

### Filesystem Scanning
```bash
# Scan local directory
trivy fs .

# Scan specific directory
trivy fs /path/to/project

# Skip specific vulnerabilities
trivy fs --skip-update --ignore-unfixed .

# Custom policy
trivy fs --policy ./policies .
```

### Infrastructure as Code Scanning
```bash
# Scan Terraform files
trivy config terraform/

# Scan Kubernetes manifests
trivy config k8s/

# Scan Docker files
trivy config --file-patterns dockerfile:Dockerfile* .

# Output with trace
trivy config --trace terraform/
```

### Repository Scanning
```bash
# Scan Git repository
trivy repo https://github.com/owner/repo

# Scan specific branch
trivy repo --branch main https://github.com/owner/repo

# Include secret scanning
trivy repo --security-checks vuln,secret https://github.com/owner/repo
```

## Vulnerability Severity Levels

### Critical (CVSS 9.0-10.0)
- **Characteristics**: Remote code execution, privilege escalation, data breach potential
- **Examples**: CVE-2021-44228 (Log4Shell), CVE-2022-22965 (Spring4Shell)
- **Action**: Immediate patching required, consider service shutdown

### High (CVSS 7.0-8.9)
- **Characteristics**: Significant security impact, potential for exploitation
- **Examples**: SQL injection, authentication bypass, XSS
- **Action**: Patch within 24-48 hours, implement workarounds

### Medium (CVSS 4.0-6.9)
- **Characteristics**: Moderate security impact, limited exploitation scenarios
- **Examples**: Information disclosure, DoS vulnerabilities
- **Action**: Patch within 1-2 weeks, assess risk context

### Low (CVSS 0.1-3.9)
- **Characteristics**: Minimal security impact, difficult to exploit
- **Examples**: Minor information leaks, edge case vulnerabilities
- **Action**: Patch in regular maintenance cycle

### Unknown
- **Characteristics**: No CVSS score assigned or calculated
- **Action**: Investigate manually, assess based on context

## Configuration Options

### Trivy Configuration File (.trivyignore)
```bash
# Ignore specific CVEs
CVE-2019-8331
CVE-2020-9283

# Ignore by package
pip
npm

# Ignore by path
tests/
*.test.js

# Expiration-based ignores
CVE-2021-1234 # expires:2024-12-31
```

### Custom Policies
```rego
# trivy-policy.rego
package trivy

import data.lib.trivy

default ignore = false

ignore {
    input.PkgName == "openssl"
    input.InstalledVersion == "1.1.1k"
    input.VulnerabilityID == "CVE-2021-3712"
}
```

### Environment Variables
```bash
# Cache directory
export TRIVY_CACHE_DIR=/path/to/cache

# Database repository
export TRIVY_DB_REPOSITORY=ghcr.io/aquasecurity/trivy-db

# Timeout settings
export TRIVY_TIMEOUT=10m

# Debug mode
export TRIVY_DEBUG=true
```

## Integration Patterns

### CI/CD Integration
```yaml
# GitHub Actions
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myregistry/myimage:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'

# GitLab CI
trivy_scan:
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Kubernetes Integration
```yaml
# Trivy Operator
apiVersion: v1
kind: ConfigMap
metadata:
  name: trivy-operator
data:
  scanJob.tolerations: |
    - key: node-role.kubernetes.io/master
      operator: Exists
      effect: NoSchedule
```

### Docker Integration
```dockerfile
# Multi-stage build with Trivy
FROM alpine:latest as trivy-scanner
RUN apk add --no-cache curl
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

FROM node:16-alpine as builder
COPY package*.json ./
RUN npm ci --only=production

# Scan stage
FROM trivy-scanner as security-scan
COPY --from=builder /app /scan-target
RUN trivy fs --severity HIGH,CRITICAL /scan-target

FROM node:16-alpine
COPY --from=builder /app /app
```

## Trivy Database and Updates

### Database Management
```bash
# Update vulnerability database
trivy image --download-db-only

# Skip database update
trivy image --skip-update nginx

# Use specific database version
trivy image --cache-dir /custom/cache nginx

# Clear cache
trivy clean --all
```

### Offline Mode
```bash
# Download database for offline use
trivy image --download-db-only --cache-dir ./db-cache

# Use offline database
trivy image --skip-update --cache-dir ./db-cache nginx
```

## Common Remediation Patterns

### Container Security
```dockerfile
# Use specific versions
FROM node:16.18.0-alpine3.16

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

# Use minimal base images
FROM gcr.io/distroless/nodejs:16

# Multi-stage builds
FROM node:16-alpine as dependencies
# Build stage...
FROM gcr.io/distroless/nodejs:16 as runtime
COPY --from=dependencies /app /app
```

### Dependency Management
```json
// package.json - Pin versions
{
  "dependencies": {
    "express": "4.18.2",
    "lodash": "4.17.21"
  }
}
```

```requirements.txt
# Python - Pin versions
Django==4.1.4
requests==2.28.1
```

### Infrastructure Security
```hcl
# Terraform - Secure S3 bucket
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## GP-Copilot Integration

### When Trivy findings are detected, Jade should:

1. **Vulnerability Prioritization**:
   - Critical/High: Immediate escalation with patch recommendations
   - Medium: Scheduled remediation with workaround suggestions
   - Low: Maintenance cycle inclusion

2. **Contextual Analysis**:
   - Map CVEs to specific packages and versions
   - Identify exploitability based on application context
   - Recommend specific version upgrades

3. **Automated Remediation**:
   - Generate Dockerfile updates for vulnerable base images
   - Suggest dependency version bumps in package files
   - Create pull requests for low-risk fixes

4. **Compliance Mapping**:
   - Map vulnerabilities to compliance frameworks (CIS, NIST, SOC2)
   - Generate compliance reports with remediation status
   - Track remediation metrics over time

5. **Integration Recommendations**:
   - Configure CI/CD pipeline integration
   - Set up automated scanning schedules
   - Implement policy-based gates

### Escalation Criteria:
- **Critical vulnerabilities**: Immediate escalation with patch timeline
- **High vulnerabilities in production**: 24-hour remediation SLA
- **Medium vulnerabilities**: Weekly review and planning
- **Infrastructure misconfigurations**: Based on blast radius assessment
- **Secret exposure**: Immediate credential rotation required

### Common Trivy Exit Codes:
- **0**: No vulnerabilities found
- **1**: Vulnerabilities found
- **2**: Misconfiguration detected
- **3**: Error occurred during scanning

This knowledge enables Jade to provide intelligent analysis of Trivy scan results, moving beyond simple vulnerability reporting to actionable security guidance.