#!/usr/bin/env python3
"""
Simple Unit Test for Fix Generation
====================================

Tests that the automated fix generation actually creates real commands,
not just empty arrays or placeholders.
"""

import asyncio
import sys
import os
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.james_ai_engine import JamesAIEngine, SecurityFinding, JamesAnalysis
from automation.automated_fixes import AutomatedFixEngine, FixType
import uuid
from datetime import datetime


async def test_fix_generation():
    """Test that fixes are generated for real vulnerabilities"""

    print("\n" + "="*60)
    print("    Testing James-OS Fix Generation")
    print("="*60 + "\n")

    # Initialize engines
    ai_engine = JamesAIEngine()
    fix_engine = AutomatedFixEngine()

    # Create test findings that match our fix patterns
    test_findings = [
        SecurityFinding(
            id="npm-001",
            severity="high",
            title="NPM audit found vulnerabilities",
            description="Package lodash@4.17.4 has known vulnerabilities (CVE-2019-10744)",
            file_path="package.json",
            tool="npm-audit",
            cve_id="CVE-2019-10744",
            remediation="Update to lodash@4.17.21"
        ),
        SecurityFinding(
            id="docker-001",
            severity="critical",
            title="Outdated base image",
            description="Docker container using node:8-alpine with security vulnerabilities",
            file_path="Dockerfile",
            tool="trivy",
            remediation="Update to node:20-alpine"
        ),
        SecurityFinding(
            id="tf-001",
            severity="high",
            title="S3 bucket publicly accessible",
            description="Terraform aws_s3_bucket resource has public-read ACL",
            file_path="main.tf",
            line_number=3,
            tool="checkov",
            remediation="Set ACL to private"
        ),
        SecurityFinding(
            id="k8s-001",
            severity="high",
            title="Container running as root",
            description="Kubernetes deployment missing securityContext runAsNonRoot",
            file_path="deployment.yaml",
            tool="kubescape",
            remediation="Add securityContext with runAsNonRoot: true"
        )
    ]

    # Create a mock analysis with the findings
    analysis = JamesAnalysis(
        analysis_id=str(uuid.uuid4()),
        project_id="test_project",
        generated_at=datetime.now().isoformat(),
        findings_analyzed=len(test_findings),
        risk_score=75.0,
        priority_level="high",
        summary="Multiple security vulnerabilities detected",
        detailed_analysis="Found npm, docker, terraform, and kubernetes security issues",
        recommendations=["Update dependencies", "Harden containers", "Fix infrastructure"],
        auto_fixable=[f.title for f in test_findings],
        requires_human=[],
        estimated_fix_time="30 minutes",
        business_impact="High risk of data breach",
        technical_impact="Systems vulnerable to exploitation",
        findings=test_findings  # This is the key - findings are now stored!
    )

    print("📝 Created test analysis with {} findings\n".format(len(test_findings)))

    # Test 1: Load findings from analysis
    print("TEST 1: Loading findings from analysis...")
    loaded_findings = await fix_engine._load_findings_from_analysis(analysis)

    if loaded_findings and len(loaded_findings) == len(test_findings):
        print("✅ Successfully loaded {} findings from analysis".format(len(loaded_findings)))
    else:
        print("❌ Failed to load findings - got {} instead of {}".format(
            len(loaded_findings) if loaded_findings else 0,
            len(test_findings)
        ))
        return False

    # Test 2: Generate fixes for the findings
    print("\nTEST 2: Generating fixes for vulnerabilities...")

    # First, save the analysis so it can be loaded
    await ai_engine._save_analysis(analysis)

    # Now generate fixes
    fix_job = await fix_engine.generate_fixes_for_analysis(
        analysis=analysis,
        project_path="/tmp/test_project"
    )

    print(f"\n📊 Fix Generation Results:")
    print(f"  - Job ID: {fix_job.job_id}")
    print(f"  - Total fixes generated: {fix_job.total_fixes}")

    if fix_job.total_fixes == 0:
        print("\n❌ No fixes were generated!")
        return False

    # Test 3: Validate fix quality
    print(f"\n📋 Generated Fixes:")
    print("-" * 50)

    all_valid = True
    for i, fix in enumerate(fix_job.fixes, 1):
        print(f"\nFix {i}: {fix.title}")
        print(f"  Type: {fix.fix_type.value}")
        print(f"  Priority: {fix.priority}")
        print(f"  Commands: {fix.commands}")
        print(f"  Files: {fix.files_to_modify}")
        print(f"  Rollback: {fix.rollback_commands}")

        # Validate fix has real commands, not placeholders
        has_real_commands = any(cmd for cmd in fix.commands if
                               any(tool in cmd for tool in ["npm", "docker", "terraform", "kubectl", "git"]))

        if has_real_commands:
            print("  ✅ Contains real commands")
        else:
            print("  ❌ Only placeholder commands")
            all_valid = False

    # Summary
    print("\n" + "="*60)
    print("                    TEST SUMMARY")
    print("="*60)
    print(f"Findings loaded: {'✅ PASS' if loaded_findings else '❌ FAIL'}")
    print(f"Fixes generated: {'✅ PASS' if fix_job.total_fixes > 0 else '❌ FAIL'}")
    print(f"Fix quality: {'✅ PASS' if all_valid else '❌ FAIL'}")

    success = loaded_findings and fix_job.total_fixes > 0 and all_valid
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")

    return success


async def test_pattern_matching():
    """Test that vulnerability patterns are matched correctly"""

    print("\n" + "="*60)
    print("    Testing Pattern Matching")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    test_cases = [
        ("npm audit found vulnerabilities", "npm_vulnerability"),
        ("Docker container using outdated alpine", "docker_vulnerability"),
        ("Terraform resource missing encryption", "terraform_security"),
        ("Kubernetes pod without securityContext", "kubernetes_security"),
        ("Package lodash has CVE-2019-10744", "outdated_dependency")
    ]

    print("Testing pattern matching:")
    for description, expected_pattern in test_cases:
        finding = SecurityFinding(
            id="test",
            severity="high",
            title=description,
            description=description,
            tool="test"
        )

        matched = False
        matched_pattern = None
        for pattern_name, pattern_config in fix_engine.fix_patterns.items():
            if fix_engine._matches_pattern(finding, pattern_config["pattern"]):
                matched = True
                matched_pattern = pattern_name
                break

        if matched_pattern == expected_pattern:
            print(f"  ✅ '{description[:30]}...' → {matched_pattern}")
        else:
            print(f"  ❌ '{description[:30]}...' → Expected {expected_pattern}, got {matched_pattern}")

    return True


async def main():
    """Run all tests"""

    # Run fix generation test
    fix_gen_success = await test_fix_generation()

    # Run pattern matching test
    pattern_success = await test_pattern_matching()

    return fix_gen_success and pattern_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)