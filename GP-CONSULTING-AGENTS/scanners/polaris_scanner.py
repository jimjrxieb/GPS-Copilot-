#!/usr/bin/env python3
"""
Polaris Scanner - Kubernetes Best Practices Validation
Single-purpose scanner for K8s configuration best practices
"""

import subprocess
import json
import shutil
from pathlib import Path
import sys
from datetime import datetime
# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig
from typing import Dict, List, Optional

from kubernetes_utils import KubernetesDetector

class PolarisScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        self.tool_path = self._find_polaris()

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Severity mapping (Polaris uses danger/warning/success)
        self.severity_mapping = {
            "danger": "high",
            "warning": "medium",
            "success": "low",
            "error": "critical"
        }

    def _find_polaris(self) -> str:
        """Find polaris binary with fallback options"""
        # Try system first
        if shutil.which("polaris"):
            return "polaris"

        # Try local installation
        local_path = Path.home() / ".local/bin/polaris"
        if local_path.exists():
            return str(local_path)

        # Try project binary paths
        project_paths = [
            Path("/home/jimmie/linkops-industries/GP-copilot/bin/polaris"),
            Path("/home/jimmie/linkops-industries/James-OS/guidepoint/tools/bin/polaris"),
        ]

        for path in project_paths:
            if path.exists():
                return str(path)

        raise RuntimeError(
            "Polaris not found. Install with:\n"
            "curl -L https://github.com/FairwindsOps/polaris/releases/download/8.5.4/polaris_linux_amd64.tar.gz | tar xz\n"
            "sudo mv polaris /usr/local/bin/"
        )

    def scan(self, target_path: str, checks: str = "all") -> dict:
        """
        Run Polaris best practices scan

        Args:
            target_path: Directory containing Kubernetes manifests
            checks: Checks to run (all, security, efficiency, reliability)

        Returns:
            Scan results dictionary
        """
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Get Kubernetes context
        k8s_summary = KubernetesDetector.get_manifest_summary(target)
        manifests = KubernetesDetector.find_k8s_manifests(target)

        if not manifests:
            empty_result = self._create_empty_result(target_path, checks, k8s_summary)
            empty_result["note"] = "No Kubernetes manifests found"
            self._save_results(empty_result)
            return empty_result

        # Build command - audit mode for local files
        cmd = [
            self.tool_path,
            "audit",
            "--audit-path", str(target),
            "--format", "json"
        ]

        # Add check filter if specified
        if checks != "all":
            cmd.extend(["--checks", checks])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    results = self._process_results(data, target_path, checks, k8s_summary)
                    self._save_results(results)
                    return results
                except json.JSONDecodeError:
                    empty_result = self._create_empty_result(target_path, checks, k8s_summary)
                    empty_result["note"] = "Polaris output parsing failed"
                    self._save_results(empty_result)
                    return empty_result
            else:
                empty_result = self._create_empty_result(target_path, checks, k8s_summary)
                self._save_results(empty_result)
                return empty_result

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Polaris scan timed out after 120 seconds")
        except Exception as e:
            raise RuntimeError(f"Polaris scan failed: {e}")

    def _create_empty_result(self, target_path: str, checks: str, k8s_summary: dict) -> dict:
        """Create empty result structure"""
        return {
            "findings": [],
            "summary": {
                "total": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "checks_run": checks
            },
            "target": target_path,
            "tool": "polaris",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "kubernetes_context": k8s_summary
        }

    def _process_results(self, data: dict, target_path: str, checks: str, k8s_summary: dict) -> dict:
        """Process Polaris results into standard format"""

        findings = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # Polaris output structure: {AuditData: {Results: [{PodResult: {...}}]}}
        audit_data = data.get("AuditData", data)  # Handle both formats
        results = audit_data.get("Results", [])

        for result in results:
            # Get pod/resource info
            pod_result = result.get("PodResult", {})
            resource_name = pod_result.get("Name", "unknown")
            resource_kind = pod_result.get("Kind", "unknown")
            namespace = pod_result.get("Namespace", "default")

            # Get container results
            container_results = pod_result.get("ContainerResults", [])

            for container in container_results:
                container_name = container.get("Name", "unknown")

                # Process each check result
                for check_id, check_result in container.get("Results", {}).items():
                    severity = check_result.get("Severity", "warning")
                    success = check_result.get("Success", True)

                    # Only include failures
                    if not success:
                        normalized_severity = self.severity_mapping.get(severity, "medium")
                        severity_counts[normalized_severity] += 1

                        finding = {
                            "check_id": check_id,
                            "message": check_result.get("Message", ""),
                            "category": check_result.get("Category", "unknown"),
                            "severity": severity,
                            "normalized_severity": normalized_severity,
                            "resource_name": resource_name,
                            "resource_kind": resource_kind,
                            "namespace": namespace,
                            "container_name": container_name,
                            "success": success
                        }

                        findings.append(finding)

        # Calculate summary statistics
        total_findings = len(findings)

        # Count by category
        category_counts = {}
        for finding in findings:
            category = finding.get("category", "unknown")
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1

        return {
            "findings": findings,
            "summary": {
                "total": total_findings,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts,
                "checks_run": checks
            },
            "target": target_path,
            "tool": "polaris",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "kubernetes_context": k8s_summary,
            "metadata": {
                "checks_type": checks,
                "scan_type": "best_practices"
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"polaris_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

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

            print(f"⭐ Polaris results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "polaris_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python polaris_scanner.py <target_path> [checks]")
        print("Checks: all (default), security, efficiency, reliability")
        sys.exit(1)

    target_path = sys.argv[1]
    checks = sys.argv[2] if len(sys.argv) > 2 else "all"

    scanner = PolarisScanner()
    results = scanner.scan(target_path, checks)

    print(f"⭐ Polaris found {results['summary']['total']} issues")

    if results['summary']['total'] > 0:
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity.get('critical', 0)}")
        print(f"   High: {severity.get('high', 0)}")
        print(f"   Medium: {severity.get('medium', 0)}")
        print(f"   Low: {severity.get('low', 0)}")