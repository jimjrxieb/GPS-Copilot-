#!/usr/bin/env python3
"""
Kube-bench Scanner - CIS Kubernetes Benchmark Compliance
Single-purpose scanner for CIS benchmark validation
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

class KubeBenchScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        self.tool_path = self._find_kube_bench()

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Severity mapping
        self.severity_mapping = {
            "FAIL": "high",
            "WARN": "medium",
            "INFO": "low",
            "PASS": "info"
        }

    def _find_kube_bench(self) -> str:
        """Find kube-bench binary with fallback options"""
        # Try system first
        if shutil.which("kube-bench"):
            return "kube-bench"

        # Try local installation
        local_path = Path.home() / ".local/bin/kube-bench"
        if local_path.exists():
            return str(local_path)

        # Try project binary paths
        project_paths = [
            Path("/home/jimmie/linkops-industries/GP-copilot/bin/kube-bench"),
            Path("/home/jimmie/linkops-industries/James-OS/guidepoint/tools/bin/kube-bench"),
        ]

        for path in project_paths:
            if path.exists():
                return str(path)

        raise RuntimeError(
            "kube-bench not found. Install with:\n"
            "curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.15/kube-bench_0.6.15_linux_amd64.tar.gz | tar xz\n"
            "sudo mv kube-bench /usr/local/bin/"
        )

    def scan(self, target_path: str, benchmark: str = "cis-1.23") -> dict:
        """
        Run kube-bench CIS benchmark scan

        Args:
            target_path: Directory containing Kubernetes manifests
            benchmark: CIS benchmark version (e.g., cis-1.23, cis-1.24)

        Returns:
            Scan results dictionary
        """
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Get Kubernetes context
        k8s_summary = KubernetesDetector.get_manifest_summary(target)

        # Build command
        cmd = [
            self.tool_path,
            "--json",
            "--benchmark", benchmark,
            "--noremediations"  # Skip remediation suggestions for cleaner output
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    results = self._process_results(data, target_path, benchmark, k8s_summary)
                    self._save_results(results)
                    return results
                except json.JSONDecodeError:
                    # kube-bench sometimes outputs non-JSON errors
                    empty_result = self._create_empty_result(target_path, benchmark, k8s_summary)
                    empty_result["note"] = "kube-bench output parsing failed"
                    self._save_results(empty_result)
                    return empty_result
            else:
                empty_result = self._create_empty_result(target_path, benchmark, k8s_summary)
                self._save_results(empty_result)
                return empty_result

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"kube-bench scan timed out after 180 seconds")
        except Exception as e:
            raise RuntimeError(f"kube-bench scan failed: {e}")

    def _create_empty_result(self, target_path: str, benchmark: str, k8s_summary: dict) -> dict:
        """Create empty result structure"""
        return {
            "findings": [],
            "summary": {
                "total": 0,
                "severity_breakdown": {"high": 0, "medium": 0, "low": 0, "info": 0},
                "benchmark": benchmark
            },
            "target": target_path,
            "tool": "kube-bench",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "kubernetes_context": k8s_summary
        }

    def _process_results(self, data: dict, target_path: str, benchmark: str, k8s_summary: dict) -> dict:
        """Process kube-bench results into standard format"""

        findings = []
        severity_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}

        # kube-bench output structure: {Controls: [{tests: [{results: [...]}]}]}
        controls = data.get("Controls", [])

        for control in controls:
            control_id = control.get("id", "unknown")
            control_text = control.get("text", "")

            for test in control.get("tests", []):
                test_id = test.get("section", "")
                test_desc = test.get("desc", "")

                for result in test.get("results", []):
                    status = result.get("status", "PASS")

                    # Only include failures and warnings
                    if status in ["FAIL", "WARN"]:
                        normalized_severity = self.severity_mapping.get(status, "low")
                        severity_counts[normalized_severity] += 1

                        finding = {
                            "test_id": result.get("test_number", ""),
                            "test_desc": result.get("test_desc", ""),
                            "status": status,
                            "normalized_severity": normalized_severity,
                            "control_id": control_id,
                            "control_text": control_text,
                            "section": test_id,
                            "section_desc": test_desc,
                            "audit": result.get("audit", ""),
                            "remediation": result.get("remediation", ""),
                            "reason": result.get("reason", "")
                        }

                        findings.append(finding)

        # Calculate summary statistics
        total_findings = len(findings)

        return {
            "findings": findings,
            "summary": {
                "total": total_findings,
                "severity_breakdown": severity_counts,
                "benchmark": benchmark,
                "total_controls": len(controls)
            },
            "target": target_path,
            "tool": "kube-bench",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "kubernetes_context": k8s_summary,
            "metadata": {
                "benchmark_version": benchmark,
                "scan_type": "cis_compliance"
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"kube_bench_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

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

            print(f"📊 Kube-bench results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "kube_bench_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python kube_bench_scanner.py <target_path> [benchmark]")
        print("Benchmarks: cis-1.23 (default), cis-1.24, cis-1.25, etc.")
        sys.exit(1)

    target_path = sys.argv[1]
    benchmark = sys.argv[2] if len(sys.argv) > 2 else "cis-1.23"

    scanner = KubeBenchScanner()
    results = scanner.scan(target_path, benchmark)

    print(f"📊 Kube-bench found {results['summary']['total']} issues")

    if results['summary']['total'] > 0:
        severity = results['summary']['severity_breakdown']
        print(f"   High: {severity.get('high', 0)}")
        print(f"   Medium: {severity.get('medium', 0)}")
        print(f"   Low: {severity.get('low', 0)}")