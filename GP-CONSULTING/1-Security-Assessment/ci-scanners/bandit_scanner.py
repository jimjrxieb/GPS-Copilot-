#!/usr/bin/env python3
"""
Production-Grade Bandit Scanner
================================
Stage: CI (Continuous Integration)
Purpose: Python SAST - detect security issues in Python code
Inherits: SecurityScanner base class

Features:
- Automatic retry with exponential backoff
- Timeout protection (5 minutes)
- Comprehensive CWE mapping
- Finding enrichment with file hashes
- Structured output with metrics
- Handles missing tool gracefully
- Non-zero exit codes handled (Bandit returns 1 when issues found)

Usage:
    python3 bandit_scanner.py /path/to/python/code
    python3 bandit_scanner.py ../../backend/app/
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add shared library to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared-library' / 'base-classes'))

from base_scanner import SecurityScanner, CWE_MAPPINGS


class BanditScanner(SecurityScanner):
    """
    Bandit SAST Scanner for Python code

    Detects common security issues in Python code:
    - SQL injection
    - Hardcoded passwords/secrets
    - Insecure cryptography
    - Command injection
    - Unsafe deserialization
    - And more...
    """

    # Comprehensive CWE mapping for Bandit test IDs
    BANDIT_CWE_MAP = {
        # Injection Vulnerabilities
        'B201': ['CWE-78'],   # Flask app.run(debug=True)
        'B601': ['CWE-78'],   # paramiko_calls
        'B602': ['CWE-78'],   # subprocess_popen_with_shell_equals_true
        'B603': ['CWE-78'],   # subprocess_without_shell_equals_true
        'B604': ['CWE-78'],   # any_other_function_with_shell_equals_true
        'B605': ['CWE-78'],   # start_process_with_a_shell
        'B606': ['CWE-78'],   # start_process_with_no_shell
        'B607': ['CWE-78'],   # start_process_with_partial_path
        'B608': ['CWE-89'],   # hardcoded_sql_expressions (SQL injection)
        'B609': ['CWE-22'],   # linux_commands_wildcard_injection
        'B610': ['CWE-89'],   # django_extra_used
        'B611': ['CWE-89'],   # django_rawsql_used

        # Secrets/Credentials
        'B105': ['CWE-798'],  # hardcoded_password_string
        'B106': ['CWE-798'],  # hardcoded_password_funcarg
        'B107': ['CWE-798'],  # hardcoded_password_default

        # Error Handling
        'B110': ['CWE-703'],  # try_except_pass
        'B112': ['CWE-703'],  # try_except_continue

        # Insecure Deserialization
        'B301': ['CWE-502'],  # pickle
        'B302': ['CWE-502'],  # marshal
        'B303': ['CWE-502'],  # md5 (moved to crypto)
        'B304': ['CWE-502'],  # ciphers (moved to crypto)
        'B305': ['CWE-502'],  # cipher_modes (moved to crypto)
        'B506': ['CWE-502'],  # yaml_load

        # Cryptography Issues
        'B303': ['CWE-327'],  # md5
        'B304': ['CWE-327'],  # insecure_hash (SHA1)
        'B305': ['CWE-327'],  # insecure_cipher_mode
        'B313': ['CWE-327'],  # blacklist_imports (Crypto.Cipher)
        'B314': ['CWE-327'],  # blacklist_imports (Crypto.Hash)
        'B315': ['CWE-327'],  # blacklist_imports (Crypto.Random)
        'B316': ['CWE-327'],  # blacklist_imports (Crypto.Util)
        'B317': ['CWE-327'],  # blacklist_imports (xml.sax)
        'B318': ['CWE-327'],  # blacklist_imports (xml.etree)
        'B319': ['CWE-327'],  # blacklist_imports (xml.minidom)
        'B320': ['CWE-327'],  # blacklist_imports (xml.dom.pulldom)
        'B321': ['CWE-330'],  # ftplib
        'B323': ['CWE-327'],  # unverified_context
        'B324': ['CWE-327'],  # hashlib_new_insecure_functions

        # File System Issues
        'B306': ['CWE-377'],  # mktemp_q
        'B307': ['CWE-78'],   # eval
        'B325': ['CWE-377'],  # tempnam

        # Input Validation
        'B308': ['CWE-20'],   # mark_safe
        'B309': ['CWE-78'],   # httpsconnection
        'B310': ['CWE-22'],   # urllib_urlopen

        # Weak Random
        'B311': ['CWE-330'],  # random

        # Command Injection
        'B312': ['CWE-78'],   # telnetlib

        # SSL/TLS Issues
        'B501': ['CWE-295'],  # request_with_no_cert_validation
        'B502': ['CWE-295'],  # ssl_with_bad_version
        'B503': ['CWE-295'],  # ssl_with_bad_defaults
        'B504': ['CWE-295'],  # ssl_with_no_version
        'B505': ['CWE-327'],  # weak_cryptographic_key
        'B507': ['CWE-295'],  # ssh_no_host_key_verification

        # Logging Injection
        'B701': ['CWE-117'],  # jinja2_autoescape_false
        'B702': ['CWE-93'],   # use_of_mako_templates
    }

    def __init__(self, scan_target: Path = None, output_dir: Path = None, timeout: int = 300):
        """
        Initialize Bandit scanner

        Args:
            scan_target: Directory to scan (defaults to project root)
            output_dir: Where to save findings (defaults to secops/2-findings/raw/ci)
            timeout: Scan timeout in seconds (default: 300 = 5 minutes)
        """
        # Set defaults if not provided
        if scan_target is None:
            scan_target = Path(__file__).parent.parent.parent.parent / 'backend'

        if output_dir is None:
            # Use absolute path to GP-DATA (go up 4 levels from scanner to GP-copilot root)
            gp_root = Path(__file__).parent.parent.parent.parent
            output_dir = gp_root / 'GP-DATA' / 'active' / '1-sec-assessment' / 'ci-findings'

        super().__init__(scan_target, output_dir, timeout)

    def get_scanner_name(self) -> str:
        """Return scanner name"""
        return 'bandit'

    def get_tool_name(self) -> str:
        """Return CLI tool name"""
        return 'bandit'

    def get_install_instructions(self) -> str:
        """Return installation instructions"""
        return 'pip install bandit'

    def get_output_filename(self) -> str:
        """Return output filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'bandit_{timestamp}.json'

    def build_command(self, output_file: str) -> List[str]:
        """
        Build Bandit command

        Args:
            output_file: Path to save raw Bandit JSON output

        Returns:
            Command list ready for subprocess.run()
        """
        return [
            'bandit',
            '-r', str(self.scan_target),  # Recursive scan
            '-f', 'json',                  # JSON output format
            '-o', output_file,             # Output file
            '-ll',                         # Only LOW severity and above (filters INFO)
            '--exclude', '*/venv/*,*/node_modules/*,*/.venv/*,*/tests/*,*/__pycache__/*,*/migrations/*'
        ]

    def parse_results(self, output_file: Path) -> Dict:
        """
        Parse Bandit JSON output and enrich findings

        Bandit Output Structure:
        {
            "results": [
                {
                    "code": "vulnerable code snippet",
                    "filename": "path/to/file.py",
                    "issue_confidence": "HIGH|MEDIUM|LOW",
                    "issue_severity": "HIGH|MEDIUM|LOW",
                    "issue_text": "Description of the issue",
                    "line_number": 42,
                    "test_id": "B608",
                    "test_name": "hardcoded_sql_expressions"
                }
            ],
            "metrics": {
                "_totals": {
                    "loc": 1234,
                    "nosec": 0
                }
            }
        }

        Returns:
            Standardized format with enriched findings
        """
        try:
            with open(output_file, 'r') as f:
                bandit_output = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to parse Bandit output: {e}")
            return {
                'findings': [],
                'metadata': {
                    'scanner': self.get_scanner_name(),
                    'scan_time': datetime.now().isoformat(),
                    'target': str(self.scan_target),
                    'error': str(e)
                }
            }

        # Extract raw results
        raw_results = bandit_output.get('results', [])
        bandit_metrics = bandit_output.get('metrics', {})

        # Build enriched findings
        findings = []
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        for idx, issue in enumerate(raw_results, 1):
            # Extract fields
            test_id = issue.get('test_id', 'UNKNOWN')
            severity = issue.get('issue_severity', 'MEDIUM').upper()
            confidence = issue.get('issue_confidence', 'MEDIUM').upper()
            file_path = issue.get('filename', '')
            line_number = issue.get('line_number', 0)

            # Treat HIGH severity + HIGH confidence as CRITICAL
            if severity == 'HIGH' and confidence == 'HIGH':
                effective_severity = 'CRITICAL'
            else:
                effective_severity = severity

            severity_breakdown[effective_severity] += 1

            # Get CWE mapping
            cwe_list = self.BANDIT_CWE_MAP.get(test_id, [])

            # Calculate file hash for tracking
            file_hash = self._calculate_file_hash(file_path)

            # Build enriched finding
            finding = {
                # Identifiers
                'id': f"bandit_{idx}",
                'scanner': self.get_scanner_name(),

                # Issue details
                'severity': effective_severity,
                'confidence': confidence,
                'title': issue.get('issue_text', ''),
                'description': issue.get('issue_text', ''),

                # Location
                'file': file_path,
                'line': line_number,
                'code': issue.get('code', '').strip(),

                # Classification
                'test_id': test_id,
                'test_name': issue.get('test_name', ''),
                'cwe': cwe_list,

                # Metadata
                'scan_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'file_hash': file_hash,

                # Original Bandit data (for reference)
                '_original': issue
            }

            findings.append(finding)

        # Extract metrics
        bandit_totals = bandit_metrics.get('_totals', {})

        # Build metadata
        metadata = {
            'scanner': self.get_scanner_name(),
            'scan_timestamp': datetime.now().isoformat(),
            'target': str(self.scan_target),
            'issue_count': len(findings),
            'severity_breakdown': severity_breakdown,
            'metrics': {
                'files_scanned': len(bandit_output.get('metrics', {}).keys()) - 1,  # Subtract _totals
                'lines_of_code': bandit_totals.get('loc', 0),
                'nosec_comments': bandit_totals.get('nosec', 0),
            }
        }

        return {
            'findings': findings,
            'metadata': metadata
        }

    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file for tracking changes

        Args:
            file_path: Path to file

        Returns:
            SHA256 hex digest or 'N/A' if file not found
        """
        try:
            absolute_path = Path(file_path)
            if not absolute_path.is_absolute():
                # Try relative to project root
                absolute_path = self.project_root / file_path

            if not absolute_path.exists():
                return 'N/A'

            with open(absolute_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            return file_hash[:16]  # First 16 chars for brevity

        except Exception as e:
            self.logger.debug(f"Failed to hash {file_path}: {e}")
            return 'N/A'


def main():
    """
    Main entry point for standalone execution

    Usage:
        python3 bandit_scanner.py [target_directory]

    Examples:
        python3 bandit_scanner.py
        python3 bandit_scanner.py ../../backend/
        python3 bandit_scanner.py /path/to/python/code
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Bandit SAST Scanner - Production Grade',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan default target (backend/)
  python3 bandit_scanner.py

  # Scan specific directory
  python3 bandit_scanner.py ../../backend/app/

  # Scan with custom timeout (10 minutes)
  python3 bandit_scanner.py --timeout 600 /path/to/code

  # Scan secops itself (dogfooding)
  python3 bandit_scanner.py ../..
        """
    )

    parser.add_argument(
        'target',
        nargs='?',
        default=None,
        help='Directory to scan (default: backend/)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Scan timeout in seconds (default: 300)'
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
    scanner = BanditScanner(
        scan_target=target,
        output_dir=output_dir,
        timeout=args.timeout
    )

    # Run scan
    success = scanner.run_scan()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
