#!/usr/bin/env python3
"""
Kube-hunter Scanner - Kubernetes Penetration Testing
Single-purpose scanner for K8s security vulnerabilities and attack vectors
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

class KubeHunterScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        self.tool_path = self._find_kube_hunter()

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Severity mapping (kube-hunter uses low/medium/high)
        self.severity_mapping = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "critical": "critical"
        }

    def _find_kube_hunter(self) -> str:
        """Find kube-hunter binary with fallback options"""
        # Try system first
        if shutil.which("kube-hunter"):
            return "kube-hunter"

        # Try local installation
        local_path = Path.home() / ".local/bin/kube-hunter"
        if local_path.exists():
            return str(local_path)

        # Try project binary paths
        project_paths = [
            Path("/home/jimmie/linkops-industries/GP-copilot/bin/kube-hunter"),
            Path("/home/jimmie/linkops-industries/James-OS/guidepoint/tools/bin/kube-hunter"),
        ]

        for path in project_paths:
            if path.exists():
                return str(path)

        raise RuntimeError(
            "kube-hunter not found. Install with:\n"
            "pip install kube-hunter\n"
            "or download from: https://github.com/aquasecurity/kube-hunter"
        )

    def scan(self, target_path: str, mode: str = "cidr", cidr_range: str = "10.0.0.0/24") -> dict:
        """
        Run kube-hunter penetration test

        Args:
            target_path: Directory containing Kubernetes manifests (for context)
            mode: Scan mode (cidr, remote, or internal)
            cidr_range: CIDR range to scan (only used in cidr mode)

        Returns:
            Scan results dictionary
        """
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Get Kubernetes context
        k8s_summary = KubernetesDetector.get_manifest_summary(target)

        # Build command based on mode
        cmd = [self.tool_path, "--report", "json"]

        if mode == "cidr":
            cmd.extend(["--cidr", cidr_range])
        elif mode == "remote":
            cmd.append("--remote")
        elif mode == "internal":
            cmd.append("--internal")
        else:
            raise ValueError(f"Invalid scan mode: {mode}. Use 'cidr', 'remote', or 'internal'")

        # Add pod mode for more aggressive testing (optional)
        # cmd.append("--pod")  # Uncomment for pod-based scanning

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    results = self._process_results(data, target_path, mode, k8s_summary)
                    self._save_results(results)
                    return results
                except json.JSONDecodeError:
                    empty_result = self._create_empty_result(target_path, mode, k8s_summary)
                    empty_result["note"] = "kube-hunter output parsing failed"
                    self._save_results(empty_result)
                    return empty_result
            else:
                empty_result = self._create_empty_result(target_path, mode, k8s_summary)
                self._save_results(empty_result)
                return empty_result

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"kube-hunter scan timed out after 300 seconds")
        except Exception as e:
            raise RuntimeError(f"kube-hunter scan failed: {e}")

    def _create_empty_result(self, target_path: str, mode: str, k8s_summary: dict) -> dict:
        """Create empty result structure"""
        return {
            "findings": [],
            "summary": {
                "total": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "scan_mode": mode
            },
            "target": target_path,
            "tool": "kube-hunter",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "kubernetes_context": k8s_summary
        }

    def _process_results(self, data: dict, target_path: str, mode: str, k8s_summary: dict) -> dict:
        """Process kube-hunter results into standard format"""

        findings = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # kube-hunter output structure: {vulnerabilities: [...], hunter_statistics: {...}}
        vulnerabilities = data.get("vulnerabilities", [])
        services = data.get("services", [])
        nodes = data.get("nodes", [])

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "medium").lower()
            normalized_severity = self.severity_mapping.get(severity, "medium")
            severity_counts[normalized_severity] += 1

            finding = {
                "vulnerability": vuln.get("vulnerability", "unknown"),
                "description": vuln.get("description", ""),
                "category": vuln.get("category", "unknown"),
                "severity": severity,
                "normalized_severity": normalized_severity,
                "hunter": vuln.get("hunter", ""),
                "location": vuln.get("location", ""),
                "vid": vuln.get("vid", ""),
                "evidence": vuln.get("evidence", "")
            }

            findings.append(finding)

        # Count by category
        category_counts = {}
        for finding in findings:
            category = finding.get("category", "unknown")
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1

        # Count by hunter type
        hunter_counts = {}
        for finding in findings:
            hunter = finding.get("hunter", "unknown")
            if hunter not in hunter_counts:
                hunter_counts[hunter] = 0
            hunter_counts[hunter] += 1

        total_findings = len(findings)

        return {
            "findings": findings,
            "summary": {
                "total": total_findings,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts,
                "hunter_breakdown": hunter_counts,
                "scan_mode": mode,
                "services_discovered": len(services),
                "nodes_discovered": len(nodes)
            },
            "target": target_path,
            "tool": "kube-hunter",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "kubernetes_context": k8s_summary,
            "services": services,
            "nodes": nodes,
            "metadata": {
                "scan_mode": mode,
                "scan_type": "penetration_test"
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"kube_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

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

            print(f"🎯 Kube-hunter results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "kube_hunter_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python kube_hunter_scanner.py <target_path> [mode] [cidr_range]")
        print("Modes: cidr (default), remote, internal")
        print("Example: python kube_hunter_scanner.py /path/to/k8s cidr 10.0.0.0/24")
        sys.exit(1)

    target_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "cidr"
    cidr_range = sys.argv[3] if len(sys.argv) > 3 else "10.0.0.0/24"

    scanner = KubeHunterScanner()
    results = scanner.scan(target_path, mode, cidr_range)

    print(f"🎯 Kube-hunter found {results['summary']['total']} vulnerabilities")

    if results['summary']['total'] > 0:
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity.get('critical', 0)}")
        print(f"   High: {severity.get('high', 0)}")
        print(f"   Medium: {severity.get('medium', 0)}")
        print(f"   Low: {severity.get('low', 0)}")