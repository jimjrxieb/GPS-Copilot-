# Security Audit Report

**Date:** 2025-10-08 23:15:20
**Total Findings:** 150

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 4 |
| HIGH | 95 |
| MEDIUM | 51 |
| LOW | 0 |

## Findings by Category

| Category | Count |
|----------|-------|
| INFRASTRUCTURE | 61 |
| SECRETS | 89 |

## Top 10 Critical Findings

### 1. Security group rule allows egress to multiple public internet addresses.
- **Severity:** CRITICAL
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/security-groups.tf:87`
- **Scanner:** tfsec

### 2. Security group rule allows egress to multiple public internet addresses.
- **Severity:** CRITICAL
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/security-groups.tf:208`
- **Scanner:** tfsec

### 3. Security group rule allows ingress from public internet.
- **Severity:** CRITICAL
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/security-groups.tf:29`
- **Scanner:** tfsec

### 4. Security group rule allows ingress from public internet.
- **Severity:** CRITICAL
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/security-groups.tf:20`
- **Scanner:** tfsec

### 5. Subnet associates public IP address.
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/vpc.tf:34`
- **Scanner:** tfsec

### 6. Subnet associates public IP address.
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/vpc.tf:23`
- **Scanner:** tfsec

### 7. IAM policy document uses sensitive action 'kms:Decrypt' on wildcarded resource 'arn:aws:kms:*:*:key/*'
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/iam.tf:185`
- **Scanner:** tfsec

### 8. IAM policy document uses sensitive action 'logs:CreateLogGroup' on wildcarded resource 'arn:aws:logs:*:*:log-group:/aws/securebank/*'
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/iam.tf:161`
- **Scanner:** tfsec

### 9. IAM policy document uses sensitive action 'secretsmanager:GetSecretValue' on wildcarded resource 'arn:aws:secretsmanager:*:*:secret:securebank/*'
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/iam.tf:138`
- **Scanner:** tfsec
- **PCI-DSS:** 8.2.1 - Strong authentication

### 10. IAM policy document uses sensitive action 's3:ListBucket' on wildcarded resource 'arn:aws:s3:::securebank-payment-receipts-*'
- **Severity:** HIGH
- **Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/iam.tf:102`
- **Scanner:** tfsec

