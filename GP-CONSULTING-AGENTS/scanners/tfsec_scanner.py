#!/usr/bin/env python3
"""
TFSec Scanner - Clean, Simple, Working
Single-purpose scanner for Terraform security analysis
"""

import json
import subprocess
import shutil
from pathlib import Path
import sys
from datetime import datetime
# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig
from typing import Dict, Any, List, Optional

class TfsecScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Try system tfsec first, fallback to local binary
        if shutil.which("tfsec"):
            self.tool_path = "tfsec"
        else:
            local_tfsec = Path("/home/jimmie/linkops-industries/GP-copilot/bin/tfsec")
            if local_tfsec.exists():
                self.tool_path = str(local_tfsec)
            else:
                # Try guidepoint location
                guidepoint_tfsec = Path("/home/jimmie/linkops-industries/James-OS/guidepoint/bin/tfsec")
                if guidepoint_tfsec.exists():
                    self.tool_path = str(guidepoint_tfsec)
                else:
                    raise RuntimeError(
                        "tfsec not found. Install with:\n"
                        "curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash"
                    )

        # Standard data persistence
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # TFSec severity mapping (they use different levels)
        self.severity_mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "error": "high",      # tfsec sometimes uses "error"
            "warning": "medium",  # tfsec sometimes uses "warning"
            "info": "low"
        }

    def _detect_terraform_context(self, target: Path) -> dict:
        """Analyze Terraform project structure"""
        tf_files = list(target.glob("**/*.tf"))
        tfvars_files = list(target.glob("**/*.tfvars"))

        # Look for common Terraform patterns
        has_main = any(f.name == "main.tf" for f in tf_files)
        has_variables = any(f.name == "variables.tf" for f in tf_files)
        has_outputs = any(f.name == "outputs.tf" for f in tf_files)
        has_terraform_dir = (target / ".terraform").exists()
        has_state_file = any(target.glob("*.tfstate*"))

        # Try to detect providers
        providers = set()
        for tf_file in tf_files[:10]:  # Sample first 10 files
            try:
                with open(tf_file, 'r') as f:
                    content = f.read().lower()
                    if 'provider "aws"' in content:
                        providers.add("aws")
                    if 'provider "azure"' in content or 'provider "azurerm"' in content:
                        providers.add("azure")
                    if 'provider "google"' in content:
                        providers.add("gcp")
                    if 'provider "kubernetes"' in content:
                        providers.add("kubernetes")
            except Exception:
                continue

        return {
            "terraform_files_count": len(tf_files),
            "tfvars_files_count": len(tfvars_files),
            "has_main_tf": has_main,
            "has_variables_tf": has_variables,
            "has_outputs_tf": has_outputs,
            "has_terraform_directory": has_terraform_dir,
            "has_state_files": has_state_file,
            "providers_detected": list(providers),
            "terraform_files": [str(f.relative_to(target)) for f in tf_files]
        }

    def scan(self, target_path: str) -> dict:
        """Run tfsec scan with standardized output format"""
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Detect Terraform context
        tf_context = self._detect_terraform_context(target)

        if tf_context["terraform_files_count"] == 0:
            empty_result = {
                "findings": [],
                "summary": {"total": 0, "message": "No Terraform files found"},
                "target": target_path,
                "tool": "tfsec",
                "timestamp": datetime.now().isoformat(),
                "scan_id": self._generate_scan_id(),
                "terraform_context": tf_context
            }
            self._save_results(empty_result)
            return empty_result

        cmd = [self.tool_path, str(target_path), "-f", "json", "--no-color"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            # tfsec returns non-zero on findings, which is expected
            if result.stdout and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    results = self._process_tfsec_results(data, target_path, tf_context)
                    self._save_results(results)
                    return results
                except json.JSONDecodeError:
                    # Sometimes tfsec outputs non-JSON when there are no issues
                    no_findings_result = {
                        "findings": [],
                        "summary": {"total": 0, "terraform_files_scanned": tf_context["terraform_files_count"]},
                        "target": target_path,
                        "tool": "tfsec",
                        "timestamp": datetime.now().isoformat(),
                        "scan_id": self._generate_scan_id(),
                        "terraform_context": tf_context
                    }
                    self._save_results(no_findings_result)
                    return no_findings_result
            else:
                # No findings
                no_findings_result = {
                    "findings": [],
                    "summary": {"total": 0, "terraform_files_scanned": tf_context["terraform_files_count"]},
                    "target": target_path,
                    "tool": "tfsec",
                    "timestamp": datetime.now().isoformat(),
                    "scan_id": self._generate_scan_id(),
                    "terraform_context": tf_context
                }
                self._save_results(no_findings_result)
                return no_findings_result

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"TFSec scan timed out after 180 seconds")
        except Exception as e:
            raise RuntimeError(f"TFSec scan failed: {e}")

    def _process_tfsec_results(self, data: dict, target_path: str, tf_context: dict) -> dict:
        """Process TFSec results into standardized format"""
        raw_findings = data.get('results', [])

        enhanced_findings = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        rule_categories = {}
        providers_with_issues = set()

        for finding in raw_findings:
            # Normalize severity
            original_severity = finding.get('severity', 'medium').lower()
            normalized_severity = self.severity_mapping.get(original_severity, "medium")

            # Extract rule category
            rule_id = finding.get('rule_id', 'unknown')
            rule_category = rule_id.split('-')[0] if '-' in rule_id else 'general'

            # Determine provider from rule or resource
            provider = finding.get('rule_provider', 'terraform')
            if not provider or provider == 'terraform':
                # Try to extract from rule_id (e.g., "aws-s3-bucket-encryption")
                if rule_id.startswith(('aws-', 'azure-', 'gcp-', 'google-')):
                    provider = rule_id.split('-')[0]

            enhanced_finding = {
                "rule_id": rule_id,
                "rule_category": rule_category,
                "severity": original_severity,
                "normalized_severity": normalized_severity,
                "title": finding.get('description', 'Terraform security issue'),
                "message": finding.get('description', 'Terraform security issue'),
                "file": finding.get('location', {}).get('filename', 'unknown'),
                "line_start": finding.get('location', {}).get('start_line', 0),
                "line_end": finding.get('location', {}).get('end_line', 0),
                "impact": finding.get('impact', ''),
                "resolution": finding.get('resolution', ''),
                "resource": finding.get('resource', ''),
                "provider": provider,
                "links": finding.get('links', [])
            }

            enhanced_findings.append(enhanced_finding)
            severity_counts[normalized_severity] += 1
            rule_categories[rule_category] = rule_categories.get(rule_category, 0) + 1
            providers_with_issues.add(provider)

        return {
            "findings": enhanced_findings,
            "summary": {
                "total": len(enhanced_findings),
                "terraform_files_scanned": tf_context["terraform_files_count"],
                "severity_breakdown": severity_counts,
                "rule_categories": rule_categories,
                "providers_with_issues": list(providers_with_issues),
                "providers_detected": tf_context["providers_detected"]
            },
            "target": target_path,
            "tool": "tfsec",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "terraform_context": tf_context,
            "metadata": {
                "tfsec_version": "latest",  # Could extract from --version
                "scan_performance": {
                    "files_scanned": tf_context["terraform_files_count"],
                    "total_findings": len(enhanced_findings)
                }
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"tfsec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

    def _save_results(self, results: dict):
        """Save scan results to persistent storage"""
        scan_id = results.get("scan_id", self._generate_scan_id())
        filename = f"{scan_id}.json"

        output_file = self.output_dir / filename
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"🏗️ TFSec results saved to: {output_file}")

            # Also save a latest.json for easy access
            latest_file = self.output_dir / "tfsec_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python tfsec_scanner.py <target_path>")
        print("Scans Terraform files for security issues using tfsec")
        sys.exit(1)

    scanner = TfsecScanner()
    results = scanner.scan(sys.argv[1])

    print(f"🏗️ TFSec found {results['summary']['total']} issues")

    if results['summary']['total'] > 0:
        print(f"   Terraform files scanned: {results['summary']['terraform_files_scanned']}")

        # Show severity breakdown
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity['critical']}")
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")

        # Show providers with issues
        if results['summary'].get('providers_with_issues'):
            print(f"   Providers with issues: {', '.join(results['summary']['providers_with_issues'])}")