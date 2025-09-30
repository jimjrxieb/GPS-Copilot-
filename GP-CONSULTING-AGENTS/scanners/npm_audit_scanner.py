#!/usr/bin/env python3
"""
NPM Audit Scanner - Clean, Simple, Working
Single-purpose scanner that just works
"""

import subprocess
import json
import os
from pathlib import Path
import sys
from datetime import datetime
# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig
from typing import Dict, List, Optional
import shutil  # For checking if npm is available

class NpmAuditScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Check if npm is available
        if not shutil.which("npm"):
            raise RuntimeError("npm not found - install Node.js and npm")

        self.tool_path = "npm"

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # NPM severity mapping
        self.severity_mapping = {
            "critical": "critical",
            "high": "high",
            "moderate": "medium",
            "low": "low",
            "info": "low"
        }

    def scan(self, target_path: str) -> dict:
        """Simple scan that just works"""
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Look for package.json files
        package_json_files = list(target.glob('**/package.json'))
        if not package_json_files:
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "projects_scanned": 0},
                "target": target_path,
                "tool": "npm_audit",
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id(),
                "projects": []
            }
            self._save_results(empty_result)
            return empty_result

        all_vulnerabilities = []
        all_projects = []
        total_count = 0
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for package_json in package_json_files:
            project_context = self._analyze_npm_project(package_json)
            all_projects.append(project_context)

            project_dir = package_json.parent

            cmd = [
                self.tool_path,
                "audit",
                "--json",
                "--audit-level", "info"  # Get all levels
            ]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=180  # Increased timeout
                )

                # npm audit can return non-zero exit codes even on success
                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        vulnerabilities = data.get("vulnerabilities", {})

                        for vuln_name, vuln_data in vulnerabilities.items():
                            # Enhanced vulnerability data
                            original_severity = vuln_data.get("severity", "low")
                            normalized_severity = self.severity_mapping.get(original_severity, "medium")

                            vulnerability = {
                                "package": vuln_name,
                                "severity": original_severity,
                                "normalized_severity": normalized_severity,
                                "via": vuln_data.get("via", []),
                                "range": vuln_data.get("range", "unknown"),
                                "fix_available": vuln_data.get("fixAvailable", False),
                                "project_name": project_context["name"],
                                "project_path": str(project_dir.relative_to(Path(target_path))),
                                "nodes": len(vuln_data.get("nodes", [])),
                                "effects": vuln_data.get("effects", [])
                            }

                            # Add fix information if available
                            if isinstance(vuln_data.get("fixAvailable"), dict):
                                fix_info = vuln_data["fixAvailable"]
                                vulnerability["fix_info"] = {
                                    "name": fix_info.get("name", ""),
                                    "version": fix_info.get("version", ""),
                                    "is_semver_major": fix_info.get("isSemVerMajor", False)
                                }

                            all_vulnerabilities.append(vulnerability)
                            severity_counts[normalized_severity] += 1
                            total_count += 1

                        # Also capture audit metadata
                        project_context["audit_metadata"] = {
                            "vulnerabilities_found": len(vulnerabilities),
                            "audit_report_version": data.get("auditReportVersion", "unknown"),
                            "npm_version": data.get("npmVersion", "unknown")
                        }

                    except json.JSONDecodeError as e:
                        # Log the error but continue
                        print(f"⚠️  Failed to parse npm audit output for {project_dir}: {e}")
                        project_context["error"] = f"JSON parse error: {str(e)}"
                else:
                    # No output - might be no vulnerabilities or an error
                    project_context["audit_metadata"] = {"vulnerabilities_found": 0}

            except subprocess.TimeoutExpired:
                print(f"⚠️  NPM audit timeout for {project_dir}")
                project_context["error"] = "Audit timeout"
            except Exception as e:
                print(f"⚠️  NPM audit error for {project_dir}: {e}")
                project_context["error"] = str(e)

        results = {
            "findings": all_vulnerabilities,
            "summary": {
                "total": total_count,
                "projects_scanned": len(package_json_files),
                "projects_with_vulnerabilities": len([p for p in all_projects if p.get("audit_metadata", {}).get("vulnerabilities_found", 0) > 0]),
                "severity_breakdown": severity_counts,
                "package_managers_detected": list(set([p["package_manager"] for p in all_projects]))
            },
            "target": target_path,
            "tool": "npm_audit",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "projects": all_projects,
            "metadata": {
                "total_dependencies": sum([p.get("dependencies_count", 0) for p in all_projects]),
                "total_dev_dependencies": sum([p.get("dev_dependencies_count", 0) for p in all_projects])
            }
        }

        # Save results
        self._save_results(results)

        return results

    def _analyze_npm_project(self, package_json_path: Path) -> dict:
        """Analyze NPM project context"""
        project_dir = package_json_path.parent

        context = {
            "project_path": str(project_dir),
            "has_package_lock": (project_dir / "package-lock.json").exists(),
            "has_yarn_lock": (project_dir / "yarn.lock").exists(),
            "has_node_modules": (project_dir / "node_modules").exists(),
            "package_manager": "unknown"
        }

        # Determine package manager
        if context["has_yarn_lock"]:
            context["package_manager"] = "yarn"
        elif context["has_package_lock"]:
            context["package_manager"] = "npm"

        # Read package.json for metadata
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                context["name"] = package_data.get("name", "unknown")
                context["version"] = package_data.get("version", "unknown")
                context["dependencies_count"] = len(package_data.get("dependencies", {}))
                context["dev_dependencies_count"] = len(package_data.get("devDependencies", {}))
        except Exception:
            context["name"] = "unknown"
            context["version"] = "unknown"
            context["dependencies_count"] = 0
            context["dev_dependencies_count"] = 0

        return context

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"npm_audit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

    def _save_results(self, results: dict):
        """Save scan results to persistent storage"""
        scan_id = results.get("scan_id", self._generate_scan_id())
        filename = f"{scan_id}.json"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_file = self.output_dir / filename
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"📦 NPM Audit results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "npm_audit_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")
            # Don't fail the scan because of save issues

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python npm_audit_scanner.py <target_path>")
        print("Scans all package.json files recursively for npm vulnerabilities")
        sys.exit(1)

    scanner = NpmAuditScanner()
    results = scanner.scan(sys.argv[1])

    print(f"📦 NPM Audit found {results['summary']['total']} vulnerabilities")
    print(f"   Projects scanned: {results['summary']['projects_scanned']}")
    print(f"   Projects with issues: {results['summary']['projects_with_vulnerabilities']}")

    # Show severity breakdown
    if results['summary']['total'] > 0:
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity['critical']}")
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")