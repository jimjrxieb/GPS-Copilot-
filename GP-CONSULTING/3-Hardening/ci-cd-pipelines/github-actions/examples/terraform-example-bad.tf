# BAD EXAMPLE - Will FAIL OPA Security Gate
# This file demonstrates common Terraform security violations

# ❌ VIOLATION: S3 bucket without encryption
resource "aws_s3_bucket" "data" {
  bucket = "my-company-data"

  # Missing: server_side_encryption_configuration
  # Missing: public access block

  tags = {
    Name = "Company Data Bucket"
  }
}

# ❌ VIOLATION: RDS instance without encryption
resource "aws_db_instance" "database" {
  identifier           = "myapp-db"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "admin"
  password             = "admin123"  # ❌ Hardcoded password

  # Missing: storage_encrypted = true
  # Missing: kms_key_id

  publicly_accessible  = true  # ❌ Publicly accessible
  skip_final_snapshot  = true  # ❌ No backup
}

# ❌ VIOLATION: Security group with 0.0.0.0/0 access
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow web traffic"
  vpc_id      = "vpc-12345"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ SSH open to world
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ MySQL open to world
  }
}

# ❌ VIOLATION: IAM policy with wildcard actions
resource "aws_iam_policy" "admin" {
  name        = "admin-policy"
  description = "Admin policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"  # ❌ Wildcard actions
        Resource = "*"  # ❌ Wildcard resources
      }
    ]
  })
}
