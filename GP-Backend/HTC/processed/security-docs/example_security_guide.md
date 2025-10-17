# Example Security Guide

This is an example security document that demonstrates how to add knowledge to the GP-RAG system.

## Container Security Best Practices

### Image Security
- Use minimal base images (Alpine, Distroless)
- Scan images for vulnerabilities with Trivy
- Never run containers as root user
- Set read-only root filesystem when possible

### Runtime Security
- Drop unnecessary capabilities
- Use security contexts to enforce constraints
- Implement network policies for micro-segmentation
- Monitor container behavior with runtime security tools

## Compliance Frameworks

### CIS Docker Benchmark
- CIS-5.2.5: Ensure privileged containers are not used
- CIS-5.2.6: Ensure containers run as non-root user
- CIS-5.2.11: Ensure read-only root filesystem

### SOC2 Controls
- CC6.1: Logical and physical access controls
- CC7.1: System monitoring and performance

This document will be automatically vectorized and made available to Jade for contextual responses.