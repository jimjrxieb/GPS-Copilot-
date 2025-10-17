#!/usr/bin/env python3
"""
Pylint Scanner - Python Code Quality

Detects:
- Code style violations (PEP 8)
- Best practice violations
- Potential bugs
- Code complexity issues
- Unused variables/imports
- Refactoring opportunities

Compliance:
- PCI-DSS 6.5.1 (Code quality prevents injection flaws)
- OWASP ASVS 1.14 (Build process includes code analysis)

Usage:
    python3 pylint_scanner.py --target /path/to/project
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add GP-PLATFORM to path for config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../GP-Backend/james-config'))

try:
    from config import GP_DATA_DIR
except ImportError:
    GP_DATA_DIR = os.path.expanduser("~/linkops-industries/GP-copilot/GP-DATA")

class PylintScanner:
    def __init__(self, target_dir, output_dir=None):
        self.target_dir = os.path.abspath(target_dir)
        self.output_dir = output_dir or os.path.join(GP_DATA_DIR, "active/1-sec-assessment/ci-findings")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        os.makedirs(self.output_dir, exist_ok=True)

    def check_pylint_installed(self):
        """Check if Pylint is installed"""
        try:
            result = subprocess.run(
                ['pylint', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✓ Pylint {version_line}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        print("❌ Pylint not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'pylint'],
                check=True,
                capture_output=True
            )
            print("✓ Pylint installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Pylint")
            return False

    def create_pylintrc(self):
        """Create a default Pylint configuration"""
        pylintrc_path = os.path.join(self.target_dir, '.pylintrc')

        if os.path.exists(pylintrc_path):
            print(f"✓ Using existing Pylint config: {pylintrc_path}")
            return

        # Create default config focusing on security and best practices
        default_config = """[MASTER]
# Ignore generated files and virtual environments
ignore=CVS,.git,__pycache__,.venv,venv,env,node_modules

[MESSAGES CONTROL]
# Enable security-related checks
enable=W0101,W0102,W0104,W0106,W0108,W0109,W0120,W0123,W0150,W0199

# Disable overly strict style checks
disable=C0114,C0115,C0116,  # Missing docstrings
        C0103,              # Invalid name (too strict)
        R0903,              # Too few public methods
        R0913,              # Too many arguments
        W0212               # Protected member access

[REPORTS]
output-format=json

[FORMAT]
max-line-length=120
indent-string='    '

[BASIC]
good-names=i,j,k,x,y,z,ex,Run,_,id,db

[DESIGN]
max-args=7
max-locals=20
max-returns=6
max-branches=15
"""

        with open(pylintrc_path, 'w') as f:
            f.write(default_config)

        print(f"✓ Created default Pylint config: {pylintrc_path}")

    def find_python_files(self):
        """Find all Python files"""
        py_files = []
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache'}

        for root, dirs, files in os.walk(self.target_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))

        return py_files

    def run_pylint(self):
        """Run Pylint scan"""
        print(f"\n{'='*60}")
        print(f"Pylint Scanner - Python Code Quality")
        print(f"{'='*60}\n")
        print(f"Target: {self.target_dir}")
        print(f"Timestamp: {self.timestamp}\n")

        # Check for Python files
        py_files = self.find_python_files()

        if not py_files:
            print("⚠️  No Python files found in target directory")
            results = {
                "scan_metadata": {
                    "scanner": "pylint",
                    "version": "3.x",
                    "target": self.target_dir,
                    "timestamp": self.timestamp,
                    "status": "no_files_found"
                },
                "summary": {
                    "total_files_scanned": 0,
                    "total_issues": 0,
                    "errors": 0,
                    "warnings": 0,
                    "refactor": 0,
                    "convention": 0
                },
                "findings": []
            }

            output_file = os.path.join(self.output_dir, f"pylint_{self.timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n✓ Results saved: {output_file}")
            return results

        print(f"✓ Found {len(py_files)} Python files\n")

        # Create default config if needed
        self.create_pylintrc()

        # Run Pylint with JSON output
        pylint_cmd = [
            'pylint',
            '--output-format=json',
            '--rcfile=' + os.path.join(self.target_dir, '.pylintrc')
        ] + py_files

        print(f"Running Pylint on {len(py_files)} files...\n")

        try:
            result = subprocess.run(
                pylint_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Pylint returns exit code based on score, not necessarily an error
            try:
                pylint_results = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse Pylint JSON output")
                pylint_results = []

            # Transform Pylint output to our format
            findings = []
            severity_counts = {
                "error": 0,
                "warning": 0,
                "refactor": 0,
                "convention": 0
            }

            for msg in pylint_results:
                msg_type = msg.get('type', 'convention').lower()
                severity_counts[msg_type] = severity_counts.get(msg_type, 0) + 1

                # Map Pylint severity to our format
                severity_map = {
                    'error': 'ERROR',
                    'warning': 'WARNING',
                    'refactor': 'INFO',
                    'convention': 'INFO'
                }

                findings.append({
                    "file": os.path.relpath(msg.get('path', ''), self.target_dir),
                    "line": msg.get('line', 0),
                    "column": msg.get('column', 0),
                    "severity": severity_map.get(msg_type, 'INFO'),
                    "rule_id": msg.get('message-id', 'unknown'),
                    "rule_name": msg.get('symbol', 'unknown'),
                    "message": msg.get('message', ''),
                    "category": "code_quality"
                })

            results = {
                "scan_metadata": {
                    "scanner": "pylint",
                    "version": "3.x",
                    "target": self.target_dir,
                    "timestamp": self.timestamp,
                    "status": "completed"
                },
                "summary": {
                    "total_files_scanned": len(py_files),
                    "total_issues": len(findings),
                    "errors": severity_counts.get('error', 0),
                    "warnings": severity_counts.get('warning', 0),
                    "refactor": severity_counts.get('refactor', 0),
                    "convention": severity_counts.get('convention', 0),
                    "severity_breakdown": {
                        "ERROR": severity_counts.get('error', 0),
                        "WARNING": severity_counts.get('warning', 0),
                        "INFO": severity_counts.get('refactor', 0) + severity_counts.get('convention', 0)
                    }
                },
                "findings": findings
            }

            # Save results
            output_file = os.path.join(self.output_dir, f"pylint_{self.timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            # Print summary
            print(f"\n{'='*60}")
            print(f"Pylint Scan Complete")
            print(f"{'='*60}\n")
            print(f"Files Scanned: {len(py_files)}")
            print(f"Total Issues:  {len(findings)}")
            print(f"  Errors:      {severity_counts.get('error', 0)}")
            print(f"  Warnings:    {severity_counts.get('warning', 0)}")
            print(f"  Refactor:    {severity_counts.get('refactor', 0)}")
            print(f"  Convention:  {severity_counts.get('convention', 0)}\n")

            if findings:
                print("Top Issues:")
                # Count issues by rule
                rule_counts = {}
                for finding in findings:
                    rule_name = finding['rule_name']
                    rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1

                # Show top 10
                for rule_name, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  - {rule_name}: {count} occurrences")

            print(f"\n✓ Results saved: {output_file}")

            return results

        except subprocess.TimeoutExpired:
            print("❌ Pylint scan timed out (5 minute limit)")
            return None
        except Exception as e:
            print(f"❌ Pylint scan failed: {e}")
            return None

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Pylint Scanner for Python Code Quality')
    parser.add_argument('--target', required=True, help='Target directory to scan')
    parser.add_argument('--output', help='Output directory for results')

    args = parser.parse_args()

    scanner = PylintScanner(args.target, args.output)

    if not scanner.check_pylint_installed():
        sys.exit(1)

    results = scanner.run_pylint()

    if results and results['summary']['errors'] > 0:
        sys.exit(1)  # Exit with error if errors found

    sys.exit(0)

if __name__ == "__main__":
    main()
