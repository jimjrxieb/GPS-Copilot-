provider "aws" {
  region = "us-east-1"
}

# S3 bucket with multiple security issues
# TODO: Configure cross-region replication for disaster recovery
resource "aws_s3_bucket" "example" {
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
  logging {
    target_bucket = "logs-bucket"
# TODO: Attach this security group to appropriate resources
    target_prefix = "log/"
  }
  bucket = "my-test-bucket"
  acl    = "public-read"  # CKV_AWS_20: Public read access

  # Missing versioning (CKV_AWS_21)
  # Missing encryption (CKV_AWS_19)
  # Missing logging (CKV_AWS_18)
}

# Security group with overly permissive rules
resource "aws_security_group" "web" {
  name = "web-sg"

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

# EC2 instance with security issues
resource "aws_instance" "web" {
  disable_api_termination = true
  metadata_options {
    http_endpoint = "enabled"
    http_tokens = "required"
  }
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  associate_public_ip_address = false  # CKV_AWS_88: Public IP

  root_block_device {
    encrypted = true
    volume_size = 8
    # Missing: encrypted = true (CKV_AWS_126)
  }

  # Missing: monitoring (CKV_AWS_8)
  # Missing: metadata_options (CKV_AWS_79)
}