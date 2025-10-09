#!/usr/bin/env python3
"""
Checkov Scanner - Clean, Simple, Working
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
import shutil

class CheckovScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Check if checkov is available
        if not shutil.which("checkov"):
            raise RuntimeError("checkov not found - install with 'pip install checkov'")

        self.tool_path = "checkov"  # Use system checkov

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Framework support matrix
        self.supported_frameworks = [
            "terraform", "cloudformation", "kubernetes", "docker",
            "arm", "bicep", "github_actions", "gitlab_ci", "helm"
        ]

        # Severity mapping
        self.severity_mapping = {
            "CRITICAL": "critical",
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low",
            "INFO": "low"
        }

    def scan(self, target_path: str, frameworks: List[str] = None) -> dict:
        """Simple scan that just works"""
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Auto-detect frameworks if not specified
        if not frameworks:
            frameworks = self._detect_frameworks(target)

        if not frameworks:
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "frameworks_scanned": []},
                "target": target_path,
                "tool": "checkov",
                "note": "No supported IaC frameworks detected",
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id()
            }
            self._save_results(empty_result)
            return empty_result

        cmd = [
            self.tool_path,
            "-d", str(target),
            "--output", "json",
            "--quiet",
            "--compact"
        ]

        # Add detected frameworks
        for framework in frameworks:
            if framework in self.supported_frameworks:
                cmd.extend(["--framework", framework])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.stdout:
                data = json.loads(result.stdout)
                results = self._process_results(data, target_path, frameworks)
                self._save_results(results)
                return results
            else:
                empty_result = {
                    "findings": [],
                    "summary": {"total": 0, "frameworks_scanned": frameworks or []},
                    "target": target_path,
                    "tool": "checkov",
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": self._generate_scan_id()
                }
                self._save_results(empty_result)
                return empty_result

        except Exception as e:
            raise RuntimeError(f"Checkov scan failed: {e}")

    def _detect_frameworks(self, target: Path) -> List[str]:
        """Auto-detect which IaC frameworks are present"""
        detected = []

        # Terraform detection
        if list(target.glob("**/*.tf")) or list(target.glob("**/*.tfvars")):
            detected.append("terraform")

        # Kubernetes detection
        k8s_files = list(target.glob("**/*.yaml")) + list(target.glob("**/*.yml"))
        if k8s_files:
            # Check if YAML contains Kubernetes resources
            for yaml_file in k8s_files[:5]:  # Sample first 5 files
                try:
                    with open(yaml_file, 'r') as f:
                        content = f.read().lower()
                        if any(k8s_indicator in content for k8s_indicator in
                              ['apiversion:', 'kind:', 'metadata:', 'spec:']):
                            detected.append("kubernetes")
                            break
                except:
                    continue

        # Docker detection
        if (list(target.glob("**/Dockerfile*")) or
            list(target.glob("**/*.dockerfile")) or
            list(target.glob("**/docker-compose*.yml"))):
            detected.append("docker")

        # CloudFormation detection
        cf_files = list(target.glob("**/*.json")) + list(target.glob("**/*.template"))
        if cf_files:
            for cf_file in cf_files[:3]:  # Sample first 3 files
                try:
                    with open(cf_file, 'r') as f:
                        content = f.read()
                        if '"AWSTemplateFormatVersion"' in content or '"Resources"' in content:
                            detected.append("cloudformation")
                            break
                except:
                    continue

        # ARM template detection
        if list(target.glob("**/*.json")):
            for json_file in list(target.glob("**/*.json"))[:3]:
                try:
                    with open(json_file, 'r') as f:
                        content = f.read()
                        if '"$schema"' in content and 'deploymentTemplate' in content:
                            detected.append("arm")
                            break
                except:
                    continue

        # GitHub Actions detection
        if list(target.glob("**/.github/workflows/*.yml")) or list(target.glob("**/.github/workflows/*.yaml")):
            detected.append("github_actions")

        # GitLab CI detection
        if list(target.glob("**/.gitlab-ci.yml")) or list(target.glob("**/.gitlab-ci.yaml")):
            detected.append("gitlab_ci")

        # Helm detection
        if list(target.glob("**/Chart.yaml")) or list(target.glob("**/values.yaml")):
            detected.append("helm")

        return list(set(detected))  # Remove duplicates

    def _process_results(self, data: dict, target_path: str, frameworks: List[str]) -> dict:
        """Process Checkov output with proper format handling"""

        all_failed = []
        all_passed = []
        all_skipped = []

        # Handle different Checkov output formats
        if isinstance(data, list):
            # Multi-framework run format
            for run_data in data:
                if isinstance(run_data, dict):
                    results = run_data.get("results", {})
                    all_failed.extend(results.get("failed_checks", []))
                    all_passed.extend(results.get("passed_checks", []))
                    all_skipped.extend(results.get("skipped_checks", []))
        elif isinstance(data, dict):
            if "results" in data:
                # Single run format
                results = data["results"]
                all_failed.extend(results.get("failed_checks", []))
                all_passed.extend(results.get("passed_checks", []))
                all_skipped.extend(results.get("skipped_checks", []))
            else:
                # Direct format (sometimes Checkov returns this)
                all_failed.extend(data.get("failed_checks", []))
                all_passed.extend(data.get("passed_checks", []))
                all_skipped.extend(data.get("skipped_checks", []))

        # Normalize and enhance findings
        for finding in all_failed:
            # Normalize severity
            original_severity = finding.get("severity", "MEDIUM")
            finding["normalized_severity"] = self.severity_mapping.get(
                original_severity.upper(), "medium"
            )

            # Add framework context
            finding["framework"] = finding.get("check_type", "unknown")

            # Clean file paths (make them relative to target)
            if "file_path" in finding:
                try:
                    abs_file_path = Path(finding["file_path"])
                    target_path_obj = Path(target_path)
                    finding["relative_file_path"] = str(abs_file_path.relative_to(target_path_obj))
                except ValueError:
                    finding["relative_file_path"] = finding["file_path"]

        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in all_failed:
            severity = finding.get("normalized_severity", "medium")
            if severity in severity_counts:
                severity_counts[severity] += 1

        return {
            "findings": all_failed,
            "summary": {
                "total": len(all_failed),
                "passed": len(all_passed),
                "failed": len(all_failed),
                "skipped": len(all_skipped),
                "frameworks_scanned": frameworks,
                "severity_breakdown": severity_counts
            },
            "target": target_path,
            "tool": "checkov",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "metadata": {
                "frameworks_detected": frameworks,
                "scan_duration": None  # Could be added with timing
            }
        }

    def _normalize_severity(self, checkov_severity: str) -> str:
        """Map Checkov severities to standard levels"""
        return self.severity_mapping.get(checkov_severity.upper(), "medium")

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"checkov_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

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

            print(f"📄 Checkov results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "checkov_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")
            # Don't fail the scan because of save issues

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python checkov_scanner.py <target_path>")
        print("Scans Infrastructure-as-Code for security misconfigurations using Checkov")
        sys.exit(1)

    scanner = CheckovScanner()
    results = scanner.scan(sys.argv[1])

    print(f"📋 Checkov found {results['summary']['total']} issues")

    if results['summary']['total'] > 0:
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity['critical']}")
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")

        if results['summary'].get('frameworks_scanned'):
            print(f"   Frameworks: {', '.join(results['summary']['frameworks_scanned'])}")
    else:
        print(f"   ✅ No issues found")
        if results['summary'].get('frameworks_scanned'):
            print(f"   Frameworks scanned: {', '.join(results['summary']['frameworks_scanned'])}")