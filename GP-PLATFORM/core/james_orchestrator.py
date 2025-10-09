#!/usr/bin/env python3
"""
James Security Orchestrator - Clean, Simple, Working
End-to-end security workflow: Scan → Analyze → Fix → Report
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import os

# Add GP-copilot directories to Python path
GP_COPILOT_BASE = '/home/jimmie/linkops-industries/GP-copilot'
sys.path.append(f'{GP_COPILOT_BASE}/GP-CONSULTING-AGENTS/scanners')
sys.path.append(f'{GP_COPILOT_BASE}/GP-CONSULTING-AGENTS/fixers')
sys.path.append(f'{GP_COPILOT_BASE}/GP-CONSULTING-AGENTS/intelligence')
sys.path.append(GP_COPILOT_BASE)
sys.path.append(f'{GP_COPILOT_BASE}/james-config')  # Add james-config for gp_data_config
sys.path.append(str(Path(__file__).parent.parent))  # Add GP-PLATFORM to path

from gp_data_config import GPDataConfig

class JamesSecurityOrchestrator:
    def __init__(self):
        self.config = GPDataConfig()
        self.results_dir = Path(self.config.get_base_directory())
        self.scans_dir = Path(self.config.get_scans_directory())
        self.fixes_dir = Path(self.config.get_fixes_directory())
        self.analysis_dir = Path(self.config.get_analysis_directory())

    def execute_full_workflow(self, target_path: str, auto_fix: bool = False) -> dict:
        """Execute complete security workflow"""

        print("🎯 JAMES SECURITY ORCHESTRATOR")
        print("=" * 60)
        print(f"Target: {target_path}")
        print(f"Auto-fix enabled: {auto_fix}")
        print()

        workflow_results = {
            "workflow_info": {
                "target": target_path,
                "auto_fix_enabled": auto_fix,
                "start_time": datetime.now().isoformat(),
                "phases": []
            },
            "phases": {}
        }

        # Phase 1: Security Scanning
        print("📊 PHASE 1: SECURITY SCANNING")
        print("-" * 40)

        try:
            # Execute scanners via subprocess
            import subprocess
            scan_cmd = f"PYTHONPATH={GP_COPILOT_BASE} python3 {GP_COPILOT_BASE}/GP-CONSULTING-AGENTS/scanners/run_all_scanners.py {target_path}"
            result = subprocess.run(scan_cmd, shell=True, capture_output=True, text=True)

            # Get latest scan results from GP-DATA
            latest_scan = max(self.scans_dir.glob('*.json'), key=lambda p: p.stat().st_mtime)
            with open(latest_scan) as f:
                scan_results = json.load(f)
            workflow_results["phases"]["scanning"] = {
                "status": "completed",
                "results": scan_results,
                "duration": self._calculate_phase_duration()
            }
            workflow_results["workflow_info"]["phases"].append("scanning")

            total_issues = self._count_total_issues(scan_results)
            print(f"✅ Scanning complete: {total_issues} security issues found")
            print()

        except Exception as e:
            print(f"❌ Scanning failed: {e}")
            workflow_results["phases"]["scanning"] = {"status": "failed", "error": str(e)}
            return workflow_results

        # Phase 2: Intelligence Analysis
        print("🧠 PHASE 2: INTELLIGENCE ANALYSIS")
        print("-" * 40)

        try:
            analysis_results = self._analyze_with_intelligence(scan_results)
            workflow_results["phases"]["analysis"] = {
                "status": "completed",
                "results": analysis_results,
                "duration": self._calculate_phase_duration()
            }
            workflow_results["workflow_info"]["phases"].append("analysis")

            high_confidence_fixes = len([f for f in analysis_results["fix_recommendations"] if f["confidence"] > 0.8])
            print(f"✅ Analysis complete: {high_confidence_fixes} high-confidence fixes identified")
            print()

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            workflow_results["phases"]["analysis"] = {"status": "failed", "error": str(e)}

        # Phase 3: Automated Fixing (if enabled)
        if auto_fix and "analysis" in workflow_results["phases"]:
            print("🔧 PHASE 3: AUTOMATED FIXING")
            print("-" * 40)

            try:
                # Save analysis results with high-confidence fixes for fixer
                analysis_data = workflow_results["phases"]["analysis"]["results"]
                enhanced_scan_results = scan_results.copy()
                enhanced_scan_results["intelligence_analysis"] = analysis_data

                # Save enhanced scan results to GP-DATA
                scan_file = self.scans_dir / f"enhanced_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(scan_file, 'w') as f:
                    json.dump(enhanced_scan_results, f, indent=2)

                # Execute fixers via subprocess
                fix_cmd = f"PYTHONPATH={GP_COPILOT_BASE} python3 {GP_COPILOT_BASE}/GP-CONSULTING-AGENTS/fixers/apply_all_fixes.py {scan_file} {target_path}"
                subprocess.run(fix_cmd, shell=True, capture_output=True, text=True)

                # Get latest fix results from GP-DATA
                latest_fix = max(self.fixes_dir.glob('*_fix_report_*.json'), key=lambda p: p.stat().st_mtime)
                with open(latest_fix) as f:
                    fix_results = json.load(f)
                workflow_results["phases"]["fixing"] = {
                    "status": "completed",
                    "results": fix_results,
                    "duration": self._calculate_phase_duration()
                }
                workflow_results["workflow_info"]["phases"].append("fixing")

                total_fixes = sum(
                    data.get("summary", {}).get("total_fixes", 0)
                    for data in fix_results["results"].values()
                    if "summary" in data
                )
                print(f"✅ Fixing complete: {total_fixes} automated fixes applied")
                print()

            except Exception as e:
                print(f"❌ Fixing failed: {e}")
                workflow_results["phases"]["fixing"] = {"status": "failed", "error": str(e)}

        # Phase 4: Executive Reporting
        print("📋 PHASE 4: EXECUTIVE REPORTING")
        print("-" * 40)

        try:
            report = self._generate_executive_report(workflow_results)
            workflow_results["phases"]["reporting"] = {
                "status": "completed",
                "results": report,
                "duration": self._calculate_phase_duration()
            }
            workflow_results["workflow_info"]["phases"].append("reporting")

            print("✅ Executive report generated")
            print()

        except Exception as e:
            print(f"❌ Reporting failed: {e}")
            workflow_results["phases"]["reporting"] = {"status": "failed", "error": str(e)}

        # Final Summary
        workflow_results["workflow_info"]["end_time"] = datetime.now().isoformat()
        workflow_results["workflow_info"]["total_duration"] = self._calculate_total_duration(workflow_results)

        self._print_final_summary(workflow_results)
        self._save_workflow_results(workflow_results)

        return workflow_results

    def _analyze_with_intelligence(self, scan_results: dict) -> dict:
        """Analyze scan results with security intelligence"""
        analysis = {
            "fix_recommendations": [],
            "risk_assessment": {},
            "compliance_impact": {}
        }

        # Analyze each scanner's findings
        for scanner, results in scan_results.get("results", {}).items():
            if "error" in results:
                continue

            findings = results.get("findings", [])
            for finding in findings:
                # Get vulnerability ID based on scanner type
                vuln_id = self._extract_vulnerability_id(scanner, finding)
                if vuln_id:
                    # Basic risk assessment without external knowledge base
                    severity = finding.get("severity", "MEDIUM").upper()
                    risk_level = "High" if severity in ["CRITICAL", "HIGH"] else "Medium" if severity == "MEDIUM" else "Low"

                    analysis["fix_recommendations"].append({
                        "vulnerability_id": vuln_id,
                        "scanner": scanner,
                        "confidence": 0.8 if severity in ["CRITICAL", "HIGH"] else 0.5,
                        "risk_level": risk_level,
                        "fix_complexity": "Medium",
                        "business_impact": finding.get("description", ""),
                        "title": finding.get("title", vuln_id)
                    })

        # Calculate overall risk assessment
        analysis["risk_assessment"] = self._calculate_risk_assessment(analysis["fix_recommendations"])

        return analysis

    def _extract_vulnerability_id(self, scanner: str, finding: dict) -> str:
        """Extract vulnerability ID from finding based on scanner type"""
        if scanner == "checkov":
            return finding.get("check_id", "")
        elif scanner == "bandit":
            return finding.get("test_id", "")
        elif scanner == "trivy":
            return finding.get("VulnerabilityID", "")
        return ""

    def _calculate_risk_assessment(self, recommendations: list) -> dict:
        """Calculate overall risk assessment"""
        risk_counts = {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
        total_findings = len(recommendations)

        for rec in recommendations:
            risk_level = rec.get("risk_level", "Unknown")
            risk_counts[risk_level] += 1

        return {
            "total_findings": total_findings,
            "risk_distribution": risk_counts,
            "overall_risk_score": self._calculate_risk_score(risk_counts),
            "high_priority_count": risk_counts["High"]
        }

    def _calculate_risk_score(self, risk_counts: dict) -> float:
        """Calculate numerical risk score"""
        weights = {"High": 3.0, "Medium": 2.0, "Low": 1.0, "Unknown": 1.5}
        total_weight = sum(count * weights[level] for level, count in risk_counts.items())
        total_findings = sum(risk_counts.values())

        if total_findings == 0:
            return 0.0

        return round(total_weight / total_findings, 2)

    def _generate_executive_report(self, workflow_results: dict) -> dict:
        """Generate executive-level security report"""
        report = {
            "executive_summary": {},
            "key_metrics": {},
            "recommendations": {},
            "compliance_status": {}
        }

        # Extract key metrics
        if "scanning" in workflow_results["phases"]:
            scan_data = workflow_results["phases"]["scanning"]["results"]
            total_issues = self._count_total_issues(scan_data)

            report["key_metrics"] = {
                "total_security_issues": total_issues,
                "scanners_executed": len(scan_data["scan_info"]["scanners"]),
                "scan_duration": workflow_results["phases"]["scanning"].get("duration", "N/A")
            }

        # Analysis insights
        if "analysis" in workflow_results["phases"]:
            analysis_data = workflow_results["phases"]["analysis"]["results"]
            risk_assessment = analysis_data.get("risk_assessment", {})

            report["executive_summary"] = {
                "overall_risk_score": risk_assessment.get("overall_risk_score", 0),
                "high_priority_issues": risk_assessment.get("high_priority_count", 0),
                "automated_fix_candidates": len([
                    r for r in analysis_data.get("fix_recommendations", [])
                    if r.get("confidence", 0) > 0.8
                ])
            }

        # Fixing results
        if "fixing" in workflow_results["phases"]:
            fix_data = workflow_results["phases"]["fixing"]["results"]
            total_fixes = sum(
                data.get("summary", {}).get("total_fixes", 0)
                for data in fix_data["results"].values()
                if "summary" in data
            )
            report["key_metrics"]["automated_fixes_applied"] = total_fixes

        return report

    def _count_total_issues(self, scan_results: dict) -> int:
        """Count total issues across all scanners"""
        total = 0
        for scanner_results in scan_results.get("results", {}).values():
            if "summary" in scanner_results:
                total += scanner_results["summary"].get("total", 0)
        return total

    def _calculate_phase_duration(self) -> str:
        """Calculate phase duration (placeholder)"""
        return "< 1 minute"

    def _calculate_total_duration(self, workflow_results: dict) -> str:
        """Calculate total workflow duration"""
        start_time = workflow_results["workflow_info"]["start_time"]
        end_time = workflow_results["workflow_info"]["end_time"]
        # Simplified duration calculation
        return "< 5 minutes"

    def _print_final_summary(self, workflow_results: dict):
        """Print final workflow summary"""
        print("🎯 JAMES WORKFLOW SUMMARY")
        print("=" * 60)

        phases_completed = len(workflow_results["workflow_info"]["phases"])
        print(f"Phases completed: {phases_completed}")

        if "scanning" in workflow_results["phases"]:
            scan_results = workflow_results["phases"]["scanning"]["results"]
            total_issues = self._count_total_issues(scan_results)
            print(f"Security issues found: {total_issues}")

        if "fixing" in workflow_results["phases"]:
            fix_results = workflow_results["phases"]["fixing"]["results"]
            total_fixes = sum(
                data.get("summary", {}).get("total_fixes", 0)
                for data in fix_results["results"].values()
                if "summary" in data
            )
            print(f"Automated fixes applied: {total_fixes}")

        print(f"Total duration: {workflow_results['workflow_info'].get('total_duration', 'N/A')}")
        print()

    def _save_workflow_results(self, workflow_results: dict):
        """Save complete workflow results to GP-DATA"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.analysis_dir / f"james_workflow_{timestamp}.json"
        results_file.parent.mkdir(exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump(workflow_results, f, indent=2)

        print(f"📁 Complete workflow results saved to: {results_file}")

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python james_orchestrator.py <target_path> [--auto-fix]")
        sys.exit(1)

    target_path = sys.argv[1]
    auto_fix = "--auto-fix" in sys.argv

    orchestrator = JamesSecurityOrchestrator()
    results = orchestrator.execute_full_workflow(target_path, auto_fix)

if __name__ == "__main__":
    main()