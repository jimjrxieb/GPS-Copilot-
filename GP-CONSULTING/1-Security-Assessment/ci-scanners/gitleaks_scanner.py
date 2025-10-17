#!/usr/bin/env python3
"""
Production-Grade Gitleaks Scanner - Secrets Detection
======================================================
Stage: CI (Continuous Integration)
Purpose: Detect hardcoded secrets in code and git history
Inherits: SecurityScanner base class

Features:
- Scans entire git history + current files
- Detects AWS keys, GitHub tokens, private keys, API keys, etc.
- Masks secret values in output (security)
- All findings marked as CRITICAL (CWE-798)
- Fast and accurate secret detection

Usage:
    # Scan current directory (git repo)
    python3 gitleaks_scanner.py --target /path/to/repo

    # Scan without git history (faster)
    python3 gitleaks_scanner.py --target /path/to/repo --no-git
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add shared library to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared-library' / 'base-classes'))

from base_scanner import SecurityScanner


class GitleaksScanner(SecurityScanner):
    """
    Gitleaks Scanner for Secret Detection

    Detects hardcoded secrets:
    - AWS Access Keys (AKIA...)
    - AWS Secret Keys
    - GitHub Personal Access Tokens
    - GitHub Fine-Grained Tokens
    - Slack Webhooks
    - Private Keys (RSA, SSH, etc.)
    - Database Passwords
    - Generic API Keys
    - JWT Tokens
    - OAuth Tokens
    """

    # Secret type to CWE mapping (all secrets are CWE-798)
    SECRET_CWE = 'CWE-798'  # Use of Hard-coded Credentials

    def __init__(
        self,
        scan_target: Path = None,
        output_dir: Path = None,
        timeout: int = 300,
        no_git: bool = False
    ):
        """
        Initialize Gitleaks scanner

        Args:
            scan_target: Git repository root (defaults to project root)
            output_dir: Where to save findings
            timeout: Scan timeout in seconds (default: 300 = 5 minutes)
            no_git: Skip git history scan (faster, only scan current files)
        """
        # Set defaults
        if scan_target is None:
            scan_target = Path(__file__).parent.parent.parent.parent  # Project root

        if output_dir is None:
            # Use absolute path to GP-DATA (go up 4 levels from scanner to GP-copilot root)
            gp_root = Path(__file__).parent.parent.parent.parent
            output_dir = gp_root / 'GP-DATA' / 'active' / '1-sec-assessment' / 'ci-findings'

        super().__init__(scan_target, output_dir, timeout)

        self.no_git = no_git

    def get_scanner_name(self) -> str:
        """Return scanner name"""
        return 'gitleaks'

    def get_tool_name(self) -> str:
        """Return CLI tool name"""
        return 'gitleaks'

    def get_install_instructions(self) -> str:
        """Return installation instructions"""
        return (
            "Download from: https://github.com/gitleaks/gitleaks/releases\n"
            "Or install via: brew install gitleaks (macOS)\n"
            "Or use binary in: GP-TOOLS/binaries/gitleaks"
        )

    def get_output_filename(self) -> str:
        """Return output filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'gitleaks_{timestamp}.json'

    def build_command(self, output_file: str) -> List[str]:
        """
        Build Gitleaks command

        Args:
            output_file: Path to save raw Gitleaks JSON output

        Returns:
            Command list ready for subprocess.run()
        """
        cmd = [
            'gitleaks',
            'detect',
            '--source', str(self.scan_target),
            '--report-format', 'json',
            '--report-path', output_file,
            '--verbose',
            '--exit-code', '0'  # Don't fail on findings (we handle that)
        ]

        # Skip git history if requested (faster)
        if self.no_git:
            cmd.append('--no-git')

        return cmd

    def parse_results(self, output_file: Path) -> Dict:
        """
        Parse Gitleaks JSON output

        Gitleaks Output Structure:
        [
            {
                "Description": "AWS Access Token",
                "StartLine": 42,
                "EndLine": 42,
                "StartColumn": 15,
                "EndColumn": 35,
                "Match": "AKIA...",
                "Secret": "AKIAIOSFODNN7EXAMPLE",
                "File": "backend/config.py",
                "SymlinkFile": "",
                "Commit": "abc123def456...",
                "Entropy": 3.5,
                "Author": "developer@example.com",
                "Email": "developer@example.com",
                "Date": "2023-01-15T10:30:00Z",
                "Message": "Add AWS config",
                "Tags": [],
                "RuleID": "aws-access-token",
                "Fingerprint": "abc123..."
            }
        ]
        """
        try:
            with open(output_file, 'r') as f:
                gitleaks_output = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to parse Gitleaks output: {e}")
            return {
                'findings': [],
                'metadata': {
                    'scanner': self.get_scanner_name(),
                    'scan_time': datetime.now().isoformat(),
                    'target': str(self.scan_target),
                    'error': str(e)
                }
            }

        # Gitleaks returns an array directly
        if not isinstance(gitleaks_output, list):
            gitleaks_output = []

        # Build enriched findings
        findings = []
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        # Track secret types
        secret_types = {}
        files_with_secrets = set()

        for leak in gitleaks_output:
            rule_id = leak.get('RuleID', 'unknown')
            description = leak.get('Description', 'Secret detected')
            file_path = leak.get('File', '')
            line_num = leak.get('StartLine', 0)
            secret_value = leak.get('Secret', '')

            # ALL secrets are CRITICAL
            severity_breakdown['CRITICAL'] += 1

            # Track secret type
            secret_types[rule_id] = secret_types.get(rule_id, 0) + 1
            files_with_secrets.add(file_path)

            # Mask the secret (show first 4 and last 4 chars only)
            masked_secret = self._mask_secret(secret_value)

            # Build finding
            finding = {
                'id': f'gitleaks_{len(findings) + 1}',
                'scanner': self.get_scanner_name(),

                # Secret details
                'secret_type': rule_id,
                'description': description,
                'title': f"{description} detected",

                # Severity (ALL CRITICAL)
                'severity': 'CRITICAL',
                'cwe': [self.SECRET_CWE],

                # Location
                'file': file_path,
                'line': line_num,
                'column': leak.get('StartColumn', 0),
                'end_line': leak.get('EndLine', line_num),

                # Secret info (MASKED)
                'secret_masked': masked_secret,
                'match': leak.get('Match', '')[:50],  # Truncate long matches

                # Git info (if available)
                'commit': leak.get('Commit', '')[:8],  # Short commit hash
                'author': leak.get('Author', ''),
                'date': leak.get('Date', ''),

                # Entropy (confidence indicator)
                'entropy': leak.get('Entropy', 0),

                # Metadata
                'scan_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),

                # Original data (with secret REMOVED for security)
                '_original': {k: v for k, v in leak.items() if k != 'Secret'}
            }

            findings.append(finding)

        # Build metadata
        metadata = {
            'scanner': self.get_scanner_name(),
            'scan_timestamp': datetime.now().isoformat(),
            'target': str(self.scan_target),
            'no_git': self.no_git,
            'issue_count': len(findings),
            'severity_breakdown': severity_breakdown,

            # Gitleaks-specific metrics
            'secrets_summary': {
                'total_secrets': len(findings),
                'unique_secret_types': len(secret_types),
                'files_with_secrets': len(files_with_secrets),
                'by_type': secret_types
            }
        }

        return {
            'findings': findings,
            'metadata': metadata
        }

    def _mask_secret(self, secret: str) -> str:
        """
        Mask secret value for security

        Shows first 4 and last 4 characters, masks the rest

        Args:
            secret: The secret value

        Returns:
            Masked secret (e.g., "AKIA****EXAMPLE")
        """
        if not secret:
            return ''

        if len(secret) <= 8:
            return '*' * len(secret)

        return f"{secret[:4]}{'*' * (len(secret) - 8)}{secret[-4:]}"


def main():
    """
    Main entry point for standalone execution

    Usage:
        python3 gitleaks_scanner.py --target /path/to/repo
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Gitleaks Scanner - Secrets Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan git repository (includes history)
  python3 gitleaks_scanner.py --target /path/to/repo

  # Scan without git history (faster)
  python3 gitleaks_scanner.py --target /path/to/repo --no-git

  # Scan current project
  python3 gitleaks_scanner.py --target ../../../

  # Scan backend only
  python3 gitleaks_scanner.py --target ../../backend/
        """
    )

    parser.add_argument(
        '--target',
        default=None,
        help='Git repository root to scan (default: project root)'
    )

    parser.add_argument(
        '--no-git',
        action='store_true',
        help='Skip git history scan (faster, only scan current files)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Scan timeout in seconds (default: 300 = 5 minutes)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for findings (default: secops/2-findings/raw/ci/)'
    )

    args = parser.parse_args()

    # Convert paths
    target = Path(args.target) if args.target else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    # Create scanner
    scanner = GitleaksScanner(
        scan_target=target,
        output_dir=output_dir,
        timeout=args.timeout,
        no_git=args.no_git
    )

    # Run scan
    success = scanner.run_scan()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
