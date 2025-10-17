#!/usr/bin/env python3
"""
Production-Grade Trivy Scanner - Dual Mode
===========================================
Stage: CD (Continuous Deployment)
Purpose: Container vulnerability scanning + IaC misconfiguration detection
Inherits: SecurityScanner base class

Modes:
1. IMAGE mode: Scan Docker container images for CVEs
2. CONFIG mode: Scan infrastructure-as-code for misconfigurations

Features:
- Dual-mode operation (container + IaC)
- CVE parsing with CVSS scores
- Fixable vs unfixable vulnerability tracking
- IaC misconfiguration detection
- Docker daemon health checks
- Comprehensive error handling

Usage:
    # Scan container image
    python3 trivy_scanner.py --mode image --target nginx:latest

    # Scan IaC (Terraform)
    python3 trivy_scanner.py --mode config --target ../../infrastructure/terraform/

    # Scan both
    python3 trivy_scanner.py --mode both --target nginx:latest --iac-target ../../infrastructure/
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add shared library to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared-library' / 'base-classes'))

from base_scanner import SecurityScanner


class TrivyScanner(SecurityScanner):
    """
    Trivy Scanner for Container Images and IaC

    Supports two scanning modes:
    1. Image: Scan Docker images for CVEs in packages
    2. Config: Scan IaC files (Terraform, K8s, Dockerfile) for misconfigurations
    """

    def __init__(
        self,
        scan_target: Path = None,
        output_dir: Path = None,
        timeout: int = 600,
        scan_mode: str = "config"
    ):
        """
        Initialize Trivy scanner

        Args:
            scan_target: Docker image name OR IaC directory path
            output_dir: Where to save findings
            timeout: Scan timeout in seconds (default: 600 = 10 minutes for large images)
            scan_mode: 'image' or 'config' (default: 'config')
        """
        # Set scan_mode FIRST (needed by get_scanner_name())
        self.scan_mode = scan_mode

        # Set defaults
        if scan_target is None:
            if scan_mode == "image":
                scan_target = "nginx:latest"  # Default test image
            else:
                scan_target = Path(__file__).parent.parent.parent.parent / 'infrastructure' / 'terraform'

        if output_dir is None:
            # Use absolute path to GP-DATA (go up 4 levels from scanner to GP-copilot root)
            gp_root = Path(__file__).parent.parent.parent.parent
            output_dir = gp_root / 'GP-DATA' / 'active' / '1-sec-assessment' / 'cd-findings'

        super().__init__(scan_target, output_dir, timeout)

        self.metrics['scan_mode'] = scan_mode

    def get_scanner_name(self) -> str:
        """Return scanner name"""
        return f'trivy-{self.scan_mode}'

    def get_tool_name(self) -> str:
        """Return CLI tool name"""
        return 'trivy'

    def get_install_instructions(self) -> str:
        """Return installation instructions"""
        return (
            "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | "
            "sh -s -- -b /usr/local/bin"
        )

    def get_output_filename(self) -> str:
        """Return output filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'trivy_{self.scan_mode}_{timestamp}.json'

    def validate_prerequisites(self) -> bool:
        """Check if Trivy and Docker (if needed) are installed"""
        # Check Trivy
        if not super().validate_prerequisites():
            return False

        # If image mode, check Docker daemon
        if self.scan_mode == "image":
            try:
                result = subprocess.run(
                    ['docker', 'info'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode != 0:
                    self.logger.error("Docker daemon is not running")
                    self.logger.info("Start Docker with: sudo systemctl start docker")
                    return False

                self.logger.debug("Docker daemon is running")

            except FileNotFoundError:
                self.logger.error("Docker not found in PATH")
                self.logger.info("Install Docker: https://docs.docker.com/engine/install/")
                return False

            except subprocess.TimeoutExpired:
                self.logger.error("Docker daemon check timed out")
                return False

        return True

    def build_command(self, output_file: str) -> List[str]:
        """
        Build Trivy command based on scan mode

        Args:
            output_file: Path to save raw Trivy JSON output

        Returns:
            Command list ready for subprocess.run()
        """
        base_cmd = [
            'trivy',
            self.scan_mode,  # 'image' or 'config'
            '--format', 'json',
            '--output', output_file,
            '--severity', 'CRITICAL,HIGH,MEDIUM,LOW',
            '--timeout', f'{self.timeout}s'
        ]

        # Mode-specific options
        if self.scan_mode == "image":
            # Image scanning options (--scanners not available in Trivy v0.48.0)
            base_cmd.extend([
                '--vuln-type', 'os,library',  # Scan OS packages and libraries
                str(self.scan_target)          # Image name
            ])

        elif self.scan_mode == "config":
            # Config scanning options (--scanners not available in older Trivy versions)
            base_cmd.extend([
                '--skip-dirs', 'node_modules,.venv,venv,.git',
                str(self.scan_target)  # Directory path
            ])

        return base_cmd

    def parse_results(self, output_file: Path) -> Dict:
        """
        Parse Trivy JSON output

        Trivy Output Structure:
        {
            "Results": [
                {
                    "Target": "nginx:latest (alpine 3.18.4)",
                    "Class": "os-pkgs",
                    "Type": "alpine",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2023-12345",
                            "PkgName": "openssl",
                            "InstalledVersion": "3.1.0-r4",
                            "FixedVersion": "3.1.4-r0",
                            "Severity": "HIGH",
                            "Title": "OpenSSL vulnerability",
                            "Description": "...",
                            "PrimaryURL": "https://avd.aquasec.com/nvd/cve-2023-12345",
                            "CVSS": {
                                "nvd": {
                                    "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                                    "V3Score": 7.5
                                }
                            }
                        }
                    ],
                    "Misconfigurations": [
                        {
                            "Type": "Terraform Security Check",
                            "ID": "AVD-AWS-0001",
                            "AVDID": "AVD-AWS-0001",
                            "Title": "S3 bucket is publicly accessible",
                            "Severity": "HIGH",
                            "Message": "Bucket does not have block public access",
                            "Resolution": "Set block_public_acls = true",
                            "CauseMetadata": {
                                "Provider": "AWS",
                                "Service": "s3",
                                "StartLine": 15,
                                "EndLine": 20
                            }
                        }
                    ]
                }
            ]
        }
        """
        try:
            with open(output_file, 'r') as f:
                trivy_output = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to parse Trivy output: {e}")
            return {
                'findings': [],
                'metadata': {
                    'scanner': self.get_scanner_name(),
                    'scan_mode': self.scan_mode,
                    'scan_time': datetime.now().isoformat(),
                    'target': str(self.scan_target),
                    'error': str(e)
                }
            }

        results = trivy_output.get('Results', [])

        # Parse based on mode
        if self.scan_mode == "image":
            return self._parse_image_results(results)
        elif self.scan_mode == "config":
            return self._parse_config_results(results)
        else:
            self.logger.error(f"Unknown scan mode: {self.scan_mode}")
            return {'findings': [], 'metadata': {}}

    def _parse_image_results(self, results: List[Dict]) -> Dict:
        """Parse container image vulnerability results"""
        findings = []
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        # Vulnerability tracking
        total_cves = 0
        fixable_cves = 0
        unfixable_cves = 0
        packages_affected = set()

        for result in results:
            target = result.get('Target', '')
            vulnerabilities = result.get('Vulnerabilities') or []

            for idx, vuln in enumerate(vulnerabilities, 1):
                cve_id = vuln.get('VulnerabilityID', 'UNKNOWN')
                pkg_name = vuln.get('PkgName', 'unknown')
                installed_ver = vuln.get('InstalledVersion', '')
                fixed_ver = vuln.get('FixedVersion', '')
                severity = vuln.get('Severity', 'UNKNOWN').upper()

                # Check if fixable
                fixable = bool(fixed_ver and fixed_ver.strip())

                if fixable:
                    fixable_cves += 1
                else:
                    unfixable_cves += 1

                total_cves += 1
                packages_affected.add(pkg_name)
                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

                # Get CVSS score
                cvss_score = None
                cvss = vuln.get('CVSS', {})
                if cvss:
                    nvd = cvss.get('nvd', {})
                    cvss_score = nvd.get('V3Score') or nvd.get('V2Score')

                # Build finding
                finding = {
                    'id': f'trivy_vuln_{len(findings) + 1}',
                    'type': 'vulnerability',
                    'scanner': self.get_scanner_name(),

                    # CVE details
                    'cve': cve_id,
                    'package': pkg_name,
                    'installed_version': installed_ver,
                    'fixed_version': fixed_ver,
                    'fixable': fixable,

                    # Severity
                    'severity': severity,
                    'cvss_score': cvss_score,

                    # Description
                    'title': vuln.get('Title', ''),
                    'description': vuln.get('Description', '')[:500],  # Truncate long descriptions

                    # References
                    'url': vuln.get('PrimaryURL', ''),
                    'references': vuln.get('References', [])[:5],  # Limit references

                    # Target info
                    'target': target,

                    # Metadata
                    'scan_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),

                    # Original data
                    '_original': vuln
                }

                findings.append(finding)

        # Build metadata
        metadata = {
            'scanner': self.get_scanner_name(),
            'scan_mode': 'image',
            'scan_timestamp': datetime.now().isoformat(),
            'target': str(self.scan_target),
            'issue_count': len(findings),
            'severity_breakdown': severity_breakdown,

            # Vulnerability-specific metrics
            'vulnerability_summary': {
                'total_cves': total_cves,
                'fixable_cves': fixable_cves,
                'unfixable_cves': unfixable_cves,
                'packages_affected': len(packages_affected),
                'fixable_percentage': round((fixable_cves / total_cves * 100) if total_cves > 0 else 0, 1)
            }
        }

        return {
            'findings': findings,
            'metadata': metadata
        }

    def _parse_config_results(self, results: List[Dict]) -> Dict:
        """Parse IaC misconfiguration results"""
        findings = []
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        # Misconfiguration tracking
        by_type = {}
        by_service = {}

        for result in results:
            target = result.get('Target', '')
            misconfigs = result.get('Misconfigurations') or []

            for misconfig in misconfigs:
                check_id = misconfig.get('ID', 'UNKNOWN')
                severity = misconfig.get('Severity', 'UNKNOWN').upper()

                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

                # Get metadata
                cause_meta = misconfig.get('CauseMetadata', {})
                provider = cause_meta.get('Provider', 'Unknown')
                service = cause_meta.get('Service', 'Unknown')
                start_line = cause_meta.get('StartLine', 0)

                # Track by type and service
                check_type = misconfig.get('Type', 'Unknown')
                by_type[check_type] = by_type.get(check_type, 0) + 1
                by_service[service] = by_service.get(service, 0) + 1

                # Build finding
                finding = {
                    'id': f'trivy_misconfig_{len(findings) + 1}',
                    'type': 'misconfiguration',
                    'scanner': self.get_scanner_name(),

                    # Check details
                    'check_id': check_id,
                    'check_type': check_type,
                    'title': misconfig.get('Title', ''),
                    'severity': severity,

                    # Location
                    'file': target,
                    'line': start_line,
                    'end_line': cause_meta.get('EndLine', start_line),

                    # Issue details
                    'message': misconfig.get('Message', ''),
                    'description': misconfig.get('Description', '')[:500],
                    'remediation': misconfig.get('Resolution', ''),

                    # Classification
                    'provider': provider,
                    'service': service,

                    # References
                    'references': misconfig.get('References', [])[:5],

                    # Metadata
                    'scan_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),

                    # Original data
                    '_original': misconfig
                }

                findings.append(finding)

        # Build metadata
        metadata = {
            'scanner': self.get_scanner_name(),
            'scan_mode': 'config',
            'scan_timestamp': datetime.now().isoformat(),
            'target': str(self.scan_target),
            'issue_count': len(findings),
            'severity_breakdown': severity_breakdown,

            # Misconfiguration-specific metrics
            'misconfiguration_summary': {
                'total_checks': len(findings),
                'by_type': by_type,
                'by_service': by_service,
                'unique_files': len(set(f['file'] for f in findings))
            }
        }

        return {
            'findings': findings,
            'metadata': metadata
        }


def main():
    """
    Main entry point for standalone execution

    Usage:
        # Image mode
        python3 trivy_scanner.py --mode image --target nginx:latest

        # Config mode
        python3 trivy_scanner.py --mode config --target ../../infrastructure/terraform/
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Trivy Scanner - Container + IaC Security',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan container image for CVEs
  python3 trivy_scanner.py --mode image --target nginx:latest
  python3 trivy_scanner.py --mode image --target securebank-backend:latest

  # Scan IaC for misconfigurations
  python3 trivy_scanner.py --mode config --target ../../infrastructure/terraform/
  python3 trivy_scanner.py --mode config --target ../../infrastructure/k8s/

  # Custom timeout (20 minutes for large images)
  python3 trivy_scanner.py --mode image --target large-image:latest --timeout 1200
        """
    )

    parser.add_argument(
        '--mode',
        choices=['image', 'config'],
        default='config',
        help='Scan mode: image (container CVEs) or config (IaC misconfigs)'
    )

    parser.add_argument(
        '--target',
        required=True,
        help='Target: Docker image name (for image mode) or directory path (for config mode)'
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
    if args.mode == "config":
        target = Path(args.target)
    else:
        target = args.target  # Image name is a string

    output_dir = Path(args.output_dir) if args.output_dir else None

    # Create scanner
    scanner = TrivyScanner(
        scan_target=target,
        output_dir=output_dir,
        timeout=args.timeout,
        scan_mode=args.mode
    )

    # Run scan
    success = scanner.run_scan()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
