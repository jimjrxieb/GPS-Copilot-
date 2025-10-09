# PCI-DSS Compliance Violations

**Date:** 2025-10-08 21:30:51
**Total PCI-DSS Violations:** 22

## Violations by Requirement

### 3.4 - Render PAN unreadable (encryption)
**Count:** 7

- **Bucket does not have encryption enabled** (HIGH)
  - Location: `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:72`
- **Bucket does not have encryption enabled** (HIGH)
  - Location: `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:11`
- **Bucket does not encrypt data with a customer managed key.** (HIGH)
  - Location: `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:72`
- **Bucket does not encrypt data with a customer managed key.** (HIGH)
  - Location: `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project/infrastructure/terraform/s3.tf:11`
- **Ensure that CloudWatch Log Group is encrypted by KMS** (MEDIUM)
  - Location: `/cloudwatch.tf:8`
- **Ensure that S3 buckets are encrypted with KMS by default** (MEDIUM)
  - Location: `/s3.tf:11`
- **Ensure that S3 buckets are encrypted with KMS by default** (MEDIUM)
  - Location: `/s3.tf:72`

### 8.2.1 - Strong authentication
**Count:** 15

- **Ensure IAM policies does not allow credentials exposure** (MEDIUM)
  - Location: `/iam.tf:95`
- **Ensure that Secrets Manager secret is encrypted using KMS CMK** (MEDIUM)
  - Location: `/secrets-manager.tf:9`
- **Ensure that Secrets Manager secret is encrypted using KMS CMK** (MEDIUM)
  - Location: `/secrets-manager.tf:39`
- **Ensure Secrets Manager secrets should have automatic rotation enabled** (MEDIUM)
  - Location: `/secrets-manager.tf:9`
- **Ensure Secrets Manager secrets should have automatic rotation enabled** (MEDIUM)
  - Location: `/secrets-manager.tf:39`
- **Hardcoded secret: Generic API Key** (HIGH)
  - Location: `backend/README.md:112`
- **Hardcoded secret: Generic API Key** (HIGH)
  - Location: `backend/README.md:329`
- **Hardcoded secret: Generic API Key** (HIGH)
  - Location: `backend/README.md:356`
- **Hardcoded secret: Generic API Key** (HIGH)
  - Location: `backend/README.md:642`
- **Hardcoded secret: Generic API Key** (HIGH)
  - Location: `backend/.env.example:34`
- **Hardcoded secret: Generic API Key** (HIGH)
  - Location: `docker-compose.yml:47`
- **Hardcoded secret: AWS** (HIGH)
  - Location: `backend/services/aws.service.js:27`
- **Hardcoded secret: AWS** (HIGH)
  - Location: `docs/AWS-DEPLOYMENT-GUIDE.md:148`
- **Hardcoded secret: Stripe Access Token** (HIGH)
  - Location: `infrastructure/k8s/deployment.yaml:235`
- **Hardcoded secret: AWS** (HIGH)
  - Location: `infrastructure/k8s/deployment.yaml:115`

