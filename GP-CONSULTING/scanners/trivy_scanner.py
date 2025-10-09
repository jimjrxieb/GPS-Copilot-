#!/usr/bin/env python3
"""
Trivy Scanner - Clean, Simple, Working
Single-purpose scanner for vulnerability and misconfiguration detection
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

class TrivyScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Try system trivy first, then fallbacks
        if shutil.which("trivy"):
            self.tool_path = "trivy"
        else:
            # Try common locations
            candidate_paths = [
                "/home/jimmie/linkops-industries/GP-copilot/bin/trivy",
                "/usr/local/bin/trivy",
                "/opt/trivy/bin/trivy"
            ]

            self.tool_path = None
            for path in candidate_paths:
                if Path(path).exists():
                    self.tool_path = path
                    break

            if not self.tool_path:
                raise RuntimeError(
                    "trivy not found. Install with:\n"
                    "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"
                )

        # Standard data persistence
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Trivy severity mapping
        self.severity_mapping = {
            "CRITICAL": "critical",
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low",
            "UNKNOWN": "low"
        }

    def _detect_scan_context(self, target: Path) -> dict:
        """Detect what Trivy will scan in the target directory"""
        context = {
            "package_files": {},
            "dockerfile_count": 0,
            "total_files": 0
        }

        # Package manager files
        package_patterns = {
            "npm": ["package.json", "package-lock.json", "yarn.lock"],
            "pip": ["requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml"],
            "go": ["go.mod", "go.sum"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
            "composer": ["composer.json", "composer.lock"],
            "ruby": ["Gemfile", "Gemfile.lock"],
            "rust": ["Cargo.toml", "Cargo.lock"]
        }

        for pkg_type, patterns in package_patterns.items():
            found_files = []
            for pattern in patterns:
                found_files.extend(target.glob(f"**/{pattern}"))
            if found_files:
                context["package_files"][pkg_type] = len(found_files)

        # Docker files
        dockerfile_patterns = ["**/Dockerfile*", "**/*.dockerfile"]
        for pattern in dockerfile_patterns:
            context["dockerfile_count"] += len(list(target.glob(pattern)))

        # Count total files for context
        context["total_files"] = len([f for f in target.rglob("*") if f.is_file()])

        return context

    def scan(self, target_path: str) -> dict:
        """Enhanced Trivy filesystem scan"""
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Detect scan context
        scan_context = self._detect_scan_context(target)

        cmd = [
            self.tool_path,
            "fs",
            "--format", "json",
            "--quiet",  # Reduce noise
            str(target)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                data = json.loads(result.stdout)
                results = self._process_results(data, target_path, scan_context)
                self._save_results(results)
                return results
            else:
                empty_result = {
                    "findings": [],
                    "summary": {"total": 0, "scan_coverage": scan_context},
                    "target": target_path,
                    "tool": "trivy",
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": self._generate_scan_id(),
                    "scan_context": scan_context
                }
                self._save_results(empty_result)
                return empty_result

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Trivy scan timed out after 300 seconds")
        except Exception as e:
            raise RuntimeError(f"Trivy scan failed: {e}")

    def _process_results(self, data: dict, target_path: str, scan_context: dict = None) -> dict:
        """Process Trivy results with enhanced metadata"""
        results = data.get("Results", [])
        all_vulnerabilities = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # Track vulnerability sources
        package_managers = set()
        vulnerability_sources = {}

        for result in results:
            result_type = result.get("Type", "unknown")
            target_file = result.get("Target", "unknown")
            vulnerabilities = result.get("Vulnerabilities", [])

            if vulnerabilities:
                package_managers.add(result_type)
                vulnerability_sources[target_file] = len(vulnerabilities)

            for vuln in vulnerabilities:
                # Normalize severity
                original_severity = vuln.get("Severity", "UNKNOWN")
                normalized_severity = self.severity_mapping.get(original_severity, "low")

                enhanced_vuln = {
                    "vulnerability_id": vuln.get("VulnerabilityID", "unknown"),
                    "package_name": vuln.get("PkgName", "unknown"),
                    "package_version": vuln.get("InstalledVersion", "unknown"),
                    "fixed_version": vuln.get("FixedVersion", ""),
                    "severity": original_severity,
                    "normalized_severity": normalized_severity,
                    "title": vuln.get("Title", "Unknown vulnerability"),
                    "description": vuln.get("Description", ""),
                    "source_file": target_file,
                    "source_type": result_type,
                    "cvss_score": vuln.get("CVSS", {}).get("nvd", {}).get("V3Score", 0),
                    "cwe_ids": vuln.get("CweIDs", []),
                    "references": vuln.get("References", []),
                    "published_date": vuln.get("PublishedDate", ""),
                    "last_modified": vuln.get("LastModifiedDate", "")
                }

                all_vulnerabilities.append(enhanced_vuln)
                severity_counts[normalized_severity] += 1

        return {
            "findings": all_vulnerabilities,
            "summary": {
                "total": len(all_vulnerabilities),
                "files_scanned": len(results),
                "severity_breakdown": severity_counts,
                "package_managers_found": list(package_managers),
                "vulnerability_sources": vulnerability_sources,
                "scan_coverage": {
                    "package_files": scan_context.get("package_files", {}) if scan_context else {},
                    "dockerfile_count": scan_context.get("dockerfile_count", 0) if scan_context else 0
                }
            },
            "target": target_path,
            "tool": "trivy",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "scan_context": scan_context or {},
            "metadata": {
                "trivy_db_version": data.get("SchemaVersion", "unknown"),
                "scan_type": "filesystem",
                "scan_performance": {
                    "results_processed": len(results),
                    "total_vulnerabilities": len(all_vulnerabilities)
                }
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"trivy_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

    def _save_results(self, results: dict):
        """Save scan results to persistent storage"""
        scan_id = results.get("scan_id", self._generate_scan_id())
        filename = f"{scan_id}.json"

        output_file = self.output_dir / filename
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"🛡️ Trivy results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "trivy_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python trivy_scanner.py <target_path>")
        print("Scans for vulnerabilities and misconfigurations using Trivy")
        sys.exit(1)

    scanner = TrivyScanner()
    results = scanner.scan(sys.argv[1])

    print(f"🛡️ Trivy found {results['summary']['total']} vulnerabilities")

    if results['summary']['total'] > 0:
        print(f"   Files scanned: {results['summary']['files_scanned']}")

        # Show severity breakdown
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity['critical']}")
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")

        # Show package managers found
        if results['summary'].get('package_managers_found'):
            print(f"   Package managers: {', '.join(results['summary']['package_managers_found'])}")