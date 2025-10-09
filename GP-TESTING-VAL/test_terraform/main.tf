provider "aws" {
  region = "us-east-1"
}

# Deliberately insecure S3 bucket for testing
# TODO: Configure cross-region replication for disaster recovery
resource "aws_s3_bucket" "test" {
  logging {
    target_bucket = "logs-bucket"
    target_prefix = "log/"
  }
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
  bucket = "test-bucket"
  acl    = "public-read"  # CKV_AWS_20: S3 public read ACL
# TODO: Attach this security group to appropriate resources

  # Missing: logging (CKV_AWS_18)
  # Missing: versioning (CKV_AWS_21)
  # Missing: encryption (CKV_AWS_19)
}

# Insecure security group
resource "aws_security_group" "test" {
  name = "test-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # CKV_AWS_24: SSH from anywhere
  }

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # CKV_AWS_25: RDP from anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]  # CKV_AWS_277: Unrestricted egress
  }
}

# Insecure EC2 instance
resource "aws_instance" "test" {
  disable_api_termination = true
  metadata_options {
    http_endpoint = "enabled"
    http_tokens = "required"
  }
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  associate_public_ip_address = false  # CKV_AWS_88: Public IP

  # Missing: monitoring (CKV_AWS_8)
  # Missing: metadata_options (CKV_AWS_79)

  root_block_device {
    encrypted = true
    volume_size = 8
    # Missing: encrypted = true (CKV_AWS_126)
  }
}

# Insecure RDS instance
resource "aws_db_instance" "test" {
  backup_retention_period = 7
  backup_window = "03:00-04:00"
  iam_database_authentication_enabled = true
  enabled_cloudwatch_logs_exports = ["error", "general", "slowquery"]
  monitoring_interval = 60
  identifier     = "test-db"
  engine         = "mysql"
  engine_version = "5.7"
  instance_class = "db.t2.micro"

  allocated_storage = 20

  username = "admin"
  password = "password123"  # Bad practice but not a Checkov check

  # Missing: backup_retention_period (CKV_AWS_16)
  # Missing: storage_encrypted (CKV_AWS_17)
  # Missing: monitoring (CKV_AWS_118)
}

# Insecure Lambda function
resource "aws_lambda_function" "test" {
  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }
  reserved_concurrent_executions = 100
  vpc_config {
    subnet_ids = ["subnet-12345"]
    security_group_ids = ["sg-12345"]
  }
  tracing_config {
    mode = "Active"
  }
  filename      = "function.zip"
  function_name = "test-function"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "nodejs14.x"

  environment {
    variables = {
      SECRET = "hardcoded-secret"
    }
    # Missing: kms_key_arn (CKV_AWS_45)
  }

  # Missing: tracing_config (CKV_AWS_50)
  # Missing: reserved_concurrent_executions (CKV_AWS_115)
  # Missing: dead_letter_config (CKV_AWS_116)
}

# IAM role with overly permissive policy
resource "aws_iam_role" "lambda" {
  name = "lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda" {
  name = "lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:GetObject"  # CKV_AWS_63: Wildcard action
        Resource = "arn:aws:s3:::my-bucket/*"  # CKV_AWS_62: Wildcard resource
      }
    ]
  })
}

# ALB without HTTPS redirect
resource "aws_lb_listener" "test" {
  load_balancer_arn = aws_lb.test.arn
  port              = "80"
  protocol          = "HTTP"


resource "aws_flow_log" "main" {
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.flow_log.arn
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.main.id
}
  default_action {
    type = "redirect"
    redirect {
      protocol = "HTTPS"

resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.main.id

  # No ingress or egress rules - completely locked down
}
      port = "443"
      status_code = "HTTP_301"
    }
    type             = "forward"
    target_group_arn = aws_lb_target_group.test.arn
  }
  # Should redirect to HTTPS (CKV_AWS_2)
}

resource "aws_lb" "test" {
  access_logs {
    enabled = true
    bucket = "alb-logs-bucket"
  }
  enable_deletion_protection = true
  name               = "test-alb"
  load_balancer_type = "application"

  # Missing: access_logs (CKV_AWS_91)
  # Missing: drop_invalid_header_fields (CKV_AWS_103)
  # Missing: enable_deletion_protection (CKV_AWS_131)
}

resource "aws_lb_target_group" "test" {
  name     = "test-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.test.id
}

# VPC without flow logs
resource "aws_vpc" "test" {
  cidr_block = "10.0.0.0/16"

  # Missing: flow logs (CKV_AWS_130, CKV2_AWS_11)
}