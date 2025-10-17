#!/usr/bin/env python3
"""
Production-Grade Semgrep Scanner - Multi-Language SAST
=======================================================
Stage: CI (Continuous Integration)
Purpose: Multi-language SAST - OWASP Top 10 coverage across Python, JavaScript, etc.
Inherits: SecurityScanner base class

Features:
- Multi-language support (Python, JavaScript, TypeScript, Go, Java, etc.)
- OWASP Top 10 coverage
- CWE extraction from rule metadata
- Severity mapping (ERROR→HIGH, WARNING→MEDIUM, INFO→LOW)
- Rule-based detection (XSS, SQLi, Command Injection, etc.)

Usage:
    # Scan entire project
    python3 semgrep_scanner.py --target /path/to/project

    # Scan with specific config
    python3 semgrep_scanner.py --target . --config "p/owasp-top-ten"
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add shared library to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared-library' / 'base-classes'))

from base_scanner import SecurityScanner


class SemgrepScanner(SecurityScanner):
    """
    Semgrep SAST Scanner for Multi-Language Security Analysis

    Detects OWASP Top 10 vulnerabilities across multiple languages:
    - A01:2021 - Broken Access Control
    - A02:2021 - Cryptographic Failures
    - A03:2021 - Injection
    - A04:2021 - Insecure Design
    - A05:2021 - Security Misconfiguration
    - A06:2021 - Vulnerable and Outdated Components
    - A07:2021 - Identification and Authentication Failures
    - A08:2021 - Software and Data Integrity Failures
    - A09:2021 - Security Logging and Monitoring Failures
    - A10:2021 - Server-Side Request Forgery
    """

    # Severity mapping: Semgrep → Our format
    SEVERITY_MAP = {
        'ERROR': 'HIGH',
        'WARNING': 'MEDIUM',
        'INFO': 'LOW'
    }

    def __init__(
        self,
        scan_target: Path = None,
        output_dir: Path = None,
        timeout: int = 300,
        config: str = "auto"
    ):
        """
        Initialize Semgrep scanner

        Args:
            scan_target: Directory to scan (defaults to project root)
            output_dir: Where to save findings
            timeout: Scan timeout in seconds (default: 300 = 5 minutes)
            config: Semgrep config (default: "auto" for automatic rule detection)
        """
        # Set defaults
        if scan_target is None:
            scan_target = Path(__file__).parent.parent.parent.parent  # Project root

        if output_dir is None:
            # Use absolute path to GP-DATA (go up 4 levels from scanner to GP-copilot root)
            gp_root = Path(__file__).parent.parent.parent.parent
            output_dir = gp_root / 'GP-DATA' / 'active' / '1-sec-assessment' / 'ci-findings'

        super().__init__(scan_target, output_dir, timeout)

        self.config = config

    def get_scanner_name(self) -> str:
        """Return scanner name"""
        return 'semgrep'

    def get_tool_name(self) -> str:
        """Return CLI tool name"""
        return 'semgrep'

    def get_install_instructions(self) -> str:
        """Return installation instructions"""
        return 'pip install semgrep'

    def get_output_filename(self) -> str:
        """Return output filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'semgrep_{timestamp}.json'

    def build_command(self, output_file: str) -> List[str]:
        """
        Build Semgrep command

        Args:
            output_file: Path to save raw Semgrep JSON output

        Returns:
            Command list ready for subprocess.run()
        """
        return [
            'semgrep',
            'scan',
            '--config', self.config,  # 'auto' or 'p/owasp-top-ten'
            '--json',
            '--output', output_file,
            '--timeout', str(self.timeout),
            '--max-memory', '4096',  # 4GB max memory
            '--no-git-ignore',  # Scan all files
            '--quiet',  # Suppress progress output
            str(self.scan_target)
        ]

    def parse_results(self, output_file: Path) -> Dict:
        """
        Parse Semgrep JSON output

        Semgrep Output Structure:
        {
            "results": [
                {
                    "check_id": "python.flask.security.xss.audit.direct-use-of-jinja2",
                    "path": "backend/app.py",
                    "start": {"line": 42, "col": 10},
                    "end": {"line": 42, "col": 50},
                    "extra": {
                        "message": "Detected direct use of Jinja2 without autoescaping...",
                        "severity": "ERROR",
                        "metadata": {
                            "owasp": ["A03:2021 - Injection"],
                            "cwe": ["CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')"],
                            "category": "security",
                            "technology": ["flask"],
                            "confidence": "HIGH"
                        },
                        "fingerprint": "abc123..."
                    }
                }
            ],
            "errors": [],
            "paths": {
                "scanned": ["backend/", "frontend/"]
            }
        }
        """
        try:
            with open(output_file, 'r') as f:
                semgrep_output = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to parse Semgrep output: {e}")
            return {
                'findings': [],
                'metadata': {
                    'scanner': self.get_scanner_name(),
                    'scan_time': datetime.now().isoformat(),
                    'target': str(self.scan_target),
                    'error': str(e)
                }
            }

        results = semgrep_output.get('results', [])
        errors = semgrep_output.get('errors', [])

        # Build enriched findings
        findings = []
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        # Track OWASP categories and CWEs
        owasp_categories = {}
        cwe_list = set()
        languages = set()

        for result in results:
            check_id = result.get('check_id', 'UNKNOWN')
            path = result.get('path', '')

            # Extract language from path
            if path.endswith('.py'):
                languages.add('Python')
            elif path.endswith(('.js', '.jsx')):
                languages.add('JavaScript')
            elif path.endswith(('.ts', '.tsx')):
                languages.add('TypeScript')
            elif path.endswith('.go'):
                languages.add('Go')
            elif path.endswith('.java'):
                languages.add('Java')

            # Get location
            start = result.get('start', {})
            end = result.get('end', {})
            start_line = start.get('line', 0)
            end_line = end.get('line', start_line)

            # Get extra metadata
            extra = result.get('extra', {})
            message = extra.get('message', '')
            semgrep_severity = extra.get('severity', 'INFO').upper()

            # Map severity
            our_severity = self.SEVERITY_MAP.get(semgrep_severity, 'MEDIUM')
            severity_breakdown[our_severity] = severity_breakdown.get(our_severity, 0) + 1

            # Extract metadata
            metadata = extra.get('metadata', {})
            owasp = metadata.get('owasp', [])
            cwe = metadata.get('cwe', [])
            category = metadata.get('category', 'unknown')
            confidence = metadata.get('confidence', 'MEDIUM')

            # Track OWASP categories
            for owasp_cat in owasp:
                owasp_categories[owasp_cat] = owasp_categories.get(owasp_cat, 0) + 1

            # Extract CWE IDs
            extracted_cwes = []
            for cwe_str in cwe:
                # Extract CWE-XXX from strings like "CWE-79: Cross-site Scripting"
                if 'CWE-' in cwe_str:
                    cwe_id = cwe_str.split(':')[0].strip()
                    extracted_cwes.append(cwe_id)
                    cwe_list.add(cwe_id)

            # Build finding
            finding = {
                'id': f'semgrep_{len(findings) + 1}',
                'scanner': self.get_scanner_name(),

                # Rule details
                'rule_id': check_id,
                'title': check_id.split('.')[-1].replace('-', ' ').title(),
                'message': message[:500],  # Truncate long messages

                # Severity
                'severity': our_severity,
                'confidence': confidence,

                # Location
                'file': path,
                'line': start_line,
                'end_line': end_line,
                'column': start.get('col', 0),

                # Classification
                'category': category,
                'owasp': owasp,
                'cwe': extracted_cwes,

                # Metadata
                'scan_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),

                # Original data
                '_original': result
            }

            findings.append(finding)

        # Build metadata
        metadata = {
            'scanner': self.get_scanner_name(),
            'scan_timestamp': datetime.now().isoformat(),
            'target': str(self.scan_target),
            'config': self.config,
            'issue_count': len(findings),
            'severity_breakdown': severity_breakdown,

            # Semgrep-specific metrics
            'semgrep_summary': {
                'total_findings': len(findings),
                'errors': len(errors),
                'languages_scanned': sorted(list(languages)),
                'owasp_categories': owasp_categories,
                'unique_cwes': sorted(list(cwe_list)),
                'cwe_count': len(cwe_list)
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
        python3 semgrep_scanner.py --target /path/to/project
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Semgrep Scanner - Multi-Language SAST',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan entire project with auto config
  python3 semgrep_scanner.py --target /path/to/project

  # Scan with OWASP Top 10 rules
  python3 semgrep_scanner.py --target . --config "p/owasp-top-ten"

  # Scan with custom timeout
  python3 semgrep_scanner.py --target . --timeout 600

  # Scan backend only
  python3 semgrep_scanner.py --target ../../backend/
        """
    )

    parser.add_argument(
        '--target',
        default=None,
        help='Directory to scan (default: project root)'
    )

    parser.add_argument(
        '--config',
        default='auto',
        help='Semgrep config (default: auto, options: p/owasp-top-ten, p/security-audit)'
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
    scanner = SemgrepScanner(
        scan_target=target,
        output_dir=output_dir,
        timeout=args.timeout,
        config=args.config
    )

    # Run scan
    success = scanner.run_scan()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
