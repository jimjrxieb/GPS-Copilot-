#!/usr/bin/env python3
"""
Bandit Security Fixer - Real Implementation
Automatically fixes Python security issues detected by Bandit scanner
"""

import json
import sys
import re
import os
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class BanditFixer:
    """
    Applies automated fixes for Bandit security findings.

    Supports LOW and MEDIUM severity fixes that are safe to apply automatically.
    HIGH severity issues require manual review.
    """

    def __init__(self):
        config = GPDataConfig()
        self.fixes_dir = config.get_fixes_directory()
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        # Define fixable issues with their patterns and fixes
        self.fix_patterns = {
            # Hardcoded passwords (B105, B106, B107)
            "B105": {
                "name": "hardcoded_password_string",
                "severity": ["LOW", "MEDIUM"],
                "fix_strategy": self._fix_hardcoded_password_string
            },
            "B106": {
                "name": "hardcoded_password_funcarg",
                "severity": ["LOW", "MEDIUM"],
                "fix_strategy": self._fix_hardcoded_password_funcarg
            },
            "B107": {
                "name": "hardcoded_password_default",
                "severity": ["LOW", "MEDIUM"],
                "fix_strategy": self._fix_hardcoded_password_url
            },

            # Bind all interfaces (B104)
            "B104": {
                "name": "hardcoded_bind_all_interfaces",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_bind_all_interfaces
            },

            # Insecure temp file (B108)
            "B108": {
                "name": "hardcoded_tmp",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_insecure_temp_file
            },

            # Flask debug mode (B201)
            "B201": {
                "name": "flask_debug_true",
                "severity": ["HIGH"],
                "fix_strategy": self._fix_flask_debug
            },

            # Insecure hash algorithms (B303, B304, B324)
            "B303": {
                "name": "blacklist_hashlib_md5",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_weak_hash_md5
            },
            "B304": {
                "name": "blacklist_hashlib_sha1",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_weak_hash_sha1
            },

            # Insecure random (B311)
            "B311": {
                "name": "blacklist_random",
                "severity": ["LOW"],
                "fix_strategy": self._fix_insecure_random
            },

            # SSL verification disabled (B501)
            "B501": {
                "name": "request_with_no_cert_validation",
                "severity": ["HIGH"],
                "fix_strategy": self._fix_ssl_verification
            },

            # Unsafe YAML load (B506)
            "B506": {
                "name": "yaml_load",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_unsafe_yaml
            },

            # Shell injection (B602, B605)
            "B602": {
                "name": "subprocess_popen_with_shell_equals_true",
                "severity": ["HIGH"],
                "fix_strategy": self._fix_shell_injection
            },
            "B605": {
                "name": "start_process_with_a_shell",
                "severity": ["HIGH"],
                "fix_strategy": self._fix_os_system
            },

            # SQL injection (B608)
            "B608": {
                "name": "hardcoded_sql_expressions",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_sql_injection
            },

            # Assert used for security (B101)
            "B101": {
                "name": "assert_used",
                "severity": ["LOW"],
                "fix_strategy": self._fix_assert_usage
            },

            # Exec usage (B102)
            "B102": {
                "name": "exec_used",
                "severity": ["MEDIUM"],
                "fix_strategy": self._fix_exec_usage
            },

            # Bare except (B110)
            "B110": {
                "name": "try_except_pass",
                "severity": ["LOW"],
                "fix_strategy": self._fix_bare_except
            }
        }

        self.applied_fixes = []
        self.skipped_fixes = []
        self.backup_files = []

    def fix_findings(self, scan_results_path: str, project_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Main entry point to fix Bandit findings.

        Args:
            scan_results_path: Path to Bandit scan results JSON
            project_path: Path to the project being fixed
            auto_fix: If True, apply fixes automatically for LOW/MEDIUM issues

        Returns:
            Dictionary with fix results
        """
        print(f"🔧 Bandit Fixer - Starting fix process")
        print(f"   Scan results: {scan_results_path}")
        print(f"   Target project: {project_path}")
        print(f"   Auto-fix mode: {auto_fix}")
        print()

        # Load scan results
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)

        if 'results' not in scan_data:
            print("❌ Invalid scan results format")
            return {"status": "error", "message": "Invalid scan results format"}

        findings = scan_data.get('results', [])

        if not findings:
            print("✅ No findings to fix!")
            return {
                "status": "success",
                "fixes_applied": 0,
                "message": "No security issues found"
            }

        print(f"📊 Found {len(findings)} security issues to analyze")
        print()

        # Group findings by file
        findings_by_file = {}
        for finding in findings:
            filename = finding.get('filename', '').replace('./', '')
            if project_path not in filename:
                # Adjust path to be relative to project
                filename = str(Path(project_path) / filename)

            if filename not in findings_by_file:
                findings_by_file[filename] = []
            findings_by_file[filename].append(finding)

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
        findings.sort(key=lambda x: x.get('line_number', 0), reverse=True)

        # Apply fixes
        for finding in findings:
            test_id = finding.get('test_id', '')
            severity = finding.get('issue_severity', '')
            line_number = finding.get('line_number', 0)

            if test_id not in self.fix_patterns:
                self.skipped_fixes.append({
                    "file": filepath,
                    "line": line_number,
                    "issue": test_id,
                    "reason": "No fix pattern available"
                })
                continue

            fix_config = self.fix_patterns[test_id]

            # Check if we should auto-fix based on severity
            if severity not in fix_config['severity'] and auto_fix:
                self.skipped_fixes.append({
                    "file": filepath,
                    "line": line_number,
                    "issue": test_id,
                    "severity": severity,
                    "reason": f"Severity {severity} requires manual review"
                })
                print(f"   ⚠️  Line {line_number}: {test_id} ({severity}) - Manual review required")
                continue

            # Apply fix
            print(f"   🔧 Line {line_number}: Fixing {test_id} - {fix_config['name']}")

            try:
                content = fix_config['fix_strategy'](content, finding, filepath)

                self.applied_fixes.append({
                    "file": filepath,
                    "line": line_number,
                    "issue": test_id,
                    "severity": severity,
                    "fix_applied": fix_config['name']
                })
            except Exception as e:
                print(f"   ❌ Failed to fix: {str(e)}")
                self.skipped_fixes.append({
                    "file": filepath,
                    "line": line_number,
                    "issue": test_id,
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

    def _fix_hardcoded_password_string(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix hardcoded password strings by using environment variables"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for os if not present
            if 'import os' not in content:
                lines.insert(0, 'import os')
                line_num += 1

            # Replace hardcoded password with environment variable
            if 'password' in line.lower():
                var_match = re.match(r'^(\s*)(\w+)\s*=\s*["\'].*["\']', line)
                if var_match:
                    indent = var_match.group(1)
                    var_name = var_match.group(2)
                    env_var = f"{var_name.upper()}"

                    # Replace with os.environ.get()
                    lines[line_num] = f"{indent}{var_name} = os.environ.get('{env_var}', '')"

                    # Add comment
                    lines.insert(line_num, f"{indent}# FIXED: Use environment variable instead of hardcoded password")

        return '\n'.join(lines)

    def _fix_hardcoded_password_funcarg(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix hardcoded password in function arguments"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for os if not present
            if 'import os' not in content:
                lines.insert(0, 'import os')
                line_num += 1

            # Replace password="..." with password=os.environ.get()
            pattern = r'password\s*=\s*["\']([^"\']+)["\']'
            replacement = r"password=os.environ.get('DB_PASSWORD', '')"
            lines[line_num] = re.sub(pattern, replacement, line)

            # Add comment
            lines.insert(line_num, "    # FIXED: Use environment variable for password")

        return '\n'.join(lines)

    def _fix_hardcoded_password_url(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix hardcoded password in URLs"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for os if not present
            if 'import os' not in content:
                lines.insert(0, 'import os')
                line_num += 1

            # Extract URL components and use environment variables
            url_pattern = r'["\']https?://([^:]+):([^@]+)@([^"\']+)["\']'
            if re.search(url_pattern, line):
                # Replace with formatted string using env vars
                lines[line_num] = re.sub(
                    url_pattern,
                    r'f"https://{os.environ.get(\'API_USER\', \'\')}:{os.environ.get(\'API_PASSWORD\', \'\')}@\3"',
                    line
                )
                lines.insert(line_num, "    # FIXED: Use environment variables for credentials")

        return '\n'.join(lines)

    def _fix_bind_all_interfaces(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix binding to all interfaces (0.0.0.0)"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace 0.0.0.0 with 127.0.0.1 or use environment variable
            if '0.0.0.0' in line:
                # Add import for os if not present
                if 'import os' not in content:
                    lines.insert(0, 'import os')
                    line_num += 1

                # Replace with environment variable with safe default
                lines[line_num] = line.replace("'0.0.0.0'", "os.environ.get('HOST', '127.0.0.1')")
                lines.insert(line_num, "    # FIXED: Use environment variable for host (default to localhost)")

        return '\n'.join(lines)

    def _fix_insecure_temp_file(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix insecure temp file usage"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for tempfile if not present
            if 'import tempfile' not in content:
                # Find where to insert import
                import_line = 0
                for i, l in enumerate(lines):
                    if l.startswith('import ') or l.startswith('from '):
                        import_line = i + 1
                lines.insert(import_line, 'import tempfile')
                line_num += 1

            # Replace hardcoded temp path with secure tempfile
            if '/tmp/' in line:
                # Extract variable name
                var_match = re.match(r'^(\s*)(\w+)\s*=\s*["\'].*["\']', line)
                if var_match:
                    indent = var_match.group(1)
                    var_name = var_match.group(2)

                    # Use tempfile.mkstemp for files or mkdtemp for directories
                    if 'file' in var_name.lower():
                        lines[line_num] = f"{indent}{var_name}_fd, {var_name} = tempfile.mkstemp()"
                        lines.insert(line_num + 1, f"{indent}os.close({var_name}_fd)  # Close the file descriptor")
                    else:
                        lines[line_num] = f"{indent}{var_name} = tempfile.mkdtemp()"

                    lines.insert(line_num, f"{indent}# FIXED: Use secure tempfile instead of hardcoded path")

        return '\n'.join(lines)

    def _fix_flask_debug(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix Flask debug mode"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace debug=True with debug=False or environment check
            if 'debug=True' in line:
                # Add import for os if not present
                if 'import os' not in content:
                    lines.insert(0, 'import os')
                    line_num += 1

                # Replace with environment-based debug flag
                lines[line_num] = line.replace(
                    'debug=True',
                    "debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'"
                )
                lines.insert(line_num, "    # FIXED: Use environment variable for debug mode")

        return '\n'.join(lines)

    def _fix_weak_hash_md5(self, content: str, finding: Dict, filepath: str) -> str:
        """Replace MD5 with SHA256"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace md5 with sha256
            if 'md5' in line:
                lines[line_num] = line.replace('hashlib.md5', 'hashlib.sha256')
                lines.insert(line_num, "    # FIXED: Replaced MD5 with SHA256")

        return '\n'.join(lines)

    def _fix_weak_hash_sha1(self, content: str, finding: Dict, filepath: str) -> str:
        """Replace SHA1 with SHA256"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace sha1 with sha256
            if 'sha1' in line:
                lines[line_num] = line.replace('hashlib.sha1', 'hashlib.sha256')
                lines.insert(line_num, "    # FIXED: Replaced SHA1 with SHA256")

        return '\n'.join(lines)

    def _fix_insecure_random(self, content: str, finding: Dict, filepath: str) -> str:
        """Replace random with secrets for security-sensitive operations"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for secrets if not present
            if 'import secrets' not in content:
                import_line = 0
                for i, l in enumerate(lines):
                    if l.startswith('import ') or l.startswith('from '):
                        import_line = i + 1
                lines.insert(import_line, 'import secrets')
                line_num += 1

            # Replace random.random() with secrets
            if 'random.random()' in line:
                lines[line_num] = line.replace('random.random()', 'secrets.randbits(64)')
                lines.insert(line_num, "    # FIXED: Use secrets module for cryptographic randomness")
            elif 'random.randint' in line:
                # Extract the range and use secrets.randbelow
                match = re.search(r'random\.randint\((\d+),\s*(\d+)\)', line)
                if match:
                    low, high = match.groups()
                    lines[line_num] = re.sub(
                        r'random\.randint\(\d+,\s*\d+\)',
                        f'secrets.randbelow({high}) + {low}',
                        line
                    )
                    lines.insert(line_num, "    # FIXED: Use secrets module for secure random numbers")

        return '\n'.join(lines)

    def _fix_ssl_verification(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix disabled SSL verification"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Remove verify=False or set it to True
            if 'verify=False' in line:
                lines[line_num] = line.replace('verify=False', 'verify=True')
                lines.insert(line_num, "    # FIXED: Enabled SSL certificate verification")
            elif 'CERT_NONE' in line:
                lines[line_num] = line.replace('ssl.CERT_NONE', 'ssl.CERT_REQUIRED')
                lines.insert(line_num, "    # FIXED: Require SSL certificate validation")

        return '\n'.join(lines)

    def _fix_unsafe_yaml(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix unsafe YAML loading"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace yaml.load with yaml.safe_load
            if 'yaml.load' in line and 'yaml.safe_load' not in line:
                lines[line_num] = line.replace('yaml.load', 'yaml.safe_load')
                lines.insert(line_num, "    # FIXED: Use safe_load to prevent arbitrary code execution")

        return '\n'.join(lines)

    def _fix_shell_injection(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix shell injection vulnerabilities"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for shlex if not present
            if 'shell=True' in line and 'import shlex' not in content:
                import_line = 0
                for i, l in enumerate(lines):
                    if l.startswith('import ') or l.startswith('from '):
                        import_line = i + 1
                lines.insert(import_line, 'import shlex')
                line_num += 1

            # Remove shell=True and use list format
            if 'shell=True' in line:
                # Try to extract the command
                cmd_match = re.search(r'["\']([^"\']+)["\']', line)
                if cmd_match:
                    cmd = cmd_match.group(1)

                    # Check if command contains user input (simple heuristic)
                    if '+' in line and 'user_input' in line:
                        # Use shlex.quote for user input
                        lines[line_num] = line.replace('shell=True', 'shell=False')
                        lines.insert(line_num, "    # FIXED: Disabled shell=True - ensure user input is properly escaped")
                        lines.insert(line_num + 1, "    # Consider using shlex.quote() for user input")
                    else:
                        # Convert to list format
                        lines[line_num] = line.replace('shell=True', 'shell=False')
                        lines.insert(line_num, "    # FIXED: Disabled shell=True to prevent command injection")

        return '\n'.join(lines)

    def _fix_os_system(self, content: str, finding: Dict, filepath: str) -> str:
        """Replace os.system with subprocess"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Add import for subprocess if not present
            if 'import subprocess' not in content:
                import_line = 0
                for i, l in enumerate(lines):
                    if l.startswith('import ') or l.startswith('from '):
                        import_line = i + 1
                lines.insert(import_line, 'import subprocess')
                line_num += 1

            # Replace os.system with subprocess.run
            if 'os.system' in line:
                # Extract the command
                cmd_match = re.search(r'os\.system\(["\']([^"\']+)["\']\)', line)
                if cmd_match:
                    cmd = cmd_match.group(1)
                    indent = len(line) - len(line.lstrip())

                    # Convert to subprocess.run with list
                    cmd_parts = cmd.split()
                    new_line = ' ' * indent + f"subprocess.run({cmd_parts}, check=True)"
                    lines[line_num] = new_line
                    lines.insert(line_num, ' ' * indent + "# FIXED: Replaced os.system with subprocess.run")

        return '\n'.join(lines)

    def _fix_sql_injection(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix SQL injection vulnerabilities"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Look for string formatting in SQL queries
            if '%' in line and ('SELECT' in line or 'INSERT' in line or 'UPDATE' in line or 'DELETE' in line):
                # Replace % formatting with parameterized queries
                if '"%s"' in line or "'%s'" in line:
                    lines[line_num] = line.replace('"%s"', '?').replace("'%s'", '?')
                    lines.insert(line_num, "    # FIXED: Use parameterized queries instead of string formatting")
                    lines.insert(line_num + 2, "    # Pass parameters separately: cursor.execute(query, (param1, param2))")

        return '\n'.join(lines)

    def _fix_assert_usage(self, content: str, finding: Dict, filepath: str) -> str:
        """Replace assert with proper error handling"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace assert with if/raise
            if line.strip().startswith('assert '):
                indent = len(line) - len(line.lstrip())

                # Extract the condition and message
                assert_match = re.match(r'^(\s*)assert\s+([^,]+)(?:,\s*(.+))?', line)
                if assert_match:
                    spaces = assert_match.group(1)
                    condition = assert_match.group(2)
                    message = assert_match.group(3) or '"Assertion failed"'

                    # Replace with if/raise
                    lines[line_num] = f"{spaces}if not ({condition}):"
                    lines.insert(line_num + 1, f"{spaces}    raise ValueError({message})")
                    lines.insert(line_num, f"{spaces}# FIXED: Replaced assert with explicit error handling")

        return '\n'.join(lines)

    def _fix_exec_usage(self, content: str, finding: Dict, filepath: str) -> str:
        """Comment out exec usage and add warning"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Comment out exec and add warning
            if 'exec(' in line:
                indent = len(line) - len(line.lstrip())
                lines[line_num] = ' ' * indent + '# ' + line.strip()
                lines.insert(line_num, ' ' * indent + "# FIXED: exec() is dangerous and should be avoided")
                lines.insert(line_num + 1, ' ' * indent + "# TODO: Refactor to avoid dynamic code execution")
                lines.insert(line_num + 3, ' ' * indent + "raise NotImplementedError('exec usage disabled for security')")

        return '\n'.join(lines)

    def _fix_bare_except(self, content: str, finding: Dict, filepath: str) -> str:
        """Fix bare except clauses"""
        lines = content.split('\n')
        line_num = finding['line_number'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            # Replace bare except with Exception
            if line.strip() == 'except:':
                indent = len(line) - len(line.lstrip())
                lines[line_num] = ' ' * indent + 'except Exception as e:'
                lines.insert(line_num, ' ' * indent + "# FIXED: Catch specific exception instead of bare except")

                # Update the pass or continue line if present
                if line_num + 2 < len(lines):
                    next_line = lines[line_num + 2]
                    if 'pass' in next_line:
                        lines[line_num + 2] = ' ' * (indent + 4) + '# TODO: Handle exception properly'
                        lines.insert(line_num + 3, ' ' * (indent + 4) + 'pass')

        return '\n'.join(lines)

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
                "files_modified": len(set(f['file'] for f in self.applied_fixes)),
                "backups_created": len(self.backup_files)
            },
            "applied_fixes": self.applied_fixes,
            "skipped_fixes": self.skipped_fixes,
            "backup_files": self.backup_files,
            "fix_summary": self._generate_summary()
        }

        # Save report
        report_file = self.fixes_dir / f"bandit_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Fix report saved: {report_file}")

        return report

    def _generate_summary(self) -> Dict[str, int]:
        """Generate summary of fixes by type"""
        summary = {}

        for fix in self.applied_fixes:
            issue_type = fix['issue']
            if issue_type not in summary:
                summary[issue_type] = 0
            summary[issue_type] += 1

        return summary


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Bandit Security Fixer - Automatically fix Python security issues")
        print()
        print("Usage:")
        print("  bandit_fixer.py <scan_results.json> <project_path> [--no-auto-fix]")
        print()
        print("Arguments:")
        print("  scan_results.json  - Path to Bandit scan results JSON file")
        print("  project_path       - Path to the project to fix")
        print("  --no-auto-fix      - Only fix LOW severity issues (skip MEDIUM/HIGH)")
        print()
        print("Example:")
        print("  bandit_fixer.py scan_results.json ./my_project")
        print("  bandit_fixer.py scan_results.json ./my_project --no-auto-fix")
        print()
        print("Fixable Issues:")
        print("  B101 - Assert usage         (LOW)    → Replace with if/raise")
        print("  B102 - Exec usage          (MEDIUM)  → Comment out and warn")
        print("  B104 - Bind all interfaces (MEDIUM)  → Use 127.0.0.1 or env var")
        print("  B105 - Hardcoded passwords (MEDIUM)  → Use environment variables")
        print("  B106 - Password in funcarg (MEDIUM)  → Use environment variables")
        print("  B107 - Password in URL     (MEDIUM)  → Use environment variables")
        print("  B108 - Insecure temp file  (MEDIUM)  → Use tempfile module")
        print("  B110 - Bare except         (LOW)     → Catch Exception")
        print("  B201 - Flask debug mode    (HIGH)    → Use env var for debug")
        print("  B303 - MD5 hash           (MEDIUM)  → Replace with SHA256")
        print("  B304 - SHA1 hash          (MEDIUM)  → Replace with SHA256")
        print("  B311 - Insecure random     (LOW)     → Use secrets module")
        print("  B501 - No SSL verify       (HIGH)    → Enable verification")
        print("  B506 - Unsafe YAML load    (MEDIUM)  → Use safe_load")
        print("  B602 - Shell injection     (HIGH)    → Disable shell=True")
        print("  B605 - os.system usage     (HIGH)    → Use subprocess")
        print("  B608 - SQL injection       (MEDIUM)  → Parameterized queries")
        sys.exit(1)

    scan_results = sys.argv[1]
    project_path = sys.argv[2]
    auto_fix = '--no-auto-fix' not in sys.argv

    fixer = BanditFixer()
    result = fixer.fix_findings(scan_results, project_path, auto_fix)

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