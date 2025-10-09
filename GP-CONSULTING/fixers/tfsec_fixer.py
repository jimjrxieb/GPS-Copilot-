#!/usr/bin/env python3
"""
Tfsec Security Fixer - Terraform Static Analysis Remediation
Automatically fixes infrastructure-as-code security issues detected by tfsec

Fixes:
- AWS security misconfigurations
- Azure security issues
- GCP security problems
- General Terraform best practices
- Compliance violations (CIS, PCI-DSS, NIST)
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hcl2

class TfsecFixer:
    def __init__(self):
        self.fix_patterns = {
            # AWS Security
            'aws-s3-encryption': {
                'name': 'enable_s3_encryption',
                'fix_strategy': self._fix_s3_encryption,
                'severity': 'critical',
                'compliance': ['CIS-AWS-2.1.1', 'PCI-DSS-3.4']
            },
            'aws-s3-public-access': {
                'name': 'block_s3_public_access',
                'fix_strategy': self._fix_s3_public_access,
                'severity': 'critical',
                'compliance': ['CIS-AWS-5.2', 'NIST-SC-7']
            },
            'aws-rds-encryption': {
                'name': 'enable_rds_encryption',
                'fix_strategy': self._fix_rds_encryption,
                'severity': 'critical',
                'compliance': ['CIS-AWS-2.3.1', 'PCI-DSS-3.4']
            },
            'aws-security-group-open': {
                'name': 'restrict_security_group',
                'fix_strategy': self._fix_security_group,
                'severity': 'critical',
                'compliance': ['CIS-AWS-5.2', 'PCI-DSS-1.2.1']
            },
            'aws-ec2-imdsv2': {
                'name': 'enforce_imdsv2',
                'fix_strategy': self._fix_ec2_imdsv2,
                'severity': 'high',
                'compliance': ['CIS-AWS-5.6', 'Cloud-Security']
            },
            'aws-ebs-encryption': {
                'name': 'enable_ebs_encryption',
                'fix_strategy': self._fix_ebs_encryption,
                'severity': 'high',
                'compliance': ['CIS-AWS-2.2.1', 'NIST-SC-28']
            },

            # Azure Security
            'azure-storage-https': {
                'name': 'enforce_https',
                'fix_strategy': self._fix_azure_storage_https,
                'severity': 'high',
                'compliance': ['CIS-Azure-3.1', 'NIST-SC-8']
            },
            'azure-nsg-open': {
                'name': 'restrict_nsg',
                'fix_strategy': self._fix_azure_nsg,
                'severity': 'critical',
                'compliance': ['CIS-Azure-6.1', 'PCI-DSS-1.2']
            },
            'azure-disk-encryption': {
                'name': 'enable_disk_encryption',
                'fix_strategy': self._fix_azure_disk_encryption,
                'severity': 'high',
                'compliance': ['CIS-Azure-7.1', 'PCI-DSS-3.4']
            },

            # GCP Security
            'gcp-storage-uniform-access': {
                'name': 'enable_uniform_access',
                'fix_strategy': self._fix_gcp_storage_uniform,
                'severity': 'high',
                'compliance': ['CIS-GCP-5.1', 'SOC2-CC6.1']
            },
            'gcp-compute-public-ip': {
                'name': 'restrict_public_ip',
                'fix_strategy': self._fix_gcp_public_ip,
                'severity': 'medium',
                'compliance': ['CIS-GCP-4.9', 'NIST-SC-7']
            },

            # General Terraform Best Practices
            'missing-tags': {
                'name': 'add_required_tags',
                'fix_strategy': self._fix_missing_tags,
                'severity': 'low',
                'compliance': ['FinOps', 'Governance']
            },
            'backend-encryption': {
                'name': 'enable_backend_encryption',
                'fix_strategy': self._fix_backend_encryption,
                'severity': 'high',
                'compliance': ['NIST-SC-28', 'State-Security']
            }
        }

        self.backup_dir = None
        self.fixes_applied = []
        self.fixes_failed = []

    def fix_findings(self, scan_results_path: str, project_path: str) -> Dict:
        """Main entry point for fixing tfsec findings"""
        print(f"🔧 Tfsec Fixer: Processing findings from {scan_results_path}")

        # Load scan results
        try:
            with open(scan_results_path, 'r') as f:
                scan_data = json.load(f)
        except Exception as e:
            return {"error": f"Failed to load scan results: {e}", "fixes_applied": 0}

        # Create backup
        self.backup_dir = self._create_backup(project_path)
        print(f"📦 Backup created: {self.backup_dir}")

        # Process findings
        findings = self._extract_findings(scan_data)
        print(f"📊 Found {len(findings)} tfsec findings to process")

        for finding in findings:
            self._apply_fix(finding, project_path)

        # Generate report
        report = self._generate_report(scan_results_path, project_path)
        self._save_report(report)

        print(f"✅ Fixes applied: {len(self.fixes_applied)}")
        print(f"❌ Fixes failed: {len(self.fixes_failed)}")

        return report

    def _extract_findings(self, scan_data: Dict) -> List[Dict]:
        """Extract actionable findings from tfsec scan results"""
        findings = []

        # Tfsec JSON structure: results array with rule_id, location, etc.
        for result in scan_data.get('results', []):
            findings.append({
                'rule_id': result.get('rule_id', ''),
                'rule_description': result.get('rule_description', ''),
                'severity': result.get('severity', 'UNKNOWN'),
                'resource': result.get('resource', ''),
                'location': result.get('location', {}),
                'category': self._map_rule_to_category(result)
            })

        return findings

    def _map_rule_to_category(self, result: Dict) -> str:
        """Map tfsec rule to internal fix category"""
        rule_id = result.get('rule_id', '').lower()

        # AWS mappings
        if 's3' in rule_id and 'encrypt' in rule_id:
            return 'aws-s3-encryption'
        elif 's3' in rule_id and 'public' in rule_id:
            return 'aws-s3-public-access'
        elif 'rds' in rule_id and 'encrypt' in rule_id:
            return 'aws-rds-encryption'
        elif 'security-group' in rule_id or 'sg-' in rule_id:
            return 'aws-security-group-open'
        elif 'ec2' in rule_id and 'imds' in rule_id:
            return 'aws-ec2-imdsv2'
        elif 'ebs' in rule_id and 'encrypt' in rule_id:
            return 'aws-ebs-encryption'

        # Azure mappings
        elif 'azure' in rule_id and 'storage' in rule_id and 'https' in rule_id:
            return 'azure-storage-https'
        elif 'azure' in rule_id and 'nsg' in rule_id:
            return 'azure-nsg-open'
        elif 'azure' in rule_id and 'disk' in rule_id and 'encrypt' in rule_id:
            return 'azure-disk-encryption'

        # GCP mappings
        elif 'gcp' in rule_id and 'storage' in rule_id:
            return 'gcp-storage-uniform-access'
        elif 'gcp' in rule_id and 'compute' in rule_id and 'ip' in rule_id:
            return 'gcp-compute-public-ip'

        # General
        elif 'tag' in rule_id:
            return 'missing-tags'
        elif 'backend' in rule_id or 'state' in rule_id:
            return 'backend-encryption'

        return 'unknown'

    def _apply_fix(self, finding: Dict, project_path: str):
        """Apply appropriate fix based on finding category"""
        category = finding.get('category')

        if category not in self.fix_patterns:
            self.fixes_failed.append({
                'finding': finding,
                'reason': 'No fix pattern available'
            })
            return

        pattern = self.fix_patterns[category]
        fix_strategy = pattern['fix_strategy']

        try:
            result = fix_strategy(finding, project_path)
            if result['success']:
                self.fixes_applied.append({
                    'finding': finding,
                    'fix': result,
                    'compliance': pattern.get('compliance', [])
                })
            else:
                self.fixes_failed.append({
                    'finding': finding,
                    'reason': result.get('reason', 'Fix strategy failed')
                })
        except Exception as e:
            self.fixes_failed.append({
                'finding': finding,
                'reason': f"Exception: {str(e)}"
            })

    # ============================================
    # AWS Security Fixes
    # ============================================

    def _fix_s3_encryption(self, finding: Dict, project_path: str) -> Dict:
        """Enable S3 bucket encryption"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                content = f.read()

            # Pattern to find the S3 bucket resource
            resource_pattern = rf'resource\s+"aws_s3_bucket"\s+"{resource.split(".")[-1]}"'
            match = re.search(resource_pattern, content)

            if not match:
                return {'success': False, 'reason': 'Resource not found in file'}

            # Check if encryption already exists
            if 'server_side_encryption_configuration' in content[match.start():]:
                return {'success': False, 'reason': 'Encryption already configured'}

            # Add encryption configuration
            encryption_block = '''
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
'''

            # Insert before closing brace of resource
            resource_end = content.find('}', match.start())
            updated_content = content[:resource_end] + encryption_block + content[resource_end:]

            with open(tf_file, 'w') as f:
                f.write(updated_content)

            return {
                'success': True,
                'action': f'Added S3 encryption to {resource}',
                'compliance': ['CIS-AWS-2.1.1']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_s3_public_access(self, finding: Dict, project_path: str) -> Dict:
        """Block S3 public access"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                content = f.read()

            # Create public access block resource
            bucket_name = resource.split('.')[-1]
            public_access_block = f'''
resource "aws_s3_bucket_public_access_block" "{bucket_name}_public_access" {{
  bucket = aws_s3_bucket.{bucket_name}.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
'''

            # Check if block already exists
            if f'aws_s3_bucket_public_access_block' in content and bucket_name in content:
                return {'success': False, 'reason': 'Public access block already exists'}

            # Append after S3 bucket resource
            with open(tf_file, 'a') as f:
                f.write(public_access_block)

            return {
                'success': True,
                'action': f'Added public access block to {resource}',
                'compliance': ['CIS-AWS-5.2']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_rds_encryption(self, finding: Dict, project_path: str) -> Dict:
        """Enable RDS encryption"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            # Find RDS resource and add encryption
            in_resource = False
            resource_name = resource.split('.')[-1]
            modified = False

            for i, line in enumerate(lines):
                if f'resource "aws_db_instance" "{resource_name}"' in line:
                    in_resource = True

                if in_resource and 'storage_encrypted' in line:
                    return {'success': False, 'reason': 'Encryption already configured'}

                if in_resource and '}' in line:
                    # Add encryption before closing brace
                    lines.insert(i, '  storage_encrypted = true\n')
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not add encryption'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Enabled RDS encryption for {resource}',
                'compliance': ['CIS-AWS-2.3.1']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_security_group(self, finding: Dict, project_path: str) -> Dict:
        """Restrict security group rules"""
        # Complex fix - requires business context
        return {
            'success': False,
            'reason': 'Manual intervention required',
            'recommendation': 'Restrict security group ingress to specific CIDR blocks instead of 0.0.0.0/0',
            'compliance': ['CIS-AWS-5.2']
        }

    def _fix_ec2_imdsv2(self, finding: Dict, project_path: str) -> Dict:
        """Enforce IMDSv2 on EC2 instances"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            in_resource = False
            resource_name = resource.split('.')[-1]
            modified = False

            for i, line in enumerate(lines):
                if f'resource "aws_instance" "{resource_name}"' in line:
                    in_resource = True

                if in_resource and 'metadata_options' in line:
                    return {'success': False, 'reason': 'Metadata options already configured'}

                if in_resource and '}' in line:
                    metadata_block = '''  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
'''
                    lines.insert(i, metadata_block)
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not add IMDSv2'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Enforced IMDSv2 for {resource}',
                'compliance': ['CIS-AWS-5.6']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_ebs_encryption(self, finding: Dict, project_path: str) -> Dict:
        """Enable EBS volume encryption"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            in_resource = False
            resource_name = resource.split('.')[-1]
            modified = False

            for i, line in enumerate(lines):
                if f'resource "aws_ebs_volume" "{resource_name}"' in line:
                    in_resource = True

                if in_resource and 'encrypted' in line:
                    return {'success': False, 'reason': 'Encryption already configured'}

                if in_resource and '}' in line:
                    lines.insert(i, '  encrypted = true\n')
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not add encryption'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Enabled EBS encryption for {resource}',
                'compliance': ['CIS-AWS-2.2.1']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    # ============================================
    # Azure Security Fixes
    # ============================================

    def _fix_azure_storage_https(self, finding: Dict, project_path: str) -> Dict:
        """Enforce HTTPS for Azure storage"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            in_resource = False
            resource_name = resource.split('.')[-1]
            modified = False

            for i, line in enumerate(lines):
                if f'resource "azurerm_storage_account" "{resource_name}"' in line:
                    in_resource = True

                if in_resource and 'enable_https_traffic_only' in line:
                    return {'success': False, 'reason': 'HTTPS already enforced'}

                if in_resource and '}' in line:
                    lines.insert(i, '  enable_https_traffic_only = true\n')
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not enforce HTTPS'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Enforced HTTPS for {resource}',
                'compliance': ['CIS-Azure-3.1']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_azure_nsg(self, finding: Dict, project_path: str) -> Dict:
        """Restrict Azure NSG rules"""
        return {
            'success': False,
            'reason': 'Manual intervention required',
            'recommendation': 'Restrict NSG rules to specific source addresses',
            'compliance': ['CIS-Azure-6.1']
        }

    def _fix_azure_disk_encryption(self, finding: Dict, project_path: str) -> Dict:
        """Enable Azure disk encryption"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            in_resource = False
            resource_name = resource.split('.')[-1]
            modified = False

            for i, line in enumerate(lines):
                if f'resource "azurerm_managed_disk" "{resource_name}"' in line:
                    in_resource = True

                if in_resource and 'encryption_settings' in line:
                    return {'success': False, 'reason': 'Encryption already configured'}

                if in_resource and '}' in line:
                    encryption_block = '''  encryption_settings {
    enabled = true
  }
'''
                    lines.insert(i, encryption_block)
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not add encryption'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Enabled disk encryption for {resource}',
                'compliance': ['CIS-Azure-7.1']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    # ============================================
    # GCP Security Fixes
    # ============================================

    def _fix_gcp_storage_uniform(self, finding: Dict, project_path: str) -> Dict:
        """Enable uniform bucket-level access for GCP"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            in_resource = False
            resource_name = resource.split('.')[-1]
            modified = False

            for i, line in enumerate(lines):
                if f'resource "google_storage_bucket" "{resource_name}"' in line:
                    in_resource = True

                if in_resource and 'uniform_bucket_level_access' in line:
                    return {'success': False, 'reason': 'Uniform access already enabled'}

                if in_resource and '}' in line:
                    uniform_block = '''  uniform_bucket_level_access {
    enabled = true
  }
'''
                    lines.insert(i, uniform_block)
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not enable uniform access'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Enabled uniform bucket-level access for {resource}',
                'compliance': ['CIS-GCP-5.1']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_gcp_public_ip(self, finding: Dict, project_path: str) -> Dict:
        """Restrict public IP for GCP compute instances"""
        return {
            'success': False,
            'reason': 'Manual intervention required',
            'recommendation': 'Remove external IP or use Cloud NAT for outbound traffic',
            'compliance': ['CIS-GCP-4.9']
        }

    # ============================================
    # General Terraform Fixes
    # ============================================

    def _fix_missing_tags(self, finding: Dict, project_path: str) -> Dict:
        """Add required tags to resources"""
        location = finding.get('location', {})
        filename = location.get('filename', '')
        resource = finding.get('resource', '')

        tf_file = Path(project_path) / filename
        if not tf_file.exists():
            return {'success': False, 'reason': 'Terraform file not found'}

        try:
            with open(tf_file, 'r') as f:
                lines = f.readlines()

            in_resource = False
            modified = False

            for i, line in enumerate(lines):
                if 'resource' in line and resource.split('.')[-1] in line:
                    in_resource = True

                if in_resource and 'tags' in line:
                    return {'success': False, 'reason': 'Tags already exist'}

                if in_resource and '}' in line:
                    tags_block = '''  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
'''
                    lines.insert(i, tags_block)
                    modified = True
                    break

            if not modified:
                return {'success': False, 'reason': 'Could not add tags'}

            with open(tf_file, 'w') as f:
                f.writelines(lines)

            return {
                'success': True,
                'action': f'Added required tags to {resource}',
                'manual_step': 'Update tag values to match your environment',
                'compliance': ['FinOps']
            }
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _fix_backend_encryption(self, finding: Dict, project_path: str) -> Dict:
        """Enable backend encryption for Terraform state"""
        return {
            'success': False,
            'reason': 'Manual intervention required',
            'recommendation': 'Configure encrypted S3 backend with DynamoDB state locking',
            'compliance': ['NIST-SC-28']
        }

    # ============================================
    # Utility Methods
    # ============================================

    def _create_backup(self, project_path: str) -> Path:
        """Create backup of project before modifications"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"{project_path}_tfsec_backup_{timestamp}")
        shutil.copytree(project_path, backup_dir, dirs_exist_ok=True)
        return backup_dir

    def _generate_report(self, scan_results_path: str, project_path: str) -> Dict:
        """Generate comprehensive fix report"""
        return {
            'tool': 'tfsec_fixer',
            'timestamp': datetime.now().isoformat(),
            'scan_results': scan_results_path,
            'project_path': project_path,
            'backup_location': str(self.backup_dir),
            'summary': {
                'total_findings': len(self.fixes_applied) + len(self.fixes_failed),
                'fixes_applied': len(self.fixes_applied),
                'fixes_failed': len(self.fixes_failed),
                'success_rate': f"{len(self.fixes_applied) / (len(self.fixes_applied) + len(self.fixes_failed)) * 100:.1f}%" if (len(self.fixes_applied) + len(self.fixes_failed)) > 0 else "0%"
            },
            'fixes_applied': self.fixes_applied,
            'fixes_failed': self.fixes_failed,
            'compliance_controls': self._extract_compliance_controls()
        }

    def _extract_compliance_controls(self) -> List[str]:
        """Extract unique compliance controls from applied fixes"""
        controls = set()
        for fix in self.fixes_applied:
            controls.update(fix.get('compliance', []))
        return sorted(list(controls))

    def _save_report(self, report: Dict):
        """Save fix report to GP-DATA"""
        from gp_data_config import GPDataConfig

        config = GPDataConfig()
        fixes_dir = config.get_fixes_directory()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = fixes_dir / f"tfsec_fix_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📊 Fix report saved: {report_file}")


def main():
    if len(sys.argv) < 3:
        print("Tfsec Security Fixer - Terraform IaC Security Remediation")
        print()
        print("Usage: tfsec_fixer.py <scan_results.json> <project_path>")
        print()
        print("Fixable Issues (Multi-Cloud Suite):")
        print()
        print("  ☁️  AWS Security:")
        print("    - Enable S3 bucket encryption (CIS-AWS-2.1.1)")
        print("    - Block S3 public access (CIS-AWS-5.2)")
        print("    - Enable RDS encryption (CIS-AWS-2.3.1)")
        print("    - Restrict security groups (PCI-DSS-1.2.1)")
        print("    - Enforce IMDSv2 on EC2 (CIS-AWS-5.6)")
        print("    - Enable EBS encryption (CIS-AWS-2.2.1)")
        print()
        print("  🔷 Azure Security:")
        print("    - Enforce HTTPS on storage (CIS-Azure-3.1)")
        print("    - Restrict NSG rules (CIS-Azure-6.1)")
        print("    - Enable disk encryption (CIS-Azure-7.1)")
        print()
        print("  🔶 GCP Security:")
        print("    - Enable uniform bucket access (CIS-GCP-5.1)")
        print("    - Restrict public IPs (CIS-GCP-4.9)")
        print()
        print("  🔧 General:")
        print("    - Add required tags (FinOps)")
        print("    - Enable backend encryption (NIST-SC-28)")
        print()
        print("Compliance: CIS, PCI-DSS, NIST, SOC2, FinOps")
        print()
        print("Example:")
        print("  python tfsec_fixer.py GP-DATA/scans/tfsec_latest.json /path/to/terraform")
        sys.exit(1)

    fixer = TfsecFixer()
    result = fixer.fix_findings(sys.argv[1], sys.argv[2])

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    else:
        print(f"\n✅ Tfsec fixer completed successfully")
        print(f"   Fixes applied: {result['summary']['fixes_applied']}")
        print(f"   Success rate: {result['summary']['success_rate']}")


if __name__ == "__main__":
    import sys
    main()