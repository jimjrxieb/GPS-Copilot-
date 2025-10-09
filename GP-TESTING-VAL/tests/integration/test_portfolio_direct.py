#!/usr/bin/env python3
"""
Direct Portfolio Security Test
=============================

Test James-OS security tools directly against Portfolio project files.
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.trivy_runner import TrivyRunner
from tools.checkov_runner import CheckovRunner
from automation.james_ai_engine import JamesAIEngine
from automation.automated_fixes import AutomatedFixEngine


async def test_portfolio_direct_scan():
    """Direct scan of Portfolio using individual tools"""

    print("\n" + "="*80)
    print("    🎯 DIRECT PORTFOLIO SECURITY SCAN")
    print("    Testing Real James-OS Tools on Portfolio")
    print("="*80 + "\n")

    # Portfolio paths
    portfolio_path = "/home/jimmie/linkops-industries/Portfolio"
    vulnerable_dockerfile = f"{portfolio_path}/Dockerfile.vulnerable"
    terraform_path = f"{portfolio_path}/terraform"
    package_json = f"{portfolio_path}/package.json"

    print(f"📁 Target: {portfolio_path}")
    print(f"🔍 Focus Files:")
    print(f"  - {vulnerable_dockerfile}")
    print(f"  - {terraform_path}/insecure.tf")
    print(f"  - {package_json}\n")

    # Initialize tools
    trivy = TrivyRunner()
    checkov = CheckovRunner()
    ai_engine = JamesAIEngine()
    fix_engine = AutomatedFixEngine()

    scan_results = {}

    try:
        # 1. Scan with Trivy (filesystem scan)
        print("🔍 Running Trivy filesystem scan...")
        trivy_result = await trivy.scan_filesystem(portfolio_path)

        if trivy_result.get("success"):
            scan_results["trivy_results"] = trivy_result.get("data", {})
            vulns = trivy_result.get("data", {}).get("vulnerabilities", [])
            print(f"  ✅ Trivy scan complete: {len(vulns)} vulnerabilities found")

            # Show some findings
            if vulns:
                print(f"  📋 Sample findings:")
                for vuln in vulns[:3]:
                    severity = vuln.get("severity", "unknown")
                    pkg = vuln.get("pkg_name", "unknown")
                    cve = vuln.get("vulnerability_id", "no-cve")
                    print(f"    - {severity}: {pkg} ({cve})")
        else:
            print(f"  ❌ Trivy scan failed: {trivy_result.get('error', 'Unknown')}")

        # 2. Scan with Checkov (Terraform)
        print(f"\n🔍 Running Checkov scan on Terraform...")
        checkov_result = await checkov.scan_directory(terraform_path)

        if checkov_result.get("success"):
            scan_results["checkov_results"] = checkov_result.get("data", {})
            findings = checkov_result.get("data", {}).get("findings", [])
            print(f"  ✅ Checkov scan complete: {len(findings)} findings")

            # Show some findings
            if findings:
                print(f"  📋 Sample findings:")
                for finding in findings[:3]:
                    check_id = finding.get("check_id", "unknown")
                    severity = finding.get("severity", "unknown")
                    desc = finding.get("description", "no description")
                    print(f"    - {severity}: {check_id} - {desc[:50]}...")
        else:
            print(f"  ❌ Checkov scan failed: {checkov_result.get('error', 'Unknown')}")

        # 3. Analyze with James AI
        print(f"\n🧠 Running James AI analysis...")

        if scan_results:
            analysis = await ai_engine.analyze_scan_results(
                scan_results,
                "portfolio_direct_test"
            )

            print(f"  🔬 Analysis ID: {analysis.analysis_id}")
            print(f"  📊 Findings analyzed: {analysis.findings_analyzed}")
            print(f"  ⚡ Risk score: {analysis.risk_score:.1f}/100")
            print(f"  🛠️  Auto-fixable: {len(analysis.auto_fixable)}")

            if analysis.summary:
                print(f"  💡 Summary: {analysis.summary[:100]}...")

            # 4. Generate fixes
            print(f"\n🔧 Generating automated fixes...")

            if analysis.findings and len(analysis.findings) > 0:
                fix_job = await fix_engine.generate_fixes_for_analysis(
                    analysis=analysis,
                    project_path=portfolio_path
                )

                print(f"  🆔 Fix job: {fix_job.job_id}")
                print(f"  🔧 Fixes generated: {fix_job.total_fixes}")

                if fix_job.total_fixes > 0:
                    print(f"\n  🛠️  Generated fixes:")
                    for i, fix in enumerate(fix_job.fixes[:3], 1):
                        print(f"    {i}. {fix.title}")
                        print(f"       Type: {fix.fix_type.value}")
                        print(f"       Commands: {fix.commands[:1]}")
                else:
                    print(f"  ⚠️  No fixes could be generated")
            else:
                print(f"  ⚠️  No findings to generate fixes for")
        else:
            print(f"  ❌ No scan results to analyze")

        # Summary
        print(f"\n" + "="*80)
        print("    PORTFOLIO SCAN RESULTS")
        print("="*80)

        total_vulns = len(scan_results.get("trivy_results", {}).get("vulnerabilities", []))
        total_findings = len(scan_results.get("checkov_results", {}).get("findings", []))

        print(f"🔍 Trivy vulnerabilities: {total_vulns}")
        print(f"🔍 Checkov findings: {total_findings}")
        print(f"📊 Total security issues: {total_vulns + total_findings}")

        if total_vulns + total_findings > 0:
            print(f"✅ Portfolio has real vulnerabilities - James-OS can analyze them!")
        else:
            print(f"⚠️  No vulnerabilities found - Portfolio may be secure or tools need adjustment")

        return True

    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run direct Portfolio scan"""

    success = await test_portfolio_direct_scan()

    print(f"\n🎯 Direct Portfolio scan: {'✅ SUCCESS' if success else '❌ FAILED'}")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)