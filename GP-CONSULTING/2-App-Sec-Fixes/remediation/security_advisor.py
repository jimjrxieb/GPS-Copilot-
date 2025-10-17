#!/usr/bin/env python3
"""
Security Advisor - Practical Integration Between Scanners and Fixes
No AI hype, just direct scanner → issue → fix mapping
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from remediation.remediation_db import RemediationDB

class SecurityAdvisor:
    """Provides actual, actionable security advice based on scan results"""

    def __init__(self):
        self.remediation_db = RemediationDB()
        self.scan_dir = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans")

    def load_scan_results(self, scan_file: Path) -> dict:
        """Load scan results from JSON file"""
        try:
            with open(scan_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {scan_file}: {e}")
            return {}

    def analyze_bandit_results(self, results: dict) -> List[Dict]:
        """Analyze Bandit results and provide fixes"""
        recommendations = []

        for finding in results.get("findings", []):
            issue_id = finding.get("test_id")
            fix_info = self.remediation_db.get_fix("bandit", issue_id)

            recommendation = {
                "file": finding.get("file"),
                "line": finding.get("line"),
                "issue_id": issue_id,
                "severity": finding.get("severity"),
                "issue": finding.get("issue"),
                "risk": fix_info.get("risk"),
                "fix": fix_info.get("fix"),
                "references": fix_info.get("references", [])
            }
            recommendations.append(recommendation)

        return recommendations

    def analyze_semgrep_results(self, results: dict) -> List[Dict]:
        """Analyze Semgrep results and provide fixes"""
        recommendations = []

        for finding in results.get("findings", []):
            rule_id = finding.get("check_id", finding.get("rule_id"))
            fix_info = self.remediation_db.get_fix("semgrep", rule_id)

            recommendation = {
                "file": finding.get("path"),
                "line": finding.get("start", {}).get("line"),
                "issue_id": rule_id,
                "severity": finding.get("severity"),
                "issue": finding.get("message", fix_info.get("issue")),
                "risk": fix_info.get("risk"),
                "fix": fix_info.get("fix"),
                "references": fix_info.get("references", [])
            }
            recommendations.append(recommendation)

        return recommendations

    def analyze_checkov_results(self, results: dict) -> List[Dict]:
        """Analyze Checkov results and provide fixes"""
        recommendations = []

        # Handle both individual findings and results structure
        failed_checks = results.get("results", {}).get("failed_checks", [])
        if not failed_checks:
            failed_checks = results.get("failed_checks", [])

        for finding in failed_checks:
            check_id = finding.get("check_id")
            fix_info = self.remediation_db.get_fix("checkov", check_id)

            recommendation = {
                "file": finding.get("file_path"),
                "line": finding.get("file_line_range", [0])[0] if finding.get("file_line_range") else None,
                "issue_id": check_id,
                "severity": finding.get("severity", "unknown"),
                "issue": finding.get("check_name", fix_info.get("issue")),
                "risk": fix_info.get("risk"),
                "fix": fix_info.get("fix"),
                "references": fix_info.get("references", [])
            }
            recommendations.append(recommendation)

        return recommendations

    def analyze_trivy_results(self, results: dict) -> List[Dict]:
        """Analyze Trivy results and provide fixes"""
        recommendations = []

        # Handle different Trivy output formats
        vulnerabilities = []
        if "Results" in results:
            for result in results.get("Results", []):
                vulnerabilities.extend(result.get("Vulnerabilities", []))
        elif "vulnerabilities" in results:
            vulnerabilities = results.get("vulnerabilities", [])

        for vuln in vulnerabilities:
            vuln_id = vuln.get("VulnerabilityID", vuln.get("vulnerability_id"))
            fix_info = self.remediation_db.get_fix("trivy", vuln_id)

            recommendation = {
                "package": vuln.get("PkgName", vuln.get("package_name")),
                "version": vuln.get("InstalledVersion", vuln.get("installed_version")),
                "issue_id": vuln_id,
                "severity": vuln.get("Severity", vuln.get("severity")),
                "issue": vuln.get("Title", vuln.get("description", fix_info.get("issue"))),
                "risk": fix_info.get("risk"),
                "fix": fix_info.get("fix"),
                "references": fix_info.get("references", [])
            }
            recommendations.append(recommendation)

        return recommendations

    def analyze_gitleaks_results(self, results: dict) -> List[Dict]:
        """Analyze GitLeaks results and provide fixes"""
        recommendations = []

        for finding in results.get("findings", []):
            # Try to categorize the secret type
            secret_type = "generic-api-key"
            if "aws" in finding.get("rule", "").lower():
                secret_type = "aws-access-token"

            fix_info = self.remediation_db.get_fix("gitleaks", secret_type)

            recommendation = {
                "file": finding.get("file"),
                "line": finding.get("line"),
                "issue_id": finding.get("rule"),
                "severity": "critical",  # Secrets are always critical
                "issue": f"Secret found: {finding.get('rule', 'Unknown type')}",
                "risk": fix_info.get("risk"),
                "fix": fix_info.get("fix"),
                "references": fix_info.get("references", [])
            }
            recommendations.append(recommendation)

        return recommendations

    def analyze_scan_file(self, scan_file: Path) -> Dict:
        """Analyze any scan file and provide recommendations"""
        results = self.load_scan_results(scan_file)
        if not results:
            return {"error": "Could not load scan results"}

        # Detect scanner type
        scanner = results.get("tool", "unknown")

        # Map to appropriate analyzer
        analyzers = {
            "bandit": self.analyze_bandit_results,
            "semgrep": self.analyze_semgrep_results,
            "checkov": self.analyze_checkov_results,
            "trivy": self.analyze_trivy_results,
            "gitleaks": self.analyze_gitleaks_results
        }

        analyzer = analyzers.get(scanner)
        if not analyzer:
            return {
                "scanner": scanner,
                "error": f"No analyzer available for {scanner}",
                "recommendations": []
            }

        recommendations = analyzer(results)

        return {
            "scanner": scanner,
            "scan_file": str(scan_file),
            "timestamp": results.get("timestamp"),
            "total_issues": len(recommendations),
            "recommendations": recommendations
        }

    def get_latest_scan_for_project(self, project_path: str, scanner: Optional[str] = None) -> Optional[Path]:
        """Find the latest scan file for a project"""
        if not self.scan_dir.exists():
            return None

        scan_files = []
        pattern = f"{scanner}_*.json" if scanner else "*.json"

        for scan_file in self.scan_dir.glob(pattern):
            try:
                with open(scan_file) as f:
                    data = json.load(f)
                    if project_path in data.get("target", ""):
                        scan_files.append(scan_file)
            except:
                continue

        return max(scan_files, key=lambda f: f.stat().st_mtime) if scan_files else None

    def provide_advice_for_project(self, project_path: str) -> Dict:
        """Provide security advice for all scans of a project"""
        advice = {
            "project": project_path,
            "timestamp": datetime.now().isoformat(),
            "scanners": {},
            "summary": {
                "total_issues": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }

        # Check each scanner type
        scanners = ["bandit", "semgrep", "checkov", "trivy", "gitleaks"]

        for scanner in scanners:
            latest_scan = self.get_latest_scan_for_project(project_path, scanner)
            if latest_scan:
                analysis = self.analyze_scan_file(latest_scan)
                advice["scanners"][scanner] = analysis

                # Update summary
                for rec in analysis.get("recommendations", []):
                    advice["summary"]["total_issues"] += 1
                    severity = rec.get("severity", "unknown").lower()
                    if severity in advice["summary"]:
                        advice["summary"][severity] += 1

        return advice

def main():
    """Test the security advisor with real scan results"""
    advisor = SecurityAdvisor()

    # Test with DVWA project
    project = "/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/DVWA"

    print("🔍 Security Advisor - Practical Remediation System")
    print("=" * 60)
    print(f"Analyzing project: {project}")
    print()

    advice = advisor.provide_advice_for_project(project)

    print(f"📊 Summary:")
    print(f"   Total Issues: {advice['summary']['total_issues']}")
    print(f"   Critical: {advice['summary']['critical']}")
    print(f"   High: {advice['summary']['high']}")
    print(f"   Medium: {advice['summary']['medium']}")
    print(f"   Low: {advice['summary']['low']}")
    print()

    # Show detailed recommendations
    for scanner_name, scanner_results in advice["scanners"].items():
        if scanner_results.get("recommendations"):
            print(f"📋 {scanner_name.upper()} Findings:")
            for rec in scanner_results["recommendations"]:
                print(f"\n   Issue: {rec.get('issue')}")
                print(f"   File: {rec.get('file', rec.get('package', 'N/A'))}")
                print(f"   Severity: {rec.get('severity')}")
                print(f"   Risk: {rec.get('risk')}")
                print(f"   Fix: {rec.get('fix', 'No fix available')[:200]}...")
                if rec.get('references'):
                    print(f"   References: {', '.join(rec['references'])}")

    # Save full report
    report_file = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/reports") / f"security_advice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w') as f:
        json.dump(advice, f, indent=2)

    print(f"\n📝 Full report saved: {report_file}")

if __name__ == "__main__":
    main()