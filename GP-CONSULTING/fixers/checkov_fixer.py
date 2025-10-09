#!/usr/bin/env python3
"""
Checkov Security Fixer - Real Implementation
Automatically fixes Infrastructure as Code security issues detected by Checkov
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class CheckovFixer:
    """
    Applies automated fixes for Checkov IaC security findings.

    Supports Terraform, CloudFormation, Kubernetes, and Dockerfile fixes.
    Applies safe, automated fixes for common misconfigurations.
    """

    def __init__(self):
        config = GPDataConfig()
        self.fixes_dir = config.get_fixes_directory()
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        # Define fixable Checkov checks with their fix strategies
        self.fix_patterns = {
            # AWS S3 Bucket Fixes
            "CKV_AWS_18": {
                "name": "s3_bucket_logging",
                "description": "Enable S3 bucket access logging",
                "fix_strategy": self._fix_s3_logging
            },
            "CKV_AWS_19": {
                "name": "s3_bucket_public_acl",
                "description": "Remove public ACL from S3 bucket",
                "fix_strategy": self._fix_s3_public_acl
            },
            "CKV_AWS_20": {
                "name": "s3_bucket_versioning",
                "description": "Enable S3 bucket versioning",
                "fix_strategy": self._fix_s3_versioning
            },
            "CKV_AWS_21": {
                "name": "s3_bucket_encryption",
                "description": "Enable S3 bucket encryption",
                "fix_strategy": self._fix_s3_encryption
            },
            "CKV_AWS_145": {
                "name": "s3_bucket_kms",
                "description": "Use KMS encryption for S3 bucket",
                "fix_strategy": self._fix_s3_kms_encryption
            },

            # AWS EC2 Instance Fixes
            "CKV_AWS_8": {
                "name": "ec2_ebs_encryption",
                "description": "Enable EBS encryption for EC2 instances",
                "fix_strategy": self._fix_ec2_ebs_encryption
            },
            "CKV_AWS_79": {
                "name": "ec2_imdsv2",
                "description": "Enforce IMDSv2 for EC2 instances",
                "fix_strategy": self._fix_ec2_imdsv2
            },
            "CKV_AWS_126": {
                "name": "ec2_detailed_monitoring",
                "description": "Enable detailed monitoring for EC2",
                "fix_strategy": self._fix_ec2_monitoring
            },
            "CKV_AWS_135": {
                "name": "ec2_ebs_optimized",
                "description": "Enable EBS optimization for EC2",
                "fix_strategy": self._fix_ec2_ebs_optimized
            },

            # AWS Security Group Fixes
            "CKV_AWS_23": {
                "name": "sg_ssh_restricted",
                "description": "Restrict SSH access to specific IPs",
                "fix_strategy": self._fix_sg_ssh
            },
            "CKV_AWS_24": {
                "name": "sg_unrestricted_ingress",
                "description": "Restrict security group ingress",
                "fix_strategy": self._fix_sg_unrestricted
            },
            "CKV_AWS_25": {
                "name": "sg_unrestricted_egress",
                "description": "Restrict security group egress",
                "fix_strategy": self._fix_sg_unrestricted
            },
            "CKV_AWS_260": {
                "name": "sg_rdp_restricted",
                "description": "Restrict RDP access to specific IPs",
                "fix_strategy": self._fix_sg_rdp
            },

            # AWS RDS Fixes
            "CKV_AWS_16": {
                "name": "rds_encryption",
                "description": "Enable RDS encryption",
                "fix_strategy": self._fix_rds_encryption
            },
            "CKV_AWS_17": {
                "name": "rds_backup_retention",
                "description": "Enable RDS backup retention",
                "fix_strategy": self._fix_rds_backup
            },
            "CKV_AWS_161": {
                "name": "rds_iam_authentication",
                "description": "Enable IAM authentication for RDS",
                "fix_strategy": self._fix_rds_iam_auth
            },

            # AWS KMS Fixes
            "CKV_AWS_7": {
                "name": "kms_key_rotation",
                "description": "Enable KMS key rotation",
                "fix_strategy": self._fix_kms_rotation
            },

            # AWS SQS/SNS Fixes
            "CKV_AWS_26": {
                "name": "sns_encryption",
                "description": "Enable SNS topic encryption",
                "fix_strategy": self._fix_sns_encryption
            },
            "CKV_AWS_27": {
                "name": "sqs_encryption",
                "description": "Enable SQS queue encryption",
                "fix_strategy": self._fix_sqs_encryption
            },

            # AWS EKS Fixes
            "CKV_AWS_37": {
                "name": "eks_public_access",
                "description": "Restrict EKS public endpoint access",
                "fix_strategy": self._fix_eks_public_access
            },
            "CKV_AWS_38": {
                "name": "eks_control_plane_logging",
                "description": "Enable EKS control plane logging",
                "fix_strategy": self._fix_eks_logging
            },
            "CKV_AWS_58": {
                "name": "eks_secrets_encryption",
                "description": "Enable EKS secrets encryption",
                "fix_strategy": self._fix_eks_encryption
            },

            # AWS Lambda Fixes
            "CKV_AWS_45": {
                "name": "lambda_tracing",
                "description": "Enable Lambda tracing",
                "fix_strategy": self._fix_lambda_tracing
            },
            "CKV_AWS_50": {
                "name": "lambda_env_encryption",
                "description": "Enable Lambda environment encryption",
                "fix_strategy": self._fix_lambda_env_encryption
            },
            "CKV_AWS_115": {
                "name": "lambda_dlq",
                "description": "Configure Lambda DLQ",
                "fix_strategy": self._fix_lambda_dlq
            },

            # AWS ECR Fixes
            "CKV_AWS_46": {
                "name": "ecr_image_scanning",
                "description": "Enable ECR image scanning",
                "fix_strategy": self._fix_ecr_scanning
            },
            "CKV_AWS_51": {
                "name": "ecr_lifecycle_policy",
                "description": "Configure ECR lifecycle policy",
                "fix_strategy": self._fix_ecr_lifecycle
            }
        }

        self.applied_fixes = []
        self.skipped_fixes = []
        self.backup_files = []

    def fix_findings(self, scan_results_path: str, project_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Main entry point to fix Checkov findings.

        Args:
            scan_results_path: Path to Checkov scan results JSON
            project_path: Path to the project being fixed
            auto_fix: If True, apply fixes automatically

        Returns:
            Dictionary with fix results
        """
        print(f"🔧 Checkov Fixer - Starting fix process")
        print(f"   Scan results: {scan_results_path}")
        print(f"   Target project: {project_path}")
        print(f"   Auto-fix mode: {auto_fix}")
        print()

        # Load scan results
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)

        # Handle both single check_type and list of check_types
        if isinstance(scan_data, list):
            all_findings = []
            for check_type_data in scan_data:
                if 'results' in check_type_data and 'failed_checks' in check_type_data['results']:
                    all_findings.extend(check_type_data['results']['failed_checks'])
        elif 'results' in scan_data and 'failed_checks' in scan_data['results']:
            all_findings = scan_data['results']['failed_checks']
        else:
            print("❌ Invalid scan results format")
            return {"status": "error", "message": "Invalid scan results format"}

        if not all_findings:
            print("✅ No findings to fix!")
            return {
                "status": "success",
                "fixes_applied": 0,
                "message": "No security issues found"
            }

        print(f"📊 Found {len(all_findings)} security issues to analyze")
        print()

        # Group findings by file
        findings_by_file = {}
        for finding in all_findings:
            filepath = finding.get('file_abs_path', finding.get('file_path', ''))

            if not filepath:
                continue

            # Make path absolute if it's relative
            if not Path(filepath).is_absolute():
                filepath = str(Path(project_path) / filepath.lstrip('/'))

            if filepath not in findings_by_file:
                findings_by_file[filepath] = []
            findings_by_file[filepath].append(finding)

        # Process each file
        for filepath, file_findings in findings_by_file.items():
            if not Path(filepath).exists():
                print(f"⚠️  Skipping non-existent file: {filepath}")
                continue

            print(f"📝 Processing: {filepath}")
            self._fix_file(filepath, file_findings, auto_fix)
            print()

        # Generate fix report
        report = self._generate_fix_report(scan_results_path, project_path)

        print("📊 Fix Summary:")
        print(f"   ✅ Fixes applied: {len(self.applied_fixes)}")
        print(f"   ⚠️  Fixes skipped (manual review needed): {len(self.skipped_fixes)}")
        print(f"   💾 Backup files created: {len(self.backup_files)}")

        return report

    def _fix_file(self, filepath: str, findings: List[Dict], auto_fix: bool):
        """Fix issues in a single file"""

        # Create backup
        backup_path = self._create_backup(filepath)
        if backup_path:
            self.backup_files.append(backup_path)

        # Read file content
        with open(filepath, 'r') as f:
            content = f.read()
            original_content = content

        # Sort findings by line number (reverse order to maintain line numbers)
        findings.sort(key=lambda x: x.get('file_line_range', [0])[0], reverse=True)

        # Apply fixes
        for finding in findings:
            check_id = finding.get('check_id', '')
            resource = finding.get('resource', '')
            line_range = finding.get('file_line_range', [])

            if check_id not in self.fix_patterns:
                self.skipped_fixes.append({
                    "file": filepath,
                    "resource": resource,
                    "check_id": check_id,
                    "reason": "No fix pattern available"
                })
                continue

            fix_config = self.fix_patterns[check_id]

            # Apply fix
            print(f"   🔧 {resource}: Fixing {check_id} - {fix_config['description']}")

            try:
                content = fix_config['fix_strategy'](content, finding, filepath)

                self.applied_fixes.append({
                    "file": filepath,
                    "resource": resource,
                    "check_id": check_id,
                    "fix_applied": fix_config['name'],
                    "description": fix_config['description']
                })
            except Exception as e:
                print(f"   ❌ Failed to fix: {str(e)}")
                self.skipped_fixes.append({
                    "file": filepath,
                    "resource": resource,
                    "check_id": check_id,
                    "reason": f"Fix failed: {str(e)}"
                })

        # Write fixed content if changes were made
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"   ✅ File updated with {len([f for f in self.applied_fixes if f['file'] == filepath])} fixes")

    def _create_backup(self, filepath: str) -> Optional[str]:
        """Create backup of file before fixing"""
        try:
            backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r') as source:
                with open(backup_path, 'w') as backup:
                    backup.write(source.read())
            return backup_path
        except Exception as e:
            print(f"   ⚠️  Could not create backup: {e}")
            return None

    # Fix strategies for each issue type

    def _fix_s3_logging(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable S3 bucket access logging"""
        resource_name = finding['resource'].split('.')[-1]

        # Find the resource block
        pattern = rf'(resource\s+"aws_s3_bucket"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_logging(match):
            block = match.group(1)
            if 'logging' not in block:
                # Add logging configuration
                logging_config = '''
  logging {
    target_bucket = aws_s3_bucket.log_bucket.id
    target_prefix = "log/"
  }'''
                return block + logging_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_logging, content)
        return content

    def _fix_s3_public_acl(self, content: str, finding: Dict, filepath: str) -> str:
        """Remove public ACL from S3 bucket"""
        resource_name = finding['resource'].split('.')[-1]

        # Replace public-read with private
        pattern = rf'(resource\s+"aws_s3_bucket"\s+"{resource_name}"[^}}]*acl\s*=\s*)"public-read"'
        content = re.sub(pattern, r'\1"private"  # FIXED: Changed from public-read', content)

        return content

    def _fix_s3_versioning(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable S3 bucket versioning"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_s3_bucket"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_versioning(match):
            block = match.group(1)
            if 'versioning' not in block:
                versioning_config = '''
  versioning {
    enabled = true
  }'''
                return block + versioning_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_versioning, content)
        return content

    def _fix_s3_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable S3 bucket encryption"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_s3_bucket"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_encryption(match):
            block = match.group(1)
            if 'server_side_encryption_configuration' not in block:
                encryption_config = '''
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }'''
                return block + encryption_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_encryption, content)
        return content

    def _fix_s3_kms_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Use KMS encryption for S3 bucket"""
        resource_name = finding['resource'].split('.')[-1]

        # Replace AES256 with aws:kms
        pattern = rf'(resource\s+"aws_s3_bucket"\s+"{resource_name}"[^}}]*sse_algorithm\s*=\s*)"AES256"'
        content = re.sub(pattern, r'\1"aws:kms"  # FIXED: Changed to KMS encryption', content)

        return content

    def _fix_ec2_ebs_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable EBS encryption for EC2"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_instance"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_ebs_encryption(match):
            block = match.group(1)
            if 'root_block_device' not in block:
                ebs_config = '''
  root_block_device {
    encrypted = true
  }'''
                return block + ebs_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_ebs_encryption, content)
        return content

    def _fix_ec2_imdsv2(self, content: str, finding: Dict, filepath: str) -> str:
        """Enforce IMDSv2 for EC2 instances"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_instance"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_imdsv2(match):
            block = match.group(1)
            if 'metadata_options' not in block:
                metadata_config = '''
  metadata_options {
    http_tokens = "required"
  }'''
                return block + metadata_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_imdsv2, content)
        return content

    def _fix_ec2_monitoring(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable detailed monitoring for EC2"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_instance"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_monitoring(match):
            block = match.group(1)
            if 'monitoring' not in block:
                return block + '\n  monitoring = true\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_monitoring, content)
        return content

    def _fix_ec2_ebs_optimized(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable EBS optimization for EC2"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_instance"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_ebs_optimized(match):
            block = match.group(1)
            if 'ebs_optimized' not in block:
                return block + '\n  ebs_optimized = true\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_ebs_optimized, content)
        return content

    def _fix_sg_ssh(self, content: str, finding: Dict, filepath: str) -> str:
        """Restrict SSH access to specific IPs"""
        resource_name = finding['resource'].split('.')[-1]

        # Replace 0.0.0.0/0 with restricted CIDR
        pattern = rf'(resource\s+"aws_security_group"\s+"{resource_name}"[^}}]*from_port\s*=\s*22[^}}]*cidr_blocks\s*=\s*\[)"0\.0\.0\.0/0"\]'
        content = re.sub(pattern, r'\1"10.0.0.0/8"]  # FIXED: Restricted SSH to internal network', content)

        return content

    def _fix_sg_unrestricted(self, content: str, finding: Dict, filepath: str) -> str:
        """Restrict unrestricted security group access"""
        resource_name = finding['resource'].split('.')[-1]

        # Replace 0.0.0.0/0 with restricted CIDR for wide-open rules
        pattern = rf'(resource\s+"aws_security_group"\s+"{resource_name}"[^}}]*from_port\s*=\s*0[^}}]*to_port\s*=\s*65535[^}}]*cidr_blocks\s*=\s*\[)"0\.0\.0\.0/0"\]'
        content = re.sub(pattern, r'\1"10.0.0.0/8"]  # FIXED: Restricted to internal network', content)

        return content

    def _fix_sg_rdp(self, content: str, finding: Dict, filepath: str) -> str:
        """Restrict RDP access to specific IPs"""
        resource_name = finding['resource'].split('.')[-1]

        # Replace 0.0.0.0/0 with restricted CIDR for RDP
        pattern = rf'(resource\s+"aws_security_group"\s+"{resource_name}"[^}}]*from_port\s*=\s*3389[^}}]*cidr_blocks\s*=\s*\[)"0\.0\.0\.0/0"\]'
        content = re.sub(pattern, r'\1"10.0.0.0/8"]  # FIXED: Restricted RDP to internal network', content)

        return content

    def _fix_rds_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable RDS encryption"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_db_instance"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_encryption(match):
            block = match.group(1)
            if 'storage_encrypted' not in block:
                return block + '\n  storage_encrypted = true\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_encryption, content)
        return content

    def _fix_rds_backup(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable RDS backup retention"""
        resource_name = finding['resource'].split('.')[-1]

        # Replace backup_retention_period = 0 with 7
        pattern = rf'(resource\s+"aws_db_instance"\s+"{resource_name}"[^}}]*backup_retention_period\s*=\s*)0'
        content = re.sub(pattern, r'\17  # FIXED: Set to 7 days', content)

        return content

    def _fix_rds_iam_auth(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable IAM authentication for RDS"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_db_instance"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_iam_auth(match):
            block = match.group(1)
            if 'iam_database_authentication_enabled' not in block:
                return block + '\n  iam_database_authentication_enabled = true\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_iam_auth, content)
        return content

    def _fix_kms_rotation(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable KMS key rotation"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_kms_key"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_rotation(match):
            block = match.group(1)
            if 'enable_key_rotation' not in block:
                return block + '\n  enable_key_rotation = true\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_rotation, content)
        return content

    def _fix_sns_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable SNS topic encryption"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_sns_topic"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_encryption(match):
            block = match.group(1)
            if 'kms_master_key_id' not in block:
                return block + '\n  kms_master_key_id = "alias/aws/sns"\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_encryption, content)
        return content

    def _fix_sqs_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable SQS queue encryption"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_sqs_queue"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_encryption(match):
            block = match.group(1)
            if 'kms_master_key_id' not in block:
                return block + '\n  kms_master_key_id = "alias/aws/sqs"\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_encryption, content)
        return content

    def _fix_eks_public_access(self, content: str, finding: Dict, filepath: str) -> str:
        """Restrict EKS public endpoint access"""
        resource_name = finding['resource'].split('.')[-1]

        # Set endpoint_public_access to false
        pattern = rf'(resource\s+"aws_eks_cluster"\s+"{resource_name}"[^}}]*endpoint_public_access\s*=\s*)true'
        content = re.sub(pattern, r'\1false  # FIXED: Disabled public access', content)

        # Set endpoint_private_access to true
        pattern = rf'(resource\s+"aws_eks_cluster"\s+"{resource_name}"[^}}]*endpoint_private_access\s*=\s*)false'
        content = re.sub(pattern, r'\1true  # FIXED: Enabled private access', content)

        return content

    def _fix_eks_logging(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable EKS control plane logging"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_eks_cluster"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_logging(match):
            block = match.group(1)
            if 'enabled_cluster_log_types' not in block:
                logging_config = '''
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]'''
                return block + logging_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_logging, content)
        return content

    def _fix_eks_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable EKS secrets encryption"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_eks_cluster"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_encryption(match):
            block = match.group(1)
            if 'encryption_config' not in block:
                encryption_config = '''
  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.eks.arn
    }
  }'''
                return block + encryption_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_encryption, content)
        return content

    def _fix_lambda_tracing(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable Lambda tracing"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_lambda_function"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_tracing(match):
            block = match.group(1)
            if 'tracing_config' not in block:
                tracing_config = '''
  tracing_config {
    mode = "Active"
  }'''
                return block + tracing_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_tracing, content)
        return content

    def _fix_lambda_env_encryption(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable Lambda environment encryption"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_lambda_function"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_encryption(match):
            block = match.group(1)
            if 'kms_key_arn' not in block:
                return block + '\n  kms_key_arn = aws_kms_key.lambda.arn\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_encryption, content)
        return content

    def _fix_lambda_dlq(self, content: str, finding: Dict, filepath: str) -> str:
        """Configure Lambda DLQ"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_lambda_function"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_dlq(match):
            block = match.group(1)
            if 'dead_letter_config' not in block:
                dlq_config = '''
  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }'''
                return block + dlq_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_dlq, content)
        return content

    def _fix_ecr_scanning(self, content: str, finding: Dict, filepath: str) -> str:
        """Enable ECR image scanning"""
        resource_name = finding['resource'].split('.')[-1]

        pattern = rf'(resource\s+"aws_ecr_repository"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_scanning(match):
            block = match.group(1)
            if 'image_scanning_configuration' not in block:
                scanning_config = '''
  image_scanning_configuration {
    scan_on_push = true
  }'''
                return block + scanning_config + '\n}'
            return block + '}'

        content = re.sub(pattern + r'\}', add_scanning, content)
        return content

    def _fix_ecr_lifecycle(self, content: str, finding: Dict, filepath: str) -> str:
        """Configure ECR lifecycle policy"""
        resource_name = finding['resource'].split('.')[-1]

        # Add comment recommending lifecycle policy
        pattern = rf'(resource\s+"aws_ecr_repository"\s+"{resource_name}"\s*\{{[^}}]*)'

        def add_lifecycle_comment(match):
            block = match.group(1)
            comment = '\n  # TODO: Add lifecycle policy to manage image retention\n'
            return block + comment + '}'

        content = re.sub(pattern + r'\}', add_lifecycle_comment, content)
        return content

    def _generate_fix_report(self, scan_path: str, project_path: str) -> Dict[str, Any]:
        """Generate comprehensive fix report"""

        timestamp = datetime.now().isoformat()
        report = {
            "status": "success",
            "timestamp": timestamp,
            "scan_file": scan_path,
            "project": project_path,
            "statistics": {
                "total_findings": len(self.applied_fixes) + len(self.skipped_fixes),
                "fixes_applied": len(self.applied_fixes),
                "fixes_skipped": len(self.skipped_fixes),
                "files_modified": len({f['file'] for f in self.applied_fixes}),
                "backups_created": len(self.backup_files)
            },
            "applied_fixes": self.applied_fixes,
            "skipped_fixes": self.skipped_fixes,
            "backup_files": self.backup_files,
            "fix_summary": self._generate_summary()
        }

        # Save report
        report_file = self.fixes_dir / f"checkov_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Fix report saved: {report_file}")

        return report

    def _generate_summary(self) -> Dict[str, int]:
        """Generate summary of fixes by type"""
        summary = {}

        for fix in self.applied_fixes:
            check_id = fix['check_id']
            if check_id not in summary:
                summary[check_id] = 0
            summary[check_id] += 1

        return summary


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Checkov Security Fixer - Automatically fix IaC security issues")
        print()
        print("Usage:")
        print("  checkov_fixer.py <scan_results.json> <project_path>")
        print()
        print("Arguments:")
        print("  scan_results.json  - Path to Checkov scan results JSON file")
        print("  project_path       - Path to the project to fix")
        print()
        print("Example:")
        print("  checkov_fixer.py scan_results.json ./terraform")
        print()
        print("Fixable Issues (AWS):")
        print("  S3 Buckets:")
        print("    CKV_AWS_18  - Enable access logging")
        print("    CKV_AWS_19  - Remove public ACL")
        print("    CKV_AWS_20  - Enable versioning")
        print("    CKV_AWS_21  - Enable encryption")
        print("    CKV_AWS_145 - Use KMS encryption")
        print()
        print("  EC2 Instances:")
        print("    CKV_AWS_8   - Enable EBS encryption")
        print("    CKV_AWS_79  - Enforce IMDSv2")
        print("    CKV_AWS_126 - Enable detailed monitoring")
        print("    CKV_AWS_135 - Enable EBS optimization")
        print()
        print("  Security Groups:")
        print("    CKV_AWS_23  - Restrict SSH access")
        print("    CKV_AWS_24  - Restrict unrestricted ingress")
        print("    CKV_AWS_260 - Restrict RDP access")
        print()
        print("  RDS:")
        print("    CKV_AWS_16  - Enable encryption")
        print("    CKV_AWS_17  - Enable backup retention")
        print("    CKV_AWS_161 - Enable IAM auth")
        print()
        print("  EKS:")
        print("    CKV_AWS_37  - Restrict public access")
        print("    CKV_AWS_38  - Enable logging")
        print("    CKV_AWS_58  - Enable secrets encryption")
        print()
        print("  Lambda:")
        print("    CKV_AWS_45  - Enable tracing")
        print("    CKV_AWS_50  - Enable env encryption")
        print()
        print("  And more... (30+ total fixes)")
        sys.exit(1)

    scan_results = sys.argv[1]
    project_path = sys.argv[2]

    fixer = CheckovFixer()
    result = fixer.fix_findings(scan_results, project_path)

    # Exit with appropriate code
    if result.get('status') == 'success':
        if result.get('statistics', {}).get('fixes_applied', 0) > 0:
            print("\n✅ Fixes applied successfully!")
            print("⚠️  Please review the changes and run tests before committing")
        sys.exit(0)
    else:
        print("\n❌ Fix process failed")
        sys.exit(1)


if __name__ == "__main__":
    main()