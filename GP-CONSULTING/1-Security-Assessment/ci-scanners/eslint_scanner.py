#!/usr/bin/env python3
"""
ESLint Scanner - JavaScript/TypeScript Code Quality

Detects:
- Code style violations
- Best practice violations
- Potential bugs
- Code complexity issues
- Unused variables
- Formatting inconsistencies

Compliance:
- PCI-DSS 6.5.1 (Code quality prevents injection flaws)
- OWASP ASVS 1.14 (Build process includes code analysis)

Usage:
    python3 eslint_scanner.py --target /path/to/project
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

class ESLintScanner:
    def __init__(self, target_dir, output_dir=None):
        self.target_dir = os.path.abspath(target_dir)
        self.output_dir = output_dir or os.path.join(GP_DATA_DIR, "active/1-sec-assessment/ci-findings")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        os.makedirs(self.output_dir, exist_ok=True)

    def check_eslint_installed(self):
        """Check if ESLint is installed"""
        try:
            result = subprocess.run(
                ['npx', 'eslint', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ ESLint version: {result.stdout.strip()}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        print("⚠️  ESLint not found. Installing via npx...")
        return False

    def install_eslint_config(self):
        """Create a default ESLint configuration if none exists"""
        eslintrc_path = os.path.join(self.target_dir, '.eslintrc.json')

        if os.path.exists(eslintrc_path):
            print(f"✓ Using existing ESLint config: {eslintrc_path}")
            return

        # Create default config focusing on security and best practices
        default_config = {
            "env": {
                "browser": True,
                "es2021": True,
                "node": True
            },
            "extends": [
                "eslint:recommended"
            ],
            "parserOptions": {
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "rules": {
                "no-unused-vars": "warn",
                "no-console": "warn",
                "no-eval": "error",
                "no-implied-eval": "error",
                "no-new-func": "error",
                "eqeqeq": "error",
                "no-var": "warn",
                "prefer-const": "warn",
                "no-undef": "error",
                "semi": ["warn", "always"],
                "quotes": ["warn", "single"],
                "indent": ["warn", 2]
            }
        }

        with open(eslintrc_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        print(f"✓ Created default ESLint config: {eslintrc_path}")

    def find_js_ts_files(self):
        """Find all JavaScript/TypeScript files"""
        extensions = ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs']
        js_files = []

        exclude_dirs = {'node_modules', '.git', 'dist', 'build', 'coverage', '.next'}

        for root, dirs, files in os.walk(self.target_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    js_files.append(os.path.join(root, file))

        return js_files

    def run_eslint(self):
        """Run ESLint scan"""
        print(f"\n{'='*60}")
        print(f"ESLint Scanner - JavaScript/TypeScript Code Quality")
        print(f"{'='*60}\n")
        print(f"Target: {self.target_dir}")
        print(f"Timestamp: {self.timestamp}\n")

        # Check for JS/TS files
        js_files = self.find_js_ts_files()

        if not js_files:
            print("⚠️  No JavaScript/TypeScript files found in target directory")
            results = {
                "scan_metadata": {
                    "scanner": "eslint",
                    "version": "8.x",
                    "target": self.target_dir,
                    "timestamp": self.timestamp,
                    "status": "no_files_found"
                },
                "summary": {
                    "total_files_scanned": 0,
                    "total_issues": 0,
                    "errors": 0,
                    "warnings": 0
                },
                "findings": []
            }

            output_file = os.path.join(self.output_dir, f"eslint_{self.timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n✓ Results saved: {output_file}")
            return results

        print(f"✓ Found {len(js_files)} JavaScript/TypeScript files\n")

        # Install default config if needed
        self.install_eslint_config()

        # Run ESLint with JSON output
        eslint_cmd = [
            'npx', 'eslint',
            self.target_dir,
            '--format', 'json',
            '--ext', '.js,.jsx,.ts,.tsx,.mjs,.cjs',
            '--ignore-pattern', 'node_modules/',
            '--ignore-pattern', 'dist/',
            '--ignore-pattern', 'build/',
            '--no-error-on-unmatched-pattern'
        ]

        print(f"Running: {' '.join(eslint_cmd)}\n")

        try:
            result = subprocess.run(
                eslint_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.target_dir
            )

            # ESLint returns exit code 1 when issues found, not necessarily an error
            eslint_results = json.loads(result.stdout) if result.stdout else []

            # Transform ESLint output to our format
            findings = []
            total_errors = 0
            total_warnings = 0

            for file_result in eslint_results:
                file_path = file_result.get('filePath', '')
                messages = file_result.get('messages', [])

                for msg in messages:
                    severity = 'ERROR' if msg.get('severity') == 2 else 'WARNING'
                    if severity == 'ERROR':
                        total_errors += 1
                    else:
                        total_warnings += 1

                    findings.append({
                        "file": os.path.relpath(file_path, self.target_dir),
                        "line": msg.get('line', 0),
                        "column": msg.get('column', 0),
                        "severity": severity,
                        "rule_id": msg.get('ruleId', 'unknown'),
                        "message": msg.get('message', ''),
                        "category": "code_quality"
                    })

            results = {
                "scan_metadata": {
                    "scanner": "eslint",
                    "version": "8.x",
                    "target": self.target_dir,
                    "timestamp": self.timestamp,
                    "status": "completed"
                },
                "summary": {
                    "total_files_scanned": len(js_files),
                    "total_issues": len(findings),
                    "errors": total_errors,
                    "warnings": total_warnings,
                    "severity_breakdown": {
                        "ERROR": total_errors,
                        "WARNING": total_warnings
                    }
                },
                "findings": findings
            }

            # Save results
            output_file = os.path.join(self.output_dir, f"eslint_{self.timestamp}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            # Print summary
            print(f"\n{'='*60}")
            print(f"ESLint Scan Complete")
            print(f"{'='*60}\n")
            print(f"Files Scanned: {len(js_files)}")
            print(f"Total Issues:  {len(findings)}")
            print(f"  Errors:      {total_errors}")
            print(f"  Warnings:    {total_warnings}\n")

            if findings:
                print("Top Issues:")
                # Count issues by rule
                rule_counts = {}
                for finding in findings:
                    rule_id = finding['rule_id']
                    rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1

                # Show top 10
                for rule_id, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  - {rule_id}: {count} occurrences")

            print(f"\n✓ Results saved: {output_file}")

            return results

        except subprocess.TimeoutExpired:
            print("❌ ESLint scan timed out (5 minute limit)")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse ESLint output: {e}")
            print(f"Raw output: {result.stdout}")
            return None
        except Exception as e:
            print(f"❌ ESLint scan failed: {e}")
            return None

def main():
    import argparse

    parser = argparse.ArgumentParser(description='ESLint Scanner for JavaScript/TypeScript')
    parser.add_argument('--target', required=True, help='Target directory to scan')
    parser.add_argument('--output', help='Output directory for results')

    args = parser.parse_args()

    scanner = ESLintScanner(args.target, args.output)
    scanner.check_eslint_installed()
    results = scanner.run_eslint()

    if results and results['summary']['total_issues'] > 0:
        sys.exit(1)  # Exit with error if issues found

    sys.exit(0)

if __name__ == "__main__":
    main()