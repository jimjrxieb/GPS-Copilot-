# Security Audit Report

**Date:** 2025-10-08 21:30:51
**Total Findings:** 83

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 2 |
| HIGH | 26 |
| MEDIUM | 53 |
| LOW | 0 |

## Findings by Category

| Category | Count |
|----------|-------|
| INFRASTRUCTURE | 71 |
| SECRETS | 10 |
| CODE | 2 |

## Top 10 Critical Findings

### 1. Security group rule allows egress to multiple public internet addresses.
- **Severity:** CRITICAL
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/security-groups.tf:27`
- **Scanner:** tfsec

### 2. Security group rule allows ingress from public internet.
- **Severity:** CRITICAL
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/security-groups.tf:19`
- **Scanner:** tfsec

### 3. Subnet associates public IP address.
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/vpc.tf:34`
- **Scanner:** tfsec

### 4. Subnet associates public IP address.
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/vpc.tf:23`
- **Scanner:** tfsec

### 5. IAM policy document uses wildcarded action '*'
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/iam.tf:100`
- **Scanner:** tfsec

### 6. IAM policy document uses sensitive action '*' on wildcarded resource '*'
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/iam.tf:100`
- **Scanner:** tfsec

### 7. Public access block does not block public ACLs
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:87`
- **Scanner:** tfsec

### 8. Public access block does not block public ACLs
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:32`
- **Scanner:** tfsec

### 9. Public access block does not block public policies
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:88`
- **Scanner:** tfsec

### 10. Public access block does not block public policies
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:33`
- **Scanner:** tfsec

