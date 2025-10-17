#!/usr/bin/env python3
"""
Production-Grade Checkov Scanner - IaC Policy-as-Code
======================================================
Stage: CD (Continuous Deployment)
Purpose: Terraform/CloudFormation/Kubernetes security scanning with compliance mapping
Inherits: SecurityScanner base class

Features:
- Terraform security checks
- Kubernetes manifest validation
- Compliance framework mapping (PCI-DSS, HIPAA, ISO27001, SOC2)
- Passed vs Failed checks tracking
- Guideline URLs for remediation

Usage:
    # Scan Terraform directory
    python3 checkov_scanner.py --target /path/to/terraform

    # Scan Kubernetes manifests
    python3 checkov_scanner.py --target /path/to/k8s --framework kubernetes
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add shared library to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared-library' / 'base-classes'))

from base_scanner import SecurityScanner


class CheckovScanner(SecurityScanner):
    """
    Checkov Scanner for Infrastructure-as-Code Security

    Policy-as-code scanning for:
    - Terraform (AWS, Azure, GCP)
    - CloudFormation
    - Kubernetes manifests
    - Dockerfiles
    - Helm charts
    - ARM templates

    Compliance frameworks:
    - PCI-DSS (Payment Card Industry)
    - HIPAA (Healthcare)
    - ISO27001 (Information Security)
    - SOC2 (Service Organization Control)
    - NIST (National Institute of Standards)
    - CIS (Center for Internet Security)
    """

    # Common compliance framework mappings
    COMPLIANCE_FRAMEWORKS = {
        'PCI-DSS': 'Payment Card Industry Data Security Standard',
        'HIPAA': 'Health Insurance Portability and Accountability Act',
        'ISO27001': 'Information Security Management',
        'SOC2': 'Service Organization Control 2',
        'NIST': 'National Institute of Standards and Technology',
        'CIS': 'Center for Internet Security'
    }

    def __init__(
        self,
        scan_target: Path = None,
        output_dir: Path = None,
        timeout: int = 600,
        framework: str = "terraform"
    ):
        """
        Initialize Checkov scanner

        Args:
            scan_target: IaC directory to scan
            output_dir: Where to save findings
            timeout: Scan timeout in seconds (default: 600 = 10 minutes)
            framework: IaC framework (terraform, kubernetes, cloudformation, etc.)
        """
        # Set defaults
        if scan_target is None:
            scan_target = Path(__file__).parent.parent.parent.parent / 'infrastructure' / 'terraform'

        if output_dir is None:
            # Use absolute path to GP-DATA (go up 4 levels from scanner to GP-copilot root)
            gp_root = Path(__file__).parent.parent.parent.parent
            output_dir = gp_root / 'GP-DATA' / 'active' / '1-sec-assessment' / 'cd-findings'

        super().__init__(scan_target, output_dir, timeout)

        self.framework = framework

    def get_scanner_name(self) -> str:
        """Return scanner name"""
        return 'checkov'

    def get_tool_name(self) -> str:
        """Return CLI tool name"""
        return 'checkov'

    def get_install_instructions(self) -> str:
        """Return installation instructions"""
        return 'pip install checkov'

    def get_output_filename(self) -> str:
        """Return output filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'checkov_{timestamp}.json'

    def build_command(self, output_file: str) -> List[str]:
        """
        Build Checkov command

        Args:
            output_file: Path to save raw Checkov JSON output (not used by Checkov, captured from STDOUT)

        Returns:
            Command list ready for subprocess.run()

        Note: Checkov outputs to STDOUT, not to a file. The base_scanner.py
              will capture STDOUT and we'll save it in parse_results().
        """
        return [
            'checkov',
            '-d', str(self.scan_target),
            '--framework', self.framework,
            '--output', 'json',
            '--download-external-modules', 'false',
            '--quiet',
            '--compact'
        ]

    def parse_results(self, output_file: Path) -> Dict:
        """
        Parse Checkov JSON output

        Checkov Output Structure:
        {
            "summary": {
                "passed": 45,
                "failed": 12,
                "skipped": 3,
                "parsing_errors": 0,
                "resource_count": 60
            },
            "results": {
                "failed_checks": [
                    {
                        "check_id": "CKV_AWS_157",
                        "check_name": "Ensure RDS database has encryption enabled",
                        "check_result": {"result": "failed"},
                        "file_path": "/infrastructure/terraform/rds.tf",
                        "file_line_range": [15, 25],
                        "resource": "aws_db_instance.main",
                        "guideline": "https://docs.bridgecrew.io/...",
                        "check_class": "checkov.terraform.checks.resource.aws.RDSEncryption",
                        "severity": "HIGH"
                    }
                ],
                "passed_checks": [...],
                "skipped_checks": [...]
            }
        }
        """
        try:
            with open(output_file, 'r') as f:
                checkov_output = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to parse Checkov output: {e}")
            return {
                'findings': [],
                'metadata': {
                    'scanner': self.get_scanner_name(),
                    'scan_time': datetime.now().isoformat(),
                    'target': str(self.scan_target),
                    'error': str(e)
                }
            }

        # Extract summary
        summary = checkov_output.get('summary', {})
        results = checkov_output.get('results', {})

        # Only process failed checks (findings)
        failed_checks = results.get('failed_checks', [])

        # Build enriched findings
        findings = []
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        # Track compliance frameworks
        compliance_frameworks = {}
        check_categories = {}

        for check in failed_checks:
            check_id = check.get('check_id', 'UNKNOWN')
            check_name = check.get('check_name', '')
            file_path = check.get('file_path', '')
            line_range = check.get('file_line_range', [0, 0])
            resource = check.get('resource', '')
            guideline = check.get('guideline', '')

            # Get severity (default to MEDIUM if not provided)
            # Checkov often returns None for severity
            severity = check.get('severity') or 'MEDIUM'
            severity = severity.upper()
            if severity not in severity_breakdown:
                severity = 'MEDIUM'

            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

            # Extract compliance frameworks from check_id or metadata
            # Checkov check IDs often contain framework hints
            frameworks = self._extract_compliance_frameworks(check)
            for fw in frameworks:
                compliance_frameworks[fw] = compliance_frameworks.get(fw, 0) + 1

            # Categorize by check type
            category = self._categorize_check(check_id, check_name)
            check_categories[category] = check_categories.get(category, 0) + 1

            # Build finding
            finding = {
                'id': f'checkov_{len(findings) + 1}',
                'scanner': self.get_scanner_name(),

                # Check details
                'check_id': check_id,
                'check_name': check_name,
                'title': check_name,

                # Severity
                'severity': severity,

                # Location
                'file': file_path,
                'line': line_range[0] if line_range else 0,
                'end_line': line_range[1] if len(line_range) > 1 else line_range[0] if line_range else 0,

                # Resource
                'resource': resource,
                'resource_type': resource.split('.')[0] if '.' in resource else resource,

                # Remediation
                'guideline': guideline,

                # Compliance
                'compliance_frameworks': frameworks,
                'category': category,

                # Metadata
                'scan_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),

                # Original data
                '_original': check
            }

            findings.append(finding)

        # Build metadata
        metadata = {
            'scanner': self.get_scanner_name(),
            'scan_timestamp': datetime.now().isoformat(),
            'target': str(self.scan_target),
            'framework': self.framework,
            'issue_count': len(findings),
            'severity_breakdown': severity_breakdown,

            # Checkov-specific metrics
            'checkov_summary': {
                'total_checks': summary.get('passed', 0) + summary.get('failed', 0) + summary.get('skipped', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'resource_count': summary.get('resource_count', 0),
                'pass_rate': round((summary.get('passed', 0) / max(summary.get('passed', 0) + summary.get('failed', 0), 1)) * 100, 1),
                'compliance_frameworks': compliance_frameworks,
                'check_categories': check_categories
            }
        }

        return {
            'findings': findings,
            'metadata': metadata
        }

    def _extract_compliance_frameworks(self, check: Dict) -> List[str]:
        """
        Extract compliance frameworks from check metadata

        Args:
            check: Checkov check data

        Returns:
            List of compliance frameworks
        """
        frameworks = []

        # Check for compliance in check_id or metadata
        check_id = check.get('check_id', '')
        check_class = check.get('check_class', '')

        # Common patterns in Checkov check IDs
        if 'PCI' in check_id or 'PCI' in check_class:
            frameworks.append('PCI-DSS')
        if 'HIPAA' in check_id or 'HIPAA' in check_class:
            frameworks.append('HIPAA')
        if 'ISO' in check_id or 'ISO27001' in check_class:
            frameworks.append('ISO27001')
        if 'SOC2' in check_id or 'SOC2' in check_class:
            frameworks.append('SOC2')
        if 'NIST' in check_id or 'NIST' in check_class:
            frameworks.append('NIST')
        if 'CIS' in check_id or 'CIS' in check_class:
            frameworks.append('CIS')

        return frameworks

    def _categorize_check(self, check_id: str, check_name: str) -> str:
        """
        Categorize the check by type

        Args:
            check_id: Check ID
            check_name: Check name

        Returns:
            Category string
        """
        check_lower = (check_id + check_name).lower()

        if 'encrypt' in check_lower or 'kms' in check_lower:
            return 'Encryption'
        elif 'iam' in check_lower or 'access' in check_lower or 'permission' in check_lower:
            return 'Access Control'
        elif 'network' in check_lower or 'security group' in check_lower or 'firewall' in check_lower:
            return 'Network Security'
        elif 'logging' in check_lower or 'monitoring' in check_lower:
            return 'Logging & Monitoring'
        elif 'backup' in check_lower or 'snapshot' in check_lower:
            return 'Backup & Recovery'
        elif 'public' in check_lower or 'exposed' in check_lower:
            return 'Exposure & Access'
        else:
            return 'Security Configuration'


def main():
    """
    Main entry point for standalone execution

    Usage:
        python3 checkov_scanner.py --target /path/to/terraform
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Checkov Scanner - IaC Policy-as-Code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan Terraform directory
  python3 checkov_scanner.py --target /path/to/terraform

  # Scan Kubernetes manifests
  python3 checkov_scanner.py --target /path/to/k8s --framework kubernetes

  # Scan with custom timeout
  python3 checkov_scanner.py --target /path/to/iac --timeout 900

  # Scan infrastructure directory
  python3 checkov_scanner.py --target ../../infrastructure/terraform/
        """
    )

    parser.add_argument(
        '--target',
        default=None,
        help='IaC directory to scan (default: infrastructure/terraform/)'
    )

    parser.add_argument(
        '--framework',
        default='terraform',
        choices=['terraform', 'kubernetes', 'cloudformation', 'dockerfile', 'helm'],
        help='IaC framework to scan (default: terraform)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='Scan timeout in seconds (default: 600 = 10 minutes)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for findings (default: secops/2-findings/raw/cd/)'
    )

    args = parser.parse_args()

    # Convert paths
    target = Path(args.target) if args.target else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    # Create scanner
    scanner = CheckovScanner(
        scan_target=target,
        output_dir=output_dir,
        timeout=args.timeout,
        framework=args.framework
    )

    # Run scan
    success = scanner.run_scan()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
