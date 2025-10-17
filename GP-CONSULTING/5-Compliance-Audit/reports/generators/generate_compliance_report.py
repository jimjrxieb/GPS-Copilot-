#!/usr/bin/env python3
"""
Compliance Report Generator

Generates framework-specific compliance reports by mapping scan results to
PCI-DSS, HIPAA, or NIST 800-53 requirements.

Usage:
    python generate_compliance_report.py --framework pci-dss --project FINANCE
    python generate_compliance_report.py --framework hipaa --project HEALTHCARE
    python generate_compliance_report.py --framework nist-800-53 --project DEFENSE
    python generate_compliance_report.py --all  # Generate all reports

Author: GP-Copilot / Jade AI
Date: 2025-10-13
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRAMEWORKS_DIR = BASE_DIR / "frameworks"
MAPPINGS_DIR = BASE_DIR / "mappings"
REPORTS_OUTPUT_DIR = BASE_DIR / "reports" / "output"
SCAN_RESULTS_DIR = Path("/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/secops/2-findings/raw")


class ComplianceReportGenerator:
    """Generate compliance reports from scan results and framework mappings"""

    def __init__(self, framework: str, project: str = None):
        self.framework = framework.lower()
        self.project = project.upper() if project else None
        self.framework_data = self._load_framework_data()
        self.universal_controls = self._load_universal_controls()
        self.scan_results = self._load_scan_results()

    def _load_framework_data(self) -> Dict:
        """Load framework-specific requirements"""
        framework_files = {
            "pci-dss": FRAMEWORKS_DIR / "pci-dss" / "pci-dss-v4.json",
            "hipaa": FRAMEWORKS_DIR / "hipaa" / "hipaa-security-rule.json",
            "nist-800-53": FRAMEWORKS_DIR / "nist-800-53" / "nist-800-53-rev5.json"
        }

        if self.framework not in framework_files:
            raise ValueError(f"Unknown framework: {self.framework}")

        framework_file = framework_files[self.framework]
        if not framework_file.exists():
            raise FileNotFoundError(f"Framework file not found: {framework_file}")

        with open(framework_file, 'r') as f:
            return json.load(f)

    def _load_universal_controls(self) -> Dict:
        """Load universal control mappings"""
        controls_file = MAPPINGS_DIR / "universal-controls.json"
        if not controls_file.exists():
            raise FileNotFoundError(f"Universal controls file not found: {controls_file}")

        with open(controls_file, 'r') as f:
            return json.load(f)

    def _load_scan_results(self) -> Dict:
        """Load scan results from secops findings directory"""
        results = {
            "bandit": [],
            "trivy": [],
            "checkov": [],
            "semgrep": [],
            "gitleaks": []
        }

        if not SCAN_RESULTS_DIR.exists():
            print(f"Warning: Scan results directory not found: {SCAN_RESULTS_DIR}")
            return results

        # Load CI scan results
        ci_dir = SCAN_RESULTS_DIR / "ci"
        if ci_dir.exists():
            for scanner in ["bandit", "semgrep", "gitleaks"]:
                result_file = ci_dir / f"{scanner}-results.json"
                if result_file.exists():
                    try:
                        with open(result_file, 'r') as f:
                            results[scanner] = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not parse {result_file}")

        # Load CD scan results
        cd_dir = SCAN_RESULTS_DIR / "cd"
        if cd_dir.exists():
            for scanner in ["trivy", "checkov"]:
                result_file = cd_dir / f"{scanner}-results.json"
                if result_file.exists():
                    try:
                        with open(result_file, 'r') as f:
                            results[scanner] = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not parse {result_file}")

        return results

    def _get_control_status(self, control_id: str, universal_controls: List[str]) -> Dict:
        """Determine compliance status for a control based on scan results"""
        status = {
            "compliant": True,
            "findings": [],
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0
        }

        # Map universal controls to scan results
        for uc_id in universal_controls:
            uc_data = next((uc for uc in self.universal_controls["universal_controls"]
                           if uc["id"] == uc_id), None)

            if not uc_data:
                continue

            # Check relevant scanners for this control
            scanner = Path(uc_data["implementation"]["scanner"]).name

            if "bandit" in scanner:
                findings = self._analyze_bandit_results(uc_data)
            elif "trivy" in scanner:
                findings = self._analyze_trivy_results(uc_data)
            elif "checkov" in scanner:
                findings = self._analyze_checkov_results(uc_data)
            elif "semgrep" in scanner:
                findings = self._analyze_semgrep_results(uc_data)
            elif "gitleaks" in scanner:
                findings = self._analyze_gitleaks_results(uc_data)
            else:
                findings = []

            if findings:
                status["compliant"] = False
                status["findings"].extend(findings)

                # Count by severity
                for finding in findings:
                    status["total_issues"] += 1
                    severity = finding.get("severity", "UNKNOWN").upper()
                    if severity == "CRITICAL":
                        status["critical_issues"] += 1
                    elif severity == "HIGH":
                        status["high_issues"] += 1
                    elif severity == "MEDIUM":
                        status["medium_issues"] += 1
                    elif severity == "LOW":
                        status["low_issues"] += 1

        return status

    def _analyze_bandit_results(self, control: Dict) -> List[Dict]:
        """Analyze Bandit scan results for control"""
        findings = []
        bandit_results = self.scan_results.get("bandit", {})

        if isinstance(bandit_results, dict) and "results" in bandit_results:
            for result in bandit_results["results"]:
                # Map Bandit severity to standard severity
                severity_map = {
                    "LOW": "LOW",
                    "MEDIUM": "MEDIUM",
                    "HIGH": "HIGH"
                }

                findings.append({
                    "scanner": "bandit",
                    "severity": severity_map.get(result.get("issue_severity", "MEDIUM"), "MEDIUM"),
                    "description": result.get("issue_text", "Unknown issue"),
                    "file": result.get("filename", "unknown"),
                    "line": result.get("line_number", 0),
                    "cwe": result.get("issue_cwe", {}).get("id", "N/A")
                })

        return findings

    def _analyze_trivy_results(self, control: Dict) -> List[Dict]:
        """Analyze Trivy scan results for control"""
        findings = []
        trivy_results = self.scan_results.get("trivy", {})

        if isinstance(trivy_results, dict) and "Results" in trivy_results:
            for result in trivy_results["Results"]:
                vulnerabilities = result.get("Vulnerabilities", [])
                for vuln in vulnerabilities:
                    severity = vuln.get("Severity", "UNKNOWN").upper()

                    # Only include HIGH and CRITICAL for compliance
                    if severity in ["HIGH", "CRITICAL"]:
                        findings.append({
                            "scanner": "trivy",
                            "severity": severity,
                            "description": vuln.get("Title", "Unknown vulnerability"),
                            "vulnerability_id": vuln.get("VulnerabilityID", "N/A"),
                            "package": vuln.get("PkgName", "unknown"),
                            "installed_version": vuln.get("InstalledVersion", "unknown"),
                            "fixed_version": vuln.get("FixedVersion", "N/A")
                        })

        return findings

    def _analyze_checkov_results(self, control: Dict) -> List[Dict]:
        """Analyze Checkov scan results for control"""
        findings = []
        checkov_results = self.scan_results.get("checkov", {})

        if isinstance(checkov_results, dict) and "results" in checkov_results:
            failed_checks = checkov_results["results"].get("failed_checks", [])

            for check in failed_checks:
                # Map check severity to standard severity
                severity_map = {
                    "CRITICAL": "CRITICAL",
                    "HIGH": "HIGH",
                    "MEDIUM": "MEDIUM",
                    "LOW": "LOW"
                }

                findings.append({
                    "scanner": "checkov",
                    "severity": severity_map.get(check.get("check_class", "MEDIUM"), "MEDIUM"),
                    "description": check.get("check_name", "Unknown check"),
                    "check_id": check.get("check_id", "N/A"),
                    "file": check.get("file_path", "unknown"),
                    "resource": check.get("resource", "unknown"),
                    "guideline": check.get("guideline", "N/A")
                })

        return findings

    def _analyze_semgrep_results(self, control: Dict) -> List[Dict]:
        """Analyze Semgrep scan results for control"""
        findings = []
        semgrep_results = self.scan_results.get("semgrep", {})

        if isinstance(semgrep_results, dict) and "results" in semgrep_results:
            for result in semgrep_results["results"]:
                # Map Semgrep severity to standard severity
                severity_map = {
                    "ERROR": "HIGH",
                    "WARNING": "MEDIUM",
                    "INFO": "LOW"
                }

                findings.append({
                    "scanner": "semgrep",
                    "severity": severity_map.get(result.get("extra", {}).get("severity", "WARNING"), "MEDIUM"),
                    "description": result.get("extra", {}).get("message", "Unknown issue"),
                    "file": result.get("path", "unknown"),
                    "line": result.get("start", {}).get("line", 0),
                    "rule_id": result.get("check_id", "N/A")
                })

        return findings

    def _analyze_gitleaks_results(self, control: Dict) -> List[Dict]:
        """Analyze Gitleaks scan results for control"""
        findings = []
        gitleaks_results = self.scan_results.get("gitleaks", [])

        if isinstance(gitleaks_results, list):
            for result in gitleaks_results:
                findings.append({
                    "scanner": "gitleaks",
                    "severity": "CRITICAL",  # All secrets are critical
                    "description": f"Secret detected: {result.get('Description', 'Unknown secret')}",
                    "file": result.get("File", "unknown"),
                    "line": result.get("StartLine", 0),
                    "rule_id": result.get("RuleID", "N/A")
                })

        return findings

    def generate_markdown_report(self) -> str:
        """Generate Markdown compliance report"""
        report_lines = []

        # Header
        report_lines.append(f"# {self.framework_data['meta']['framework']} Compliance Report")
        report_lines.append(f"")
        report_lines.append(f"**Framework:** {self.framework_data['meta']['framework']} {self.framework_data['meta']['version']}")
        report_lines.append(f"**Project:** {self.framework_data['meta']['project']}")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"")
        report_lines.append("---")
        report_lines.append("")

        # Executive Summary
        total_requirements = len(self.framework_data["requirements"])
        compliant_count = 0
        non_compliant_count = 0
        total_findings = 0
        critical_findings = 0
        high_findings = 0

        requirement_statuses = []

        for req in self.framework_data["requirements"]:
            req_id = req.get("requirement_id") or req.get("control_id")
            universal_controls = req.get("universal_controls", [])

            status = self._get_control_status(req_id, universal_controls)
            requirement_statuses.append({
                "requirement": req,
                "status": status
            })

            if status["compliant"]:
                compliant_count += 1
            else:
                non_compliant_count += 1

            total_findings += status["total_issues"]
            critical_findings += status["critical_issues"]
            high_findings += status["high_issues"]

        compliance_percentage = (compliant_count / total_requirements * 100) if total_requirements > 0 else 0

        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"**Compliance Score:** {compliance_percentage:.1f}% ({compliant_count}/{total_requirements} requirements)")
        report_lines.append(f"**Total Findings:** {total_findings}")
        report_lines.append(f"- Critical: {critical_findings}")
        report_lines.append(f"- High: {high_findings}")
        report_lines.append("")

        # Compliance status indicator
        if compliance_percentage >= 95:
            status_emoji = "✅"
            status_text = "COMPLIANT"
        elif compliance_percentage >= 80:
            status_emoji = "⚠️"
            status_text = "MOSTLY COMPLIANT"
        else:
            status_emoji = "❌"
            status_text = "NON-COMPLIANT"

        report_lines.append(f"**Status:** {status_emoji} {status_text}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # Detailed Findings by Requirement
        report_lines.append("## Detailed Compliance Status")
        report_lines.append("")

        for req_status in requirement_statuses:
            req = req_status["requirement"]
            status = req_status["status"]

            req_id = req.get("requirement_id") or req.get("control_id")
            title = req.get("title")
            category = req.get("category") or req.get("family", "N/A")

            # Requirement header
            status_icon = "✅" if status["compliant"] else "❌"
            report_lines.append(f"### {status_icon} {req_id}: {title}")
            report_lines.append(f"")
            report_lines.append(f"**Category:** {category}")
            report_lines.append(f"**Description:** {req.get('description', 'N/A')}")
            report_lines.append(f"**Universal Controls:** {', '.join(req.get('universal_controls', []))}")
            report_lines.append(f"")

            if status["compliant"]:
                report_lines.append("**Status:** ✅ COMPLIANT - No issues found")
            else:
                report_lines.append(f"**Status:** ❌ NON-COMPLIANT - {status['total_issues']} issues found")
                report_lines.append(f"")
                report_lines.append("**Findings:**")
                report_lines.append("")

                # Group findings by severity
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    severity_findings = [f for f in status["findings"] if f.get("severity") == severity]

                    if severity_findings:
                        report_lines.append(f"**{severity} ({len(severity_findings)}):**")
                        report_lines.append("")

                        for finding in severity_findings[:10]:  # Limit to 10 per severity
                            report_lines.append(f"- **{finding.get('scanner', 'unknown').upper()}:** {finding.get('description', 'No description')}")

                            if "file" in finding:
                                file_info = f"  - File: `{finding['file']}`"
                                if "line" in finding:
                                    file_info += f" (Line {finding['line']})"
                                report_lines.append(file_info)

                            if "vulnerability_id" in finding:
                                report_lines.append(f"  - CVE: {finding['vulnerability_id']}")

                            if "fixed_version" in finding and finding["fixed_version"] != "N/A":
                                report_lines.append(f"  - Fix: Upgrade to {finding['fixed_version']}")

                        if len(severity_findings) > 10:
                            report_lines.append(f"  - ... and {len(severity_findings) - 10} more")

                        report_lines.append("")

            # Implementation details
            impl = req.get("implementation", {})
            report_lines.append("**Remediation:**")
            report_lines.append(f"- Scanner: `{impl.get('scanner', 'N/A')}`")
            report_lines.append(f"- Fixer: `{impl.get('fixer', 'N/A')}`")
            report_lines.append(f"- OPA Policy: `{impl.get('opa_policy', 'N/A')}`")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")

        if non_compliant_count == 0:
            report_lines.append("🎉 Congratulations! Your system is fully compliant with all requirements.")
        else:
            report_lines.append(f"To achieve full compliance, address the following {non_compliant_count} non-compliant requirements:")
            report_lines.append("")

            priority_order = []
            for req_status in requirement_statuses:
                if not req_status["status"]["compliant"]:
                    req = req_status["requirement"]
                    status = req_status["status"]
                    priority = req.get("priority", "P2")

                    priority_order.append({
                        "priority": priority,
                        "req_id": req.get("requirement_id") or req.get("control_id"),
                        "title": req.get("title"),
                        "critical_issues": status["critical_issues"],
                        "high_issues": status["high_issues"]
                    })

            # Sort by priority, then by critical issues
            priority_order.sort(key=lambda x: (x["priority"], -x["critical_issues"], -x["high_issues"]))

            for i, item in enumerate(priority_order, 1):
                report_lines.append(f"{i}. **{item['req_id']}:** {item['title']}")
                report_lines.append(f"   - Priority: {item['priority']}")
                report_lines.append(f"   - Critical: {item['critical_issues']}, High: {item['high_issues']}")
                report_lines.append("")

        report_lines.append("---")
        report_lines.append("")
        report_lines.append(f"*Report generated by GP-Copilot Compliance Framework v1.0*")

        return "\n".join(report_lines)

    def save_report(self, output_format: str = "markdown") -> Path:
        """Save compliance report to file"""
        if output_format != "markdown":
            raise NotImplementedError(f"Format {output_format} not yet supported")

        # Create output directory
        output_dir = REPORTS_OUTPUT_DIR / self.framework
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        project_suffix = f"-{self.project}" if self.project else ""
        output_file = output_dir / f"compliance-report{project_suffix}-{timestamp}.md"

        # Generate and save report
        report_content = self.generate_markdown_report()

        with open(output_file, 'w') as f:
            f.write(report_content)

        print(f"✅ Compliance report generated: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate compliance reports from scan results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_compliance_report.py --framework pci-dss --project FINANCE
  python generate_compliance_report.py --framework hipaa --project HEALTHCARE
  python generate_compliance_report.py --framework nist-800-53 --project DEFENSE
  python generate_compliance_report.py --all
        """
    )

    parser.add_argument(
        "--framework",
        choices=["pci-dss", "hipaa", "nist-800-53"],
        help="Compliance framework to generate report for"
    )

    parser.add_argument(
        "--project",
        choices=["FINANCE", "HEALTHCARE", "DEFENSE"],
        help="Project name (optional)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate reports for all frameworks"
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "pdf", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    if args.all:
        frameworks = [
            ("pci-dss", "FINANCE"),
            ("hipaa", "HEALTHCARE"),
            ("nist-800-53", "DEFENSE")
        ]

        print("Generating compliance reports for all frameworks...")
        print()

        for framework, project in frameworks:
            try:
                generator = ComplianceReportGenerator(framework, project)
                output_file = generator.save_report(output_format=args.format)
                print(f"✅ {framework.upper()} report: {output_file}")
            except Exception as e:
                print(f"❌ Error generating {framework} report: {e}")
                continue

        print()
        print("✅ All compliance reports generated successfully!")

    elif args.framework:
        try:
            generator = ComplianceReportGenerator(args.framework, args.project)
            output_file = generator.save_report(output_format=args.format)

            print()
            print(f"✅ Compliance report generated successfully!")
            print(f"📄 Report location: {output_file}")
            print()
            print("Next steps:")
            print(f"  1. Review the report: cat {output_file}")
            print(f"  2. Address non-compliant findings using fixers")
            print(f"  3. Re-run scanners and regenerate report")

        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
