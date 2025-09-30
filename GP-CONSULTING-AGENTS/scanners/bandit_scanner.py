#!/usr/bin/env python3
"""
Bandit Scanner - Clean, Simple, Working
Single-purpose scanner for Python security analysis
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig

class BanditScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        self.tool_path = "bandit"  # Use system bandit

        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Bandit severity mapping (lowercase to match other scanners)
        self.severity_mapping = {
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low"
        }

    def scan(self, target_path: str) -> dict:
        """Simple scan that just works"""
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Check for Python files before running
        if not self._has_python_files(target):
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "message": "No Python files found"},
                "target": target_path,
                "tool": "bandit",
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id()
            }
            self._save_results(empty_result)
            return empty_result

        cmd = [
            self.tool_path,
            "-r", str(target),
            "-f", "json"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                # Clean the output - bandit sometimes includes progress bars in stdout
                stdout_clean = result.stdout

                # Find the JSON part (starts with { and ends with })
                json_start = stdout_clean.find('{')
                json_end = stdout_clean.rfind('}')

                if json_start >= 0 and json_end >= 0 and json_end > json_start:
                    json_part = stdout_clean[json_start:json_end + 1]
                    data = json.loads(json_part)

                    # Process and persist results
                    processed_results = self._process_results(data, target_path)
                    self._save_results(processed_results)

                    return processed_results
                else:
                    # No valid JSON found
                    empty_result = {
                        "findings": [],
                        "summary": {"total": 0, "message": "No valid JSON in bandit output"},
                        "target": target_path,
                        "tool": "bandit",
                        "timestamp": datetime.now().isoformat(),
                        "scan_id": self._generate_scan_id()
                    }
                    self._save_results(empty_result)
                    return empty_result
            else:
                empty_result = {
                    "findings": [],
                    "summary": {"total": 0},
                    "target": target_path,
                    "tool": "bandit",
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": self._generate_scan_id()
                }
                self._save_results(empty_result)
                return empty_result

        except json.JSONDecodeError as e:
            # Return empty results instead of crashing
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "error": f"JSON parse error: {e}"},
                "target": target_path,
                "tool": "bandit",
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id()
            }
            self._save_results(empty_result)
            return empty_result
        except Exception as e:
            raise RuntimeError(f"Bandit scan failed: {e}")

    def _process_results(self, data: dict, target_path: str) -> dict:
        """Process results into standardized format with severity normalization"""
        results = data.get("results", [])
        metrics = data.get("metrics", {})

        # Count files safely
        files_scanned = 0
        if "_totals" in metrics:
            files_scanned = metrics["_totals"].get("loc", 0)
        else:
            # Count non-_totals keys as files
            files_scanned = len([k for k in metrics.keys() if k != "_totals"])

        # Normalize findings with standard severity levels (lowercase)
        normalized_findings = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for finding in results:
            # Map bandit severity to standard levels
            bandit_severity = finding.get("issue_severity", "MEDIUM").upper()
            normalized_severity = self._normalize_severity(bandit_severity)
            severity_counts[normalized_severity] += 1

            normalized_findings.append({
                "file": finding.get("filename", ""),
                "line": finding.get("line_number", 0),
                "severity": normalized_severity,
                "issue": finding.get("issue_text", ""),
                "confidence": finding.get("issue_confidence", "MEDIUM"),
                "cwe": finding.get("issue_cwe", {}).get("id") if isinstance(finding.get("issue_cwe"), dict) else None,
                "test_id": finding.get("test_id", ""),
                "code": finding.get("code", "")
            })

        return {
            "findings": normalized_findings,
            "summary": {
                "total": len(results),
                "files_scanned": files_scanned,
                "severity_breakdown": severity_counts
            },
            "target": target_path,
            "tool": "bandit",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id()
        }

    def _normalize_severity(self, bandit_severity: str) -> str:
        """Map bandit severity to standard levels"""
        return self.severity_mapping.get(bandit_severity, "medium")

    def _has_python_files(self, target: Path) -> bool:
        """Check if target contains Python files"""
        if target.is_file():
            return target.suffix == '.py'
        elif target.is_dir():
            return any(target.rglob('*.py'))
        return False

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier (same format as other scanners)"""
        return f"bandit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

    def _save_results(self, results: dict):
        """Save scan results using standard pattern"""
        scan_id = results.get("scan_id", self._generate_scan_id())
        filename = f"{scan_id}.json"

        output_file = self.output_dir / filename
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"🐍 Bandit results saved to: {output_file}")

            # Also save latest.json (same as other scanners)
            latest_file = self.output_dir / "bandit_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️ Failed to save results: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python bandit_scanner.py <target_path>")
        print("Scans Python code for security issues using Bandit")
        sys.exit(1)

    scanner = BanditScanner()
    results = scanner.scan(sys.argv[1])

    print(f"🐍 Bandit found {results['summary']['total']} security issues")

    if results['summary']['total'] > 0:
        print(f"   Files scanned: {results['summary']['files_scanned']}")

        # Show severity breakdown
        severity = results['summary']['severity_breakdown']
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")