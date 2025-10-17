# GOOD EXAMPLE - Will PASS OPA Security Gate
# This file demonstrates Terraform security best practices

# ✅ SECURE: S3 bucket with encryption and public access block
resource "aws_s3_bucket" "data" {
  bucket = "my-company-data-secure"

  tags = {
    Name        = "Company Data Bucket"
    Environment = "Production"
    Compliance  = "PCI-DSS"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ✅ SECURE: KMS key for encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "S3 Encryption Key"
  }
}

# ✅ SECURE: RDS instance with encryption and private access
resource "aws_db_instance" "database" {
  identifier           = "myapp-db-secure"
  engine               = "postgres"
  engine_version       = "14.7"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20

  # Credentials from Secrets Manager (not hardcoded)
  username = data.aws_secretsmanager_secret_version.db_credentials.secret_string.username
  password = data.aws_secretsmanager_secret_version.db_credentials.secret_string.password

  # ✅ Encryption enabled
  storage_encrypted   = true
  kms_key_id         = aws_kms_key.rds.arn

  # ✅ Private access only
  publicly_accessible = false

  # ✅ Backup enabled
  backup_retention_period = 7
  skip_final_snapshot     = false
  final_snapshot_identifier = "myapp-db-final-snapshot"

  # ✅ SSL enforcement
  enabled_cloudwatch_logs_exports = ["postgresql"]

  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.database.name

  tags = {
    Name        = "Application Database"
    Environment = "Production"
  }
}

resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "RDS Encryption Key"
  }
}

# ✅ SECURE: Security group with least privilege
resource "aws_security_group" "web" {
  name        = "web-sg-secure"
  description = "Allow web traffic from specific CIDR"
  vpc_id      = aws_vpc.main.id

  # ✅ HTTPS only, from specific CIDR
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Internal network only
    description = "HTTPS from internal network"
  }

  # ✅ Egress restricted
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS to internet"
  }

  tags = {
    Name = "Web Security Group"
  }
}

resource "aws_security_group" "database" {
  name        = "database-sg-secure"
  description = "Database security group"
  vpc_id      = aws_vpc.main.id

  # ✅ PostgreSQL only from web tier
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
    description     = "PostgreSQL from web tier only"
  }

  tags = {
    Name = "Database Security Group"
  }
}

# ✅ SECURE: IAM policy with least privilege
resource "aws_iam_policy" "app_s3_access" {
  name        = "app-s3-access"
  description = "Allow app to access specific S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.data.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.data.arn
      }
    ]
  })
}

# Supporting resources
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "Main VPC"
  }
}

resource "aws_db_subnet_group" "database" {
  name       = "database-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "Database subnet group"
  }
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "Private Subnet A"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "Private Subnet B"
  }
}

# Secrets Manager for credentials
data "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = "myapp/database/credentials"
}
