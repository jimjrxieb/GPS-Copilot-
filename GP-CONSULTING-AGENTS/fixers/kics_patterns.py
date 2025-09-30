#!/usr/bin/env python3
"""
KICS Remediation Patterns - Production-Ready Fix Templates
Based on proven KICS auto-remediation logic
"""

# Known fix patterns from KICS and industry best practices
TERRAFORM_FIX_PATTERNS = {
    "CKV_AWS_8": {
        "name": "EBS Encryption",
        "pattern": "root_block_device_encryption",
        "template": """
  root_block_device {
    encrypted = true
  }""",
        "target_block": "root_block_device",
        "attribute": "encrypted",
        "value": "true",
        "description": "Enable EBS encryption for EC2 instances"
    },

    "CKV_AWS_135": {
        "name": "EBS Optimization",
        "pattern": "ebs_optimization",
        "template": """
  ebs_optimized = true""",
        "target_block": None,  # Resource level
        "attribute": "ebs_optimized",
        "value": "true",
        "description": "Enable EBS optimization for EC2 instances"
    },

    "CKV2_AWS_41": {
        "name": "IAM Instance Profile",
        "pattern": "iam_instance_profile",
        "template": """
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name""",
        "target_block": None,  # Resource level
        "attribute": "iam_instance_profile",
        "value": "aws_iam_instance_profile.ec2_profile.name",
        "description": "Attach IAM instance profile to EC2 instances",
        "requires_resources": [
            {
                "type": "aws_iam_role",
                "name": "ec2_role",
                "template": """
resource "aws_iam_role" "ec2_role" {
  name = "ec2-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}"""
            },
            {
                "type": "aws_iam_instance_profile",
                "name": "ec2_profile",
                "template": """
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.ec2_role.name

  tags = var.tags
}"""
            }
        ]
    },

    "CKV_AWS_126": {
        "name": "EC2 Detailed Monitoring",
        "pattern": "monitoring_enabled",
        "template": """
  monitoring = true""",
        "target_block": None,
        "attribute": "monitoring",
        "value": "true",
        "description": "Enable detailed monitoring for EC2 instances"
    },

    "CKV_AWS_79": {
        "name": "IMDSv2 Enforcement",
        "pattern": "imdsv2_required",
        "template": """
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
    http_put_response_hop_limit = 1
  }""",
        "target_block": "metadata_options",
        "attributes": {
            "http_endpoint": "enabled",
            "http_tokens": "required",
            "http_put_response_hop_limit": "1"
        },
        "description": "Enforce IMDSv2 for EC2 metadata access"
    }
}

def get_fix_pattern(check_id: str) -> dict:
    """Get the proven fix pattern for a specific check ID"""
    return TERRAFORM_FIX_PATTERNS.get(check_id, {})

def get_all_patterns() -> dict:
    """Get all available fix patterns"""
    return TERRAFORM_FIX_PATTERNS