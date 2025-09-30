#!/usr/bin/env python3
"""
Gitleaks Scanner - Clean, Simple, Working
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
import shutil  # For checking if gitleaks is installed

class GitleaksScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Try system gitleaks first, fallback to local binary
        if shutil.which("gitleaks"):
            self.tool_path = "gitleaks"
        else:
            # Updated path to actual GP-copilot binary location
            self.tool_path = "/home/jimmie/linkops-industries/GP-copilot/bin/gitleaks"

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Gitleaks severity mapping
        self.severity_mapping = {
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "low",
            "critical": "critical"
        }

        # Scan modes
        self.scan_modes = {
            "detect": "scan current state of files",
            "protect": "scan staged changes",
            "history": "scan entire git history"
        }

    def _is_git_repo(self, target: Path) -> bool:
        """Check if target is a git repository"""
        git_dir = target / ".git"
        if git_dir.exists():
            return True

        # Check if we're inside a git repo (subdirectory)
        current = target.resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return True
            current = current.parent

        return False

    def _get_repo_info(self, target: Path) -> dict:
        """Get git repository information"""
        try:
            # Get current branch
            branch_cmd = ["git", "-C", str(target), "rev-parse", "--abbrev-ref", "HEAD"]
            branch_result = subprocess.run(branch_cmd, capture_output=True, text=True, timeout=10)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Get commit count
            count_cmd = ["git", "-C", str(target), "rev-list", "--count", "HEAD"]
            count_result = subprocess.run(count_cmd, capture_output=True, text=True, timeout=10)
            commit_count = int(count_result.stdout.strip()) if count_result.returncode == 0 else 0

            return {
                "current_branch": current_branch,
                "commit_count": commit_count,
                "is_git_repo": True
            }
        except Exception:
            return {"is_git_repo": False}

    def scan(self, target_path: str, scan_mode: str = "detect", include_history: bool = False) -> dict:
        """
        Scan for secrets with flexible modes

        Args:
            target_path: Directory or file to scan
            scan_mode: 'detect' (current state), 'protect' (staged), 'history' (full git history)
            include_history: If True, also scan git history (slower but more thorough)
        """
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Check if it's a git repo for better context
        repo_info = self._get_repo_info(target)

        cmd = [self.tool_path]

        # Choose scan mode based on context and parameters
        if include_history or scan_mode == "history":
            if repo_info.get("is_git_repo", False):
                cmd.extend(["detect", "--source", str(target)])
                # Gitleaks will automatically scan history in git repos
            else:
                # Not a git repo, fall back to file scanning
                cmd.extend(["detect", "--no-git", "--source", str(target)])
        elif scan_mode == "protect":
            if repo_info.get("is_git_repo", False):
                cmd.extend(["protect", "--source", str(target)])
            else:
                # Fall back to detect mode for non-git
                cmd.extend(["detect", "--no-git", "--source", str(target)])
        else:  # detect mode (default)
            if repo_info.get("is_git_repo", False):
                cmd.extend(["detect", "--source", str(target)])
            else:
                cmd.extend(["detect", "--no-git", "--source", str(target)])

        # Add output format
        cmd.extend(["--report-format", "json"])

        # Add verbose mode for better error reporting
        cmd.append("--verbose")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                data = json.loads(result.stdout)
                results = self._process_results(data, target_path, scan_mode, repo_info)
                self._save_results(results)
                return results
            else:
                # No secrets found
                empty_result = {
                    "findings": [],
                    "summary": {"total": 0, "secrets_found": 0},
                    "target": target_path,
                    "tool": "gitleaks",
                    "scan_mode": scan_mode,
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": self._generate_scan_id(),
                    "repo_info": repo_info
                }
                self._save_results(empty_result)
                return empty_result

        except json.JSONDecodeError:
            # No secrets found
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "secrets_found": 0},
                "target": target_path,
                "tool": "gitleaks",
                "scan_mode": scan_mode,
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id(),
                "repo_info": self._get_repo_info(target)
            }
            self._save_results(empty_result)
            return empty_result
        except Exception as e:
            raise RuntimeError(f"Gitleaks scan failed: {e}")

    def _process_results(self, data: list, target_path: str, scan_mode: str = "detect", repo_info: dict = None) -> dict:
        """Process Gitleaks results with enhanced metadata"""

        if not data:
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "secrets_found": 0},
                "target": target_path,
                "tool": "gitleaks",
                "scan_mode": scan_mode,
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id(),
                "repo_info": repo_info or {}
            }
            return empty_result

        # Enhance each finding
        enhanced_findings = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for finding in data:
            # Normalize severity
            original_severity = finding.get("RuleID", "").lower()
            # Map common Gitleaks rules to severity
            if any(keyword in original_severity for keyword in ['api', 'key', 'secret', 'token']):
                normalized_severity = "high"
            elif any(keyword in original_severity for keyword in ['password', 'private']):
                normalized_severity = "critical"
            else:
                normalized_severity = "medium"

            finding["normalized_severity"] = normalized_severity
            severity_counts[normalized_severity] += 1

            # Clean file paths
            if "File" in finding:
                try:
                    abs_file_path = Path(finding["File"])
                    target_path_obj = Path(target_path)
                    finding["relative_file_path"] = str(abs_file_path.relative_to(target_path_obj))
                except ValueError:
                    finding["relative_file_path"] = finding["File"]

            # Add metadata
            finding["secret_type"] = finding.get("RuleID", "unknown")
            finding["line_number"] = finding.get("StartLine", 0)
            finding["column"] = finding.get("StartColumn", 0)

            enhanced_findings.append(finding)

        # Group findings by secret type
        secret_types = {}
        for finding in enhanced_findings:
            secret_type = finding.get("secret_type", "unknown")
            if secret_type not in secret_types:
                secret_types[secret_type] = 0
            secret_types[secret_type] += 1

        return {
            "findings": enhanced_findings,
            "summary": {
                "total": len(enhanced_findings),
                "secrets_found": len(enhanced_findings),
                "severity_breakdown": severity_counts,
                "secret_types": secret_types,
                "scan_mode": scan_mode
            },
            "target": target_path,
            "tool": "gitleaks",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "repo_info": repo_info or {},
            "metadata": {
                "git_repo_detected": repo_info.get("is_git_repo", False) if repo_info else False,
                "scan_mode_used": scan_mode
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"gitleaks_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

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

            print(f"🔐 Gitleaks results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "gitleaks_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")
            # Don't fail the scan because of save issues

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python gitleaks_scanner.py <target_path> [scan_mode] [--include-history]")
        print("Scan modes: detect (default), protect, history")
        sys.exit(1)

    target_path = sys.argv[1]
    scan_mode = sys.argv[2] if len(sys.argv) > 2 else "detect"
    include_history = "--include-history" in sys.argv

    scanner = GitleaksScanner()
    results = scanner.scan(target_path, scan_mode, include_history)
    print(f"🔐 Gitleaks found {results['summary']['total']} secrets")

    # Show breakdown
    if results['summary']['total'] > 0:
        severity = results['summary'].get('severity_breakdown', {})
        print(f"   Critical: {severity.get('critical', 0)}")
        print(f"   High: {severity.get('high', 0)}")
        print(f"   Medium: {severity.get('medium', 0)}")
        print(f"   Low: {severity.get('low', 0)}")