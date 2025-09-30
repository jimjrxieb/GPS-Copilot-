#!/usr/bin/env python3
"""
Semgrep Scanner - Clean, Simple, Working
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
import shutil  # For checking if semgrep is available

class SemgrepScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Check if semgrep is available
        if not shutil.which("semgrep"):
            raise RuntimeError("semgrep not found - install with 'pip install semgrep'")

        self.tool_path = "semgrep"

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Semgrep severity mapping
        self.severity_mapping = {
            "ERROR": "high",
            "WARNING": "medium",
            "INFO": "low"
        }

        # Language detection patterns
        self.language_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".php": "php",
            ".rb": "ruby",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json"
        }

    def _detect_languages(self, target: Path) -> Dict[str, int]:
        """Detect programming languages in target directory"""
        language_counts = {}

        for file_path in target.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix in self.language_extensions:
                    lang = self.language_extensions[suffix]
                    language_counts[lang] = language_counts.get(lang, 0) + 1

        return language_counts

    def scan(self, target_path: str) -> dict:
        """Simple scan that just works"""
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Detect languages for better context
        languages_detected = self._detect_languages(target)

        cmd = [
            self.tool_path,
            "--config=auto",  # Use curated rulesets
            "--json",
            "--verbose",      # Get more rule information
            "--metrics=off",  # Disable telemetry
            str(target)
        ]

        # Add timeout and exclude common dirs
        cmd.extend([
            "--exclude=node_modules/",
            "--exclude=.git/",
            "--exclude=*.min.js",
            "--exclude=*.bundle.js"
        ])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                data = json.loads(result.stdout)
                results = self._process_results(data, target_path, languages_detected)
                self._save_results(results)
                return results
            else:
                empty_result = {
                    "findings": [],
                    "summary": {"total": 0, "languages_detected": languages_detected},
                    "target": target_path,
                    "tool": "semgrep",
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": self._generate_scan_id()
                }
                self._save_results(empty_result)
                return empty_result

        except Exception as e:
            raise RuntimeError(f"Semgrep scan failed: {e}")

    def _process_results(self, data: dict, target_path: str, languages_detected: Dict[str, int] = None) -> dict:
        """Process Semgrep results with enhanced metadata"""

        results = data.get("results", [])
        paths_scanned = data.get("paths", {})

        # Enhanced findings with normalized severity
        enhanced_findings = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        rule_categories = {}
        languages_with_findings = set()

        for finding in results:
            # Normalize severity
            original_severity = finding.get("extra", {}).get("severity", "INFO")
            normalized_severity = self.severity_mapping.get(original_severity.upper(), "medium")

            # Extract rule information
            check_id = finding.get("check_id", "unknown")
            rule_category = check_id.split(".")[0] if "." in check_id else "general"

            # Get file language
            file_path = finding.get("path", "")
            file_suffix = Path(file_path).suffix.lower()
            file_language = self.language_extensions.get(file_suffix, "unknown")

            enhanced_finding = {
                "check_id": check_id,
                "rule_category": rule_category,
                "message": finding.get("extra", {}).get("message", finding.get("check_id", "Security issue detected")),
                "severity": original_severity,
                "normalized_severity": normalized_severity,
                "file": file_path,
                "language": file_language,
                "line_start": finding.get("start", {}).get("line", 0),
                "line_end": finding.get("end", {}).get("line", 0),
                "column_start": finding.get("start", {}).get("col", 0),
                "column_end": finding.get("end", {}).get("col", 0),
                "fix": finding.get("extra", {}).get("fix", ""),
                "metadata": finding.get("extra", {}).get("metadata", {}),
                "owasp_category": finding.get("extra", {}).get("metadata", {}).get("owasp", ""),
                "cwe": finding.get("extra", {}).get("metadata", {}).get("cwe", [])
            }

            enhanced_findings.append(enhanced_finding)

            # Update counts
            severity_counts[normalized_severity] += 1
            rule_categories[rule_category] = rule_categories.get(rule_category, 0) + 1
            if file_language != "unknown":
                languages_with_findings.add(file_language)

        # Calculate scan statistics
        files_scanned = paths_scanned.get("scanned", [])

        return {
            "findings": enhanced_findings,
            "summary": {
                "total": len(enhanced_findings),
                "files_scanned": len(files_scanned),
                "rules_applied": len(set(r.get("check_id", "") for r in results)),
                "rule_categories": rule_categories,
                "severity_breakdown": severity_counts,
                "languages_detected": languages_detected or {},
                "languages_with_findings": list(languages_with_findings)
            },
            "target": target_path,
            "tool": "semgrep",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "metadata": {
                "semgrep_version": data.get("version", "unknown"),
                "scan_performance": {
                    "files_scanned": len(files_scanned),
                    "total_findings": len(enhanced_findings)
                }
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"semgrep_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

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

            print(f"🔍 Semgrep results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "semgrep_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")
            # Don't fail the scan because of save issues

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python semgrep_scanner.py <target_path>")
        print("Scans code for security issues using Semgrep's curated rulesets")
        sys.exit(1)

    scanner = SemgrepScanner()
    results = scanner.scan(sys.argv[1])

    print(f"🔍 Semgrep found {results['summary']['total']} code issues")

    if results['summary']['total'] > 0:
        print(f"   Files scanned: {results['summary']['files_scanned']}")
        print(f"   Rules applied: {results['summary']['rules_applied']}")

        # Show severity breakdown
        severity = results['summary']['severity_breakdown']
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")

        # Show top rule categories
        categories = results['summary']['rule_categories']
        if categories:
            print(f"   Top categories: {', '.join(list(categories.keys())[:3])}")