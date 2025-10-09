#!/usr/bin/env python3
"""
Test Tool-Based Pattern Routing
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine.automation.automated_fixes import AutomatedFixEngine
from automation_engine.automation.james_ai_engine import SecurityFinding
import uuid
from datetime import datetime

async def test_tool_based_routing():
    """Test tool-based routing with realistic findings"""

    print("\n" + "="*60)
    print("    Testing Tool-Based Pattern Routing")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    # Create realistic findings with proper tool attribution
    test_findings = [
        # Trivy container findings
        SecurityFinding(
            id="trivy-container-1",
            severity="critical",
            title="alpine:3.15 base image vulnerabilities",
            description="alpine:3.15 has 12 vulnerabilities including CVE-2023-1234",
            file_path="/test/Dockerfile",
            tool="trivy",
            remediation="Update to alpine:3.18"
        ),
        SecurityFinding(
            id="trivy-container-2",
            severity="high",
            title="node:16 container image vulnerabilities",
            description="node:16 container has outdated packages",
            file_path="/test/Dockerfile",
            tool="trivy",
            remediation="Update container"
        ),

        # Trivy NPM findings
        SecurityFinding(
            id="trivy-npm-1",
            severity="high",
            title="NPM package vulnerabilities",
            description="lodash@4.17.4 has CVE-2019-10744 in package.json",
            file_path="/test/package.json",
            tool="trivy",
            remediation="Update package"
        ),

        # Checkov terraform findings
        SecurityFinding(
            id="checkov-tf-1",
            severity="medium",
            title="S3 bucket encryption",
            description="aws_s3_bucket missing encryption configuration",
            file_path="/test/main.tf",
            tool="checkov",
            remediation="Add encryption"
        ),

        # Kubescape kubernetes findings
        SecurityFinding(
            id="kubescape-k8s-1",
            severity="high",
            title="Security context missing",
            description="Kubernetes deployment missing securityContext configuration",
            file_path="/test/deployment.yaml",
            tool="kubescape",
            remediation="Add securityContext"
        )
    ]

    print("📝 Testing tool-specific routing...")

    correct_routes = 0
    total_tests = len(test_findings)

    expected_routes = {
        "trivy-container-1": "docker_vulnerability",
        "trivy-container-2": "docker_vulnerability",
        "trivy-npm-1": "npm_vulnerability",
        "checkov-tf-1": "terraform_security",
        "kubescape-k8s-1": "kubernetes_security"
    }

    for finding in test_findings:
        # Test tool-specific routing
        detected_pattern = fix_engine._get_tool_specific_pattern(finding)
        expected_pattern = expected_routes[finding.id]

        if detected_pattern == expected_pattern:
            print(f"  ✅ {finding.tool}: '{finding.title[:30]}...' → {detected_pattern}")
            correct_routes += 1
        else:
            print(f"  ❌ {finding.tool}: '{finding.title[:30]}...' → Expected {expected_pattern}, got {detected_pattern}")

    # Test complete fix generation pipeline
    print(f"\n🔧 Testing complete fix generation pipeline...")

    total_fixes_generated = 0
    successful_fixes = 0

    for finding in test_findings:
        try:
            fixes = await fix_engine._generate_fixes_for_finding(finding, "/tmp/test")
            total_fixes_generated += len(fixes)

            if fixes:
                fix = fixes[0]  # Check first fix
                has_real_commands = any(
                    any(tool in cmd for tool in ["sed", "docker", "terraform", "kubectl", "npm"])
                    for cmd in fix.commands
                )

                if has_real_commands:
                    successful_fixes += 1
                    print(f"  ✅ {finding.tool}: Generated {len(fix.commands)} real commands")
                else:
                    print(f"  ⚠️ {finding.tool}: Generated placeholder commands")
            else:
                print(f"  ❌ {finding.tool}: No fixes generated")

        except Exception as e:
            print(f"  💥 {finding.tool}: Error - {e}")

    # Results
    routing_accuracy = (correct_routes / total_tests) * 100
    fix_success_rate = (successful_fixes / total_tests) * 100 if total_tests > 0 else 0

    print(f"\n📊 Tool-Based Routing Results:")
    print(f"=" * 40)
    print(f"Correct routing: {correct_routes}/{total_tests} ({routing_accuracy:.1f}%)")
    print(f"Fix generation success: {successful_fixes}/{total_tests} ({fix_success_rate:.1f}%)")
    print(f"Total fixes generated: {total_fixes_generated}")

    return routing_accuracy, fix_success_rate

async def test_original_vs_improved():
    """Compare original pattern matching vs improved routing"""

    print("\n" + "="*60)
    print("    Original vs Improved Pattern Matching")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    # Test case that was failing before
    container_finding = SecurityFinding(
        id="test-container",
        severity="critical",
        title="alpine:3.15 has CVE-2023-1234",
        description="alpine:3.15 base image has security vulnerabilities",
        file_path="/test/Dockerfile",
        tool="trivy"
    )

    # Test new tool-specific routing
    tool_route = fix_engine._get_tool_specific_pattern(container_finding)
    print(f"🎯 Tool-specific routing: {tool_route}")

    # Test old pattern matching (for comparison)
    old_match = None
    for pattern_name, pattern_config in fix_engine.fix_patterns.items():
        if fix_engine._matches_pattern(container_finding, pattern_config["pattern"]):
            old_match = pattern_name
            break

    print(f"🔄 Original pattern matching: {old_match}")

    # Generate actual fix
    fixes = await fix_engine._generate_fixes_for_finding(container_finding, "/tmp/test")

    if fixes:
        fix = fixes[0]
        print(f"✅ Generated fix: {fix.title}")
        print(f"   Commands: {len(fix.commands)}")
        print(f"   Type: {fix.fix_type.value}")
    else:
        print(f"❌ No fixes generated")

    improvement = tool_route == "docker_vulnerability" and tool_route != old_match
    return improvement

async def main():
    """Run routing improvement tests"""

    print("🚀 Pattern Routing Improvement Test")
    print("=" * 60)

    # Test tool-based routing
    routing_accuracy, fix_success_rate = await test_tool_based_routing()

    # Test specific improvement
    specific_improvement = await test_original_vs_improved()

    print(f"\n🎯 ROUTING IMPROVEMENT RESULTS")
    print(f"=" * 60)
    print(f"Tool routing accuracy: {routing_accuracy:.1f}%")
    print(f"Fix generation success: {fix_success_rate:.1f}%")
    print(f"Specific improvement: {'✅ YES' if specific_improvement else '❌ NO'}")

    # Overall assessment
    overall_success = routing_accuracy >= 80 and fix_success_rate >= 60

    if overall_success:
        print("✅ SIGNIFICANT ROUTING IMPROVEMENT ACHIEVED!")
    elif routing_accuracy > 60:
        print("⚠️ MODERATE IMPROVEMENT - needs fine-tuning")
    else:
        print("❌ ROUTING STILL NEEDS WORK")

    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)