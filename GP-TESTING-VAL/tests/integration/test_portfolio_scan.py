#!/usr/bin/env python3
"""
Real Portfolio Security Scan
============================

Test James-OS autonomous security operations against the real Portfolio project.
This will:
1. Scan the actual Portfolio directory for vulnerabilities
2. Use James AI to analyze real findings
3. Generate real automated fixes
4. Test the complete autonomous pipeline

NO MOCKS - This is a real production test.
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.project_scanner import ProjectScanner
from automation.james_ai_engine import JamesAIEngine
from automation.automated_fixes import AutomatedFixEngine


async def test_portfolio_autonomous_scan():
    """Test James-OS against real Portfolio project"""

    print("\n" + "="*80)
    print("    🚀 JAMES-OS AUTONOMOUS SECURITY SCAN")
    print("    Target: Real Portfolio Application")
    print("    Mode: Full Autonomous Operations")
    print("="*80 + "\n")

    # Initialize James-OS components
    scanner = ProjectScanner()
    ai_engine = JamesAIEngine()
    fix_engine = AutomatedFixEngine()

    # Portfolio project path
    portfolio_path = "/home/jimmie/linkops-industries/Portfolio"
    project_id = "portfolio_real_scan"

    print(f"📁 Scanning Portfolio Project: {portfolio_path}")
    print(f"🆔 Project ID: {project_id}\n")

    try:
        # Step 1: Run real security scans
        print("🔍 STEP 1: Running Security Scans")
        print("-" * 50)

        scan_result = await scanner.scan_project_full(
            project_id=project_id,
            scan_types=["trivy", "checkov", "secrets"]  # Real scan types
        )

        # Note: scan_project_full uses project registry, so let's just run individual scans
        # against the Portfolio directory directly

        print(f"✅ Scan completed: {scan_result['scan_id']}")
        print(f"📊 Scan status: {scan_result['status']}")
        print(f"📁 Results saved to: {scan_result.get('output_path', 'N/A')}")

        # Show scan summary
        if 'summary' in scan_result:
            summary = scan_result['summary']
            print(f"\n📈 Scan Summary:")
            print(f"  - Tools run: {summary.get('tools_executed', 0)}")
            print(f"  - Total findings: {summary.get('total_findings', 0)}")
            print(f"  - Critical: {summary.get('critical', 0)}")
            print(f"  - High: {summary.get('high', 0)}")
            print(f"  - Medium: {summary.get('medium', 0)}")

        # Step 2: James AI Analysis
        print(f"\n🧠 STEP 2: James AI Analysis")
        print("-" * 50)

        # Get scan results for AI analysis
        scan_results = scan_result.get('results', {})

        analysis = await ai_engine.analyze_scan_results(
            scan_results,
            project_id
        )

        print(f"🔬 Analysis ID: {analysis.analysis_id}")
        print(f"📊 Risk Score: {analysis.risk_score:.1f}/100")
        print(f"⚡ Priority: {analysis.priority_level}")
        print(f"🔍 Findings Analyzed: {analysis.findings_analyzed}")
        print(f"🛠️  Auto-fixable: {len(analysis.auto_fixable)}")
        print(f"👤 Requires Human: {len(analysis.requires_human)}")

        # Show AI analysis summary
        print(f"\n💡 James AI Summary:")
        print(f"  {analysis.summary}")

        if analysis.recommendations:
            print(f"\n📋 AI Recommendations:")
            for i, rec in enumerate(analysis.recommendations[:3], 1):
                print(f"  {i}. {rec}")

        # Step 3: Automated Fix Generation
        print(f"\n🔧 STEP 3: Automated Fix Generation")
        print("-" * 50)

        fix_job = await fix_engine.generate_fixes_for_analysis(
            analysis=analysis,
            project_path=portfolio_path
        )

        print(f"🆔 Fix Job ID: {fix_job.job_id}")
        print(f"🔧 Total Fixes Generated: {fix_job.total_fixes}")

        if fix_job.total_fixes > 0:
            print(f"\n🛠️  Generated Fixes:")
            for i, fix in enumerate(fix_job.fixes[:5], 1):  # Show first 5
                print(f"\n  Fix {i}: {fix.title}")
                print(f"    Type: {fix.fix_type.value}")
                print(f"    Priority: {fix.priority}")
                print(f"    Files: {fix.files_to_modify}")
                print(f"    Commands: {fix.commands[:2]}")  # Show first 2 commands

        # Step 4: Dry Run Application (Safety First!)
        print(f"\n🎯 STEP 4: Dry Run Fix Application")
        print("-" * 50)

        if fix_job.total_fixes > 0:
            print("⚠️  Applying fixes in DRY RUN mode (no actual changes)")

            applied_job = await fix_engine.apply_fix_job(
                job_id=fix_job.job_id,
                project_path=portfolio_path,
                dry_run=True  # SAFETY: Don't actually modify Portfolio
            )

            print(f"✅ Dry run completed")
            print(f"🎯 Fixes that would be applied: {applied_job.applied_fixes}")
            print(f"❌ Fixes that would fail: {applied_job.failed_fixes}")
        else:
            print("⚠️  No fixes generated to apply")

        # Step 5: Results Summary
        print(f"\n🎉 STEP 5: Autonomous Operation Results")
        print("=" * 80)

        total_findings = analysis.findings_analyzed
        fixable_findings = len(analysis.auto_fixable)
        autonomy_rate = (fixable_findings / total_findings * 100) if total_findings > 0 else 0

        print(f"📊 Portfolio Security Assessment:")
        print(f"  🔍 Vulnerabilities Found: {total_findings}")
        print(f"  🤖 Autonomously Fixable: {fixable_findings}")
        print(f"  📈 Autonomy Rate: {autonomy_rate:.1f}%")
        print(f"  ⚡ Risk Level: {analysis.priority_level}")
        print(f"  🕐 Estimated Fix Time: {analysis.estimated_fix_time}")

        # Real autonomous capability test
        if autonomy_rate >= 70:
            print(f"\n✅ HIGH AUTONOMY: James-OS can handle most Portfolio security issues")
        elif autonomy_rate >= 50:
            print(f"\n⚠️  MEDIUM AUTONOMY: James-OS can handle some Portfolio security issues")
        else:
            print(f"\n❌ LOW AUTONOMY: Portfolio requires mostly manual security fixes")

        print(f"\n🚀 James-OS Autonomous Security Operations: COMPLETE")

        return {
            "total_findings": total_findings,
            "fixable_findings": fixable_findings,
            "autonomy_rate": autonomy_rate,
            "fixes_generated": fix_job.total_fixes,
            "scan_successful": True,
            "ai_analysis_successful": analysis.findings_analyzed > 0,
            "fix_generation_successful": fix_job.total_fixes > 0
        }

    except Exception as e:
        print(f"\n❌ AUTONOMOUS OPERATION FAILED: {e}")
        return {
            "scan_successful": False,
            "error": str(e)
        }


async def main():
    """Run real Portfolio security scan"""

    results = await test_portfolio_autonomous_scan()

    # Final assessment
    print(f"\n" + "="*80)
    print("    JAMES-OS AUTONOMOUS SECURITY ASSESSMENT")
    print("="*80)

    if results.get("scan_successful"):
        autonomy_rate = results.get("autonomy_rate", 0)
        print(f"🎯 Portfolio Autonomy Rate: {autonomy_rate:.1f}%")
        print(f"🔧 Fixes Generated: {results.get('fixes_generated', 0)}")

        if autonomy_rate >= 70:
            print(f"🏆 RESULT: James-OS can autonomously secure your Portfolio!")
        else:
            print(f"📈 RESULT: James-OS partially autonomous - needs improvement")
    else:
        print(f"❌ RESULT: Autonomous operations failed - needs debugging")

    return results.get("scan_successful", False)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)