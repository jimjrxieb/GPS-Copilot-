# Terraform Security Best Practices

## Overview
Terraform security focuses on Infrastructure as Code (IaC) security, state management, and cloud resource configuration.

## State Management Security

### Remote State Storage
```hcl
# Secure S3 backend with encryption
terraform {
  backend "s3" {
    bucket         = "terraform-state-secure"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
    dynamodb_table = "terraform-locks"
  }
}
```

### State Locking
```hcl
# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_locks" {
  name           = "terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "Terraform State Locks"
  }
}
```

## AWS Security Configurations

### S3 Bucket Security
```hcl
# Secure S3 bucket configuration
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.secure_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_key.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "access_logging" {
  bucket = aws_s3_bucket.secure_bucket.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "access-logs/"
}
```

### EC2 Security Groups
```hcl
# Restrictive security group
resource "aws_security_group" "web_tier" {
  name_prefix = "web-tier-"
  vpc_id      = aws_vpc.main.id

  # HTTPS only
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }

  # SSH from bastion only
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
    description     = "SSH from bastion host"
  }

  # Outbound HTTPS only
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  # Outbound HTTP for package updates
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP outbound for updates"
  }

  tags = {
    Name = "web-tier-sg"
  }
}
```

### IAM Security
```hcl
# Principle of least privilege IAM role
resource "aws_iam_role" "app_role" {
  name = "application-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = "us-west-2"
          }
        }
      }
    ]
  })

  max_session_duration = 3600  # 1 hour
}

# Minimal IAM policy
resource "aws_iam_policy" "app_policy" {
  name = "application-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.app_bucket.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.app_secret.arn
      }
    ]
  })
}
```

### RDS Security
```hcl
# Secure RDS instance
resource "aws_db_instance" "secure_db" {
  identifier = "secure-database"

  engine         = "postgres"
  engine_version = "14.9"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds_key.arn

  db_name  = "appdb"
  username = "dbadmin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = false
  final_snapshot_identifier = "secure-db-final-snapshot"

  enabled_cloudwatch_logs_exports = ["postgresql"]

  deletion_protection = true

  tags = {
    Name = "secure-database"
  }
}

# Secure database subnet group (private subnets)
resource "aws_db_subnet_group" "main" {
  name       = "main"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "Main DB subnet group"
  }
}
```

## Secret Management

### Using AWS Secrets Manager
```hcl
# Generate random password
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "database-password"
  description            = "Database password for application"
  recovery_window_in_days = 7
  kms_key_id             = aws_kms_key.secrets_key.arn
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}
```

### Environment Variables (Avoid Hardcoding)
```hcl
# Use environment variables for sensitive data
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Reference in provider configuration
provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key_id     # From environment
  secret_key = var.aws_secret_access_key # From environment
}
```

## Network Security

### VPC Configuration
```hcl
# Secure VPC with private subnets
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main-vpc"
  }
}

# Private subnets for databases
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "private-subnet-a"
  }
}

# NAT Gateway for outbound internet
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id

  tags = {
    Name = "main-nat-gateway"
  }

  depends_on = [aws_internet_gateway.main]
}
```

### Network ACLs
```hcl
# Restrictive network ACL
resource "aws_network_acl" "private" {
  vpc_id = aws_vpc.main.id

  # Allow inbound HTTPS from VPC
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = aws_vpc.main.cidr_block
    from_port  = 443
    to_port    = 443
  }

  # Allow outbound to VPC
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = aws_vpc.main.cidr_block
    from_port  = 0
    to_port    = 65535
  }

  tags = {
    Name = "private-nacl"
  }
}
```

## Encryption at Rest and Transit

### KMS Key Management
```hcl
# KMS key for encryption
resource "aws_kms_key" "main" {
  description             = "Main encryption key"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "main-kms-key"
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/main-key"
  target_key_id = aws_kms_key.main.key_id
}
```

### Certificate Management
```hcl
# ACM certificate for HTTPS
resource "aws_acm_certificate" "main" {
  domain_name       = "example.com"
  validation_method = "DNS"

  subject_alternative_names = [
    "*.example.com"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "main-certificate"
  }
}
```

## Monitoring and Logging

### CloudTrail
```hcl
# CloudTrail for API logging
resource "aws_cloudtrail" "main" {
  name           = "main-trail"
  s3_bucket_name = aws_s3_bucket.cloudtrail.id
  s3_key_prefix  = "cloudtrail-logs"

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.sensitive.arn}/*"]
    }
  }

  kms_key_id                = aws_kms_key.cloudtrail.arn
  enable_log_file_validation = true

  tags = {
    Name = "main-cloudtrail"
  }
}
```

### VPC Flow Logs
```hcl
# VPC Flow Logs
resource "aws_flow_log" "vpc_flow_log" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}
```

## Common Security Anti-patterns to Avoid

### Insecure Configurations
```hcl
# BAD: Overly permissive security group
resource "aws_security_group" "bad_example" {
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Never do this
  }
}

# BAD: Hardcoded secrets
resource "aws_instance" "bad_example" {
  user_data = <<-EOF
    export DB_PASSWORD="hardcoded_password"  # Never do this
  EOF
}

# BAD: Unencrypted storage
resource "aws_s3_bucket" "bad_example" {
  bucket = "insecure-bucket"
  # Missing encryption, versioning, public access block
}
```

## Terraform Security Tools Integration

### Checkov
```bash
# Scan Terraform files
checkov -f main.tf
checkov -d terraform/ --framework terraform
checkov --check CKV_AWS_20  # Specific check
```

### TFSec
```bash
# Scan for security issues
tfsec .
tfsec --format json --out results.json .
tfsec --exclude-downloaded-modules .
```

### Terraform Plan Analysis
```bash
# Review plan for security issues
terraform plan -out=tfplan
terraform show -json tfplan | jq '.planned_values'
```

## Compliance Mapping

### CIS AWS Foundations Benchmark
- **2.1.1**: CloudTrail enabled in all regions
- **2.2.1**: CloudTrail log file validation enabled
- **2.3.1**: S3 bucket access logging enabled
- **2.7**: CloudTrail logs encrypted at rest using KMS

### NIST Cybersecurity Framework
- **PR.AC**: Access controls (IAM, Security Groups)
- **PR.DS**: Data security (Encryption, Backup)
- **PR.PT**: Protective technology (WAF, Shield)
- **DE.AE**: Anomaly detection (CloudWatch, GuardDuty)

### SOC2 Type II
- **CC6.1**: Logical access controls
- **CC6.7**: Data transmission and disposal
- **CC7.1**: System monitoring

## Integration with GP-Copilot

When Terraform security issues are detected, Jade should:

1. **Identify Resource Type**: S3, EC2, RDS, IAM, etc.
2. **Assess Risk Level**: Critical (public resources) to Low (missing tags)
3. **Apply Security Templates**: Use secure baseline configurations
4. **Generate Remediation Code**: Provide corrected Terraform
5. **Map to Compliance**: Reference CIS, NIST, SOC2 controls
6. **Escalate Complex Changes**: Infrastructure modifications requiring approval

### Escalation Criteria:
- **Public resources**: Immediate escalation
- **Missing encryption**: High priority
- **Overpermissive IAM**: High priority
- **Network exposure**: Medium priority
- **Missing monitoring**: Low priority automated fix