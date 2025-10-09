# Checkov Infrastructure as Code Security

## Overview
Checkov is a static code analysis tool for Infrastructure as Code (IaC). It scans Terraform, CloudFormation, Kubernetes, Helm, ARM Templates, and Serverless framework.

## Key Security Checks by Framework

### Terraform AWS Checks

#### CKV_AWS_20: S3 Bucket Public Access
- **Risk**: High
- **Description**: S3 Bucket has an ACL defined which allows public access
- **Fix**: Remove public-read or public-read-write ACLs
```hcl
# Bad
resource "aws_s3_bucket_acl" "example" {
  bucket = aws_s3_bucket.example.id
  acl    = "public-read"
}

# Good
resource "aws_s3_bucket_acl" "example" {
  bucket = aws_s3_bucket.example.id
  acl    = "private"
}
```

#### CKV_AWS_21: S3 Bucket Versioning
- **Risk**: Medium
- **Description**: Ensure S3 bucket has versioning enabled
- **Fix**: Enable versioning for data protection
```hcl
resource "aws_s3_bucket_versioning" "example" {
  bucket = aws_s3_bucket.example.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

#### CKV_AWS_144: S3 Bucket Cross-Region Replication
- **Risk**: Low
- **Description**: Ensure S3 bucket has cross-region replication enabled
- **Fix**: Configure replication for disaster recovery

### Kubernetes Security Checks

#### CKV_K8S_8: Liveness Probe
- **Risk**: Medium
- **Description**: Containers should have liveness probe
- **Fix**: Add liveness probe for health monitoring
```yaml
# Good
spec:
  containers:
  - name: app
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
```

#### CKV_K8S_9: Readiness Probe
- **Risk**: Medium
- **Description**: Containers should have readiness probe
- **Fix**: Add readiness probe for traffic routing

#### CKV_K8S_10: CPU Limits
- **Risk**: Medium
- **Description**: Containers should have CPU limits
- **Fix**: Set resource limits to prevent resource exhaustion
```yaml
spec:
  containers:
  - name: app
    resources:
      limits:
        cpu: "500m"
        memory: "512Mi"
```

#### CKV_K8S_11: CPU Requests
- **Risk**: Low
- **Description**: Containers should have CPU requests
- **Fix**: Set resource requests for proper scheduling

#### CKV_K8S_12: Memory Limits
- **Risk**: Medium
- **Description**: Containers should have memory limits
- **Fix**: Prevent memory exhaustion attacks

#### CKV_K8S_14: Image Tag Latest
- **Risk**: Medium
- **Description**: Container should not use latest image tag
- **Fix**: Use specific version tags
```yaml
# Bad
image: nginx:latest

# Good
image: nginx:1.21.6
```

#### CKV_K8S_15: Image Pull Policy
- **Risk**: Low
- **Description**: Image should use imagePullPolicy Always
- **Fix**: Ensure latest security patches
```yaml
spec:
  containers:
  - name: app
    imagePullPolicy: Always
```

#### CKV_K8S_16: Privileged Containers
- **Risk**: Critical
- **Description**: Container should not run as privileged
- **Fix**: Remove privileged flag
```yaml
# Bad
securityContext:
  privileged: true

# Good
securityContext:
  privileged: false
```

#### CKV_K8S_17: Privileged Escalation
- **Risk**: High
- **Description**: Containers should not allow privilege escalation
- **Fix**: Disable privilege escalation
```yaml
securityContext:
  allowPrivilegeEscalation: false
```

#### CKV_K8S_22: Read-only Root Filesystem
- **Risk**: Medium
- **Description**: Use read-only root filesystem
- **Fix**: Mount root filesystem as read-only
```yaml
securityContext:
  readOnlyRootFilesystem: true
```

#### CKV_K8S_23: Run as Non-root
- **Risk**: High
- **Description**: Minimize container privileges
- **Fix**: Run as non-root user
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

### Docker Security Checks

#### CKV_DOCKER_2: HEALTHCHECK Instruction
- **Risk**: Medium
- **Description**: Dockerfile should include HEALTHCHECK instruction
- **Fix**: Add health check for container monitoring
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

#### CKV_DOCKER_3: User Instruction
- **Risk**: High
- **Description**: Dockerfile should specify USER
- **Fix**: Run as non-root user
```dockerfile
RUN groupadd -r myuser && useradd -r -g myuser myuser
USER myuser
```

## Remediation Strategies by Risk Level

### Critical Issues (Immediate Action)
- Privileged containers (CKV_K8S_16)
- Public S3 buckets (CKV_AWS_20)
- Root filesystem access (CKV_DOCKER_3)

### High Priority (Within 24 hours)
- Privilege escalation (CKV_K8S_17)
- Missing security contexts (CKV_K8S_23)
- Insecure network policies

### Medium Priority (Within 1 week)
- Missing probes (CKV_K8S_8, CKV_K8S_9)
- Resource limits (CKV_K8S_10, CKV_K8S_12)
- Versioning controls (CKV_AWS_21)

### Low Priority (Next sprint)
- Resource requests (CKV_K8S_11)
- Image pull policies (CKV_K8S_15)
- Health checks (CKV_DOCKER_2)

## Integration with GP-Copilot

When Checkov findings are detected, Jade should:
1. Categorize by infrastructure type (K8s, Terraform, Docker)
2. Prioritize by risk level (Critical → Low)
3. Apply automated fixes for standard patterns
4. Generate compliance reports mapping to frameworks
5. Escalate architectural changes to senior engineers

## Compliance Framework Mapping

### CIS Benchmarks
- CIS Kubernetes Benchmark: K8S security checks
- CIS Docker Benchmark: Container security
- CIS Cloud Provider Benchmarks: AWS/Azure/GCP

### NIST Cybersecurity Framework
- **Protect (PR)**: Access controls, data security
- **Detect (DE)**: Monitoring and logging
- **Respond (RS)**: Incident response capabilities

### SOC2 Type II
- **CC6.1**: Logical access controls
- **CC7.1**: System monitoring
- **CC7.2**: Change management