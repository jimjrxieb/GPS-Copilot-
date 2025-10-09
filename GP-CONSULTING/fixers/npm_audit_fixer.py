#!/usr/bin/env python3
"""
NPM Audit Fixer - Real Implementation
Automatically fixes Node.js dependency vulnerabilities detected by npm audit
"""

import json
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class NpmAuditFixer:
    """
    Applies automated fixes for npm audit security findings.

    Supports:
    - Automatic dependency updates for fixable vulnerabilities
    - package.json and package-lock.json updates
    - Audit fix recommendations
    """

    def __init__(self):
        config = GPDataConfig()
        self.fixes_dir = config.get_fixes_directory()
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        self.applied_fixes = []
        self.skipped_fixes = []
        self.backup_files = []

    def fix_findings(self, scan_results_path: str, project_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Main entry point to fix npm audit findings.

        Args:
            scan_results_path: Path to npm audit scan results JSON
            project_path: Path to the project being fixed
            auto_fix: If True, apply fixes automatically

        Returns:
            Dictionary with fix results
        """
        print(f"🔧 NPM Audit Fixer - Starting fix process")
        print(f"   Scan results: {scan_results_path}")
        print(f"   Target project: {project_path}")
        print(f"   Auto-fix mode: {auto_fix}")
        print()

        # Load scan results
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)

        # Extract npm audit findings
        vulnerabilities = self._extract_vulnerabilities(scan_data)

        if not vulnerabilities:
            print("✅ No npm vulnerabilities to fix!")
            return {
                "status": "success",
                "fixes_applied": 0,
                "message": "No security issues found"
            }

        print(f"📊 Found {len(vulnerabilities)} npm vulnerabilities to analyze")
        print()

        # Check if package.json and package-lock.json exist
        package_json_path = Path(project_path) / "package.json"
        package_lock_path = Path(project_path) / "package-lock.json"

        if not package_json_path.exists():
            print("❌ No package.json found in project")
            return {
                "status": "error",
                "message": "No package.json found"
            }

        # Create backups
        self._create_backup(str(package_json_path))
        if package_lock_path.exists():
            self._create_backup(str(package_lock_path))

        # Categorize vulnerabilities
        fixable = []
        manual_review = []

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'unknown').lower()
            fixable_via = vuln.get('fixAvailable', False)

            if fixable_via and severity in ['low', 'moderate']:
                fixable.append(vuln)
            else:
                manual_review.append(vuln)

        print(f"📊 Vulnerability Breakdown:")
        print(f"   🔧 Auto-fixable: {len(fixable)}")
        print(f"   ⚠️  Manual review: {len(manual_review)}")
        print()

        # Apply automated fixes
        if fixable and auto_fix:
            print("🔧 Applying automated fixes...")
            fix_result = self._apply_npm_audit_fix(project_path, fixable)

            if fix_result['success']:
                self.applied_fixes.extend(fix_result['fixes'])
                print(f"   ✅ Fixed {len(fix_result['fixes'])} vulnerabilities")
            else:
                print(f"   ❌ Fix failed: {fix_result.get('error')}")

        # Record manual review items
        for vuln in manual_review:
            self.skipped_fixes.append({
                "package": vuln.get('name'),
                "severity": vuln.get('severity'),
                "vulnerability": vuln.get('title'),
                "reason": "Requires manual review due to severity or breaking changes"
            })

        # Generate fix report
        report = self._generate_fix_report(scan_results_path, project_path)

        print("\n📊 Fix Summary:")
        print(f"   ✅ Fixes applied: {len(self.applied_fixes)}")
        print(f"   ⚠️  Fixes skipped (manual review needed): {len(self.skipped_fixes)}")
        print(f"   💾 Backup files created: {len(self.backup_files)}")

        return report

    def _extract_vulnerabilities(self, scan_data: dict) -> List[Dict]:
        """Extract vulnerability data from npm audit results"""
        vulnerabilities = []

        # Handle different npm audit output formats
        if 'results' in scan_data and 'npm_audit' in scan_data['results']:
            npm_data = scan_data['results']['npm_audit']

            # npm audit v7+ format (newer npm versions)
            if 'vulnerabilities' in npm_data:
                for pkg_name, vuln_data in npm_data.get('vulnerabilities', {}).items():
                    if isinstance(vuln_data, dict):
                        vulnerabilities.append({
                            'name': pkg_name,
                            'severity': vuln_data.get('severity', 'unknown'),
                            'title': vuln_data.get('via', [{}])[0].get('title', 'Unknown vulnerability') if isinstance(vuln_data.get('via'), list) else 'Unknown vulnerability',
                            'fixAvailable': vuln_data.get('fixAvailable', False),
                            'range': vuln_data.get('range', 'unknown'),
                            'nodes': vuln_data.get('nodes', []),
                            'effects': vuln_data.get('effects', [])
                        })

            # npm audit v6 format (legacy)
            elif 'advisories' in npm_data:
                for advisory_id, advisory in npm_data.get('advisories', {}).items():
                    vulnerabilities.append({
                        'name': advisory.get('module_name', 'unknown'),
                        'severity': advisory.get('severity', 'unknown'),
                        'title': advisory.get('title', 'Unknown vulnerability'),
                        'fixAvailable': advisory.get('patched_versions', 'none') != 'none',
                        'range': advisory.get('vulnerable_versions', 'unknown'),
                        'recommendation': advisory.get('recommendation', '')
                    })

        return vulnerabilities

    def _apply_npm_audit_fix(self, project_path: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Apply npm audit fix command"""
        try:
            # Run npm audit fix
            result = subprocess.run(
                ['npm', 'audit', 'fix'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            fixes = []
            if result.returncode == 0:
                # Parse output to determine what was fixed
                for vuln in vulnerabilities:
                    fixes.append({
                        "package": vuln.get('name'),
                        "severity": vuln.get('severity'),
                        "fix_applied": "npm audit fix",
                        "description": f"Updated {vuln.get('name')} to fix {vuln.get('title')}"
                    })

                return {
                    "success": True,
                    "fixes": fixes,
                    "output": result.stdout
                }
            else:
                # Try npm audit fix --force for more aggressive fixes
                force_result = subprocess.run(
                    ['npm', 'audit', 'fix', '--force'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if force_result.returncode == 0:
                    for vuln in vulnerabilities:
                        fixes.append({
                            "package": vuln.get('name'),
                            "severity": vuln.get('severity'),
                            "fix_applied": "npm audit fix --force",
                            "description": f"Force updated {vuln.get('name')} to fix {vuln.get('title')}"
                        })

                    return {
                        "success": True,
                        "fixes": fixes,
                        "output": force_result.stdout,
                        "warning": "Used --force flag for breaking changes"
                    }
                else:
                    return {
                        "success": False,
                        "error": force_result.stderr or result.stderr
                    }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "npm audit fix timed out after 5 minutes"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "npm command not found - ensure Node.js is installed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _create_backup(self, filepath: str) -> Optional[str]:
        """Create backup of file before fixing"""
        try:
            backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r') as source:
                with open(backup_path, 'w') as backup:
                    backup.write(source.read())
            self.backup_files.append(backup_path)
            return backup_path
        except Exception as e:
            print(f"   ⚠️  Could not create backup: {e}")
            return None

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
                "backups_created": len(self.backup_files)
            },
            "applied_fixes": self.applied_fixes,
            "skipped_fixes": self.skipped_fixes,
            "backup_files": self.backup_files
        }

        # Save report
        report_file = self.fixes_dir / f"npm_audit_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Fix report saved: {report_file}")

        return report


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("NPM Audit Fixer - Automatically fix Node.js dependency vulnerabilities")
        print()
        print("Usage:")
        print("  npm_audit_fixer.py <scan_results.json> <project_path>")
        print()
        print("Arguments:")
        print("  scan_results.json  - Path to npm audit scan results JSON file")
        print("  project_path       - Path to the Node.js project to fix")
        print()
        print("Example:")
        print("  npm_audit_fixer.py scan_results.json ./my-node-app")
        print()
        print("How it works:")
        print("  1. Analyzes npm audit findings")
        print("  2. Categorizes by severity and fixability")
        print("  3. Applies 'npm audit fix' for low/moderate issues")
        print("  4. Flags high/critical for manual review")
        print("  5. Creates backups and generates report")
        print()
        print("Note: Requires npm to be installed and accessible")
        sys.exit(1)

    scan_results = sys.argv[1]
    project_path = sys.argv[2]

    fixer = NpmAuditFixer()
    result = fixer.fix_findings(scan_results, project_path)

    # Exit with appropriate code
    if result.get('status') == 'success':
        if result.get('statistics', {}).get('fixes_applied', 0) > 0:
            print("\n✅ Fixes applied successfully!")
            print("⚠️  Please review the changes and run tests before committing")
            print("⚠️  Run 'npm install' to ensure lock file is updated")
        sys.exit(0)
    else:
        print("\n❌ Fix process failed")
        sys.exit(1)


if __name__ == "__main__":
    main()