#!/usr/bin/env python3
"""
Test Improved Fix Generation with Real Container Vulnerabilities
"""

import asyncio
import sys
import os
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine.automation.automated_fixes import AutomatedFixEngine, FixType
from automation_engine.automation.james_ai_engine import SecurityFinding
import uuid
from datetime import datetime

async def test_container_fixes():
    """Test container-specific vulnerability fixes"""

    print("\n" + "="*60)
    print("    Testing Container Vulnerability Fixes")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    # Create realistic container findings from Trivy
    container_findings = [
        SecurityFinding(
            id="trivy-001",
            severity="critical",
            title="alpine:3.15 base image vulnerabilities",
            description="alpine:3.15 has 12 vulnerabilities including CVE-2023-1234",
            file_path="/tmp/test/Dockerfile",
            tool="trivy",
            remediation="Update to alpine:3.18"
        ),
        SecurityFinding(
            id="trivy-002",
            severity="high",
            title="node:16-alpine vulnerabilities",
            description="node:16-alpine contains outdated packages with known CVEs",
            file_path="/tmp/test/Dockerfile",
            tool="trivy",
            remediation="Update to node:18-alpine"
        ),
        SecurityFinding(
            id="trivy-003",
            severity="medium",
            title="ubuntu:20.04 package vulnerabilities",
            description="ubuntu:20.04 base image has security updates available",
            file_path="/tmp/test/Dockerfile",
            tool="trivy",
            remediation="Update to ubuntu:22.04"
        )
    ]

    # Create test Dockerfile to work with
    os.makedirs("/tmp/test", exist_ok=True)
    dockerfile_content = """FROM alpine:3.15
RUN apk add --no-cache curl
COPY . /app
WORKDIR /app
CMD ["./start.sh"]
"""

    with open("/tmp/test/Dockerfile", "w") as f:
        f.write(dockerfile_content)

    print("📝 Created test Dockerfile with alpine:3.15")
    print("📝 Testing container fix generation...\n")

    # Test each container finding
    total_fixes = 0
    successful_fixes = 0

    for finding in container_findings:
        print(f"🔍 Testing: {finding.title}")

        try:
            # Test image extraction
            image_info = fix_engine._extract_image_from_finding(finding)
            if image_info:
                image_name, version = image_info
                print(f"   ✅ Extracted: {image_name}:{version}")

                # Test version upgrade determination
                target_version = fix_engine._determine_safe_image_version(image_name, version)
                if target_version:
                    print(f"   ✅ Upgrade path: {version} → {target_version}")
                else:
                    print(f"   ⚠️ No upgrade path found for {image_name}:{version}")

            else:
                print(f"   ❌ Could not extract image from finding")

            # Generate actual fix
            fix = await fix_engine._create_container_fix(finding, f"fix-{finding.id}", "/tmp/test")
            total_fixes += 1

            if fix.commands and any("sed" in cmd or "docker" in cmd for cmd in fix.commands):
                successful_fixes += 1
                print(f"   ✅ Generated {len(fix.commands)} fix commands")
                for cmd in fix.commands[:2]:  # Show first 2 commands
                    print(f"      → {cmd}")
            else:
                print(f"   ❌ Generated placeholder/manual fix")

        except Exception as e:
            print(f"   💥 Error: {e}")

        print()

    # Test the complete vulnerability-to-fix pipeline
    print(f"🔧 Testing complete pipeline...")

    vulns_as_dicts = []
    for finding in container_findings:
        vulns_as_dicts.append({
            "check_id": f"CONTAINER-{finding.id}",
            "check_name": finding.title,
            "file_path": finding.file_path,
            "resource": "Dockerfile",
            "severity": finding.severity
        })

    fix_job = await fix_engine.generate_fixes_for_vulnerabilities(
        vulns_as_dicts,
        "/tmp/test"
    )

    # Results
    print(f"\n📊 Container Fix Test Results:")
    print(f"=" * 40)
    print(f"Total container findings: {len(container_findings)}")
    print(f"Fixes generated: {total_fixes}")
    print(f"Successful fixes: {successful_fixes}")
    print(f"Success rate: {(successful_fixes/total_fixes)*100:.1f}%" if total_fixes > 0 else "N/A")
    print(f"Pipeline job fixes: {fix_job.total_fixes}")

    # Cleanup
    import shutil
    shutil.rmtree("/tmp/test", ignore_errors=True)

    return successful_fixes, total_fixes

async def test_pattern_matching_improvements():
    """Test improved pattern matching for different vulnerability types"""

    print("\n" + "="*60)
    print("    Testing Pattern Matching Improvements")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    # Test cases with expected pattern matches
    test_cases = [
        # Container vulnerabilities
        ("alpine:3.15 has CVE-2023-1234", "docker_vulnerability", "trivy"),
        ("node:16 container image vulnerabilities", "docker_vulnerability", "trivy"),
        ("FROM ubuntu:20.04 has security issues", "container_vulnerability", "trivy"),

        # NPM vulnerabilities
        ("lodash@4.17.4 has CVE-2019-10744", "npm_vulnerability", "npm-audit"),
        ("package.json contains vulnerable dependencies", "npm_vulnerability", "npm-audit"),

        # Terraform
        ("aws_s3_bucket missing encryption", "terraform_security", "checkov"),
        ("CKV_AWS_126 monitoring disabled", "CKV_AWS_126", "checkov"),

        # Kubernetes
        ("securityContext allowPrivilegeEscalation", "kubernetes_security", "kubescape"),
        ("CKV_K8S_23 privilege escalation", "CKV_K8S_23", "kubescape")
    ]

    correct_matches = 0
    total_tests = len(test_cases)

    for description, expected_pattern, tool in test_cases:
        finding = SecurityFinding(
            id="test",
            severity="high",
            title=description,
            description=description,
            tool=tool
        )

        # Test pattern matching
        matched_pattern = None
        for pattern_name, pattern_config in fix_engine.fix_patterns.items():
            if fix_engine._matches_pattern(finding, pattern_config["pattern"]):
                matched_pattern = pattern_name
                break

        if matched_pattern == expected_pattern:
            print(f"  ✅ '{description[:40]}...' → {matched_pattern}")
            correct_matches += 1
        else:
            print(f"  ❌ '{description[:40]}...' → Expected {expected_pattern}, got {matched_pattern}")

    match_rate = (correct_matches / total_tests) * 100
    print(f"\n📊 Pattern Matching Results:")
    print(f"Correct matches: {correct_matches}/{total_tests}")
    print(f"Match accuracy: {match_rate:.1f}%")

    return correct_matches, total_tests

async def main():
    """Run all improvement tests"""

    print("🚀 GuidePoint Fix Generation Improvement Test")
    print("=" * 60)

    # Test container fixes
    container_success, container_total = await test_container_fixes()

    # Test pattern matching
    pattern_success, pattern_total = await test_pattern_matching_improvements()

    # Overall results
    print(f"\n🎯 OVERALL IMPROVEMENT RESULTS")
    print(f"=" * 60)
    print(f"Container fixes: {container_success}/{container_total} ({(container_success/container_total)*100:.1f}%)")
    print(f"Pattern matching: {pattern_success}/{pattern_total} ({(pattern_success/pattern_total)*100:.1f}%)")

    # Calculate overall improvement
    overall_success = container_success + pattern_success
    overall_total = container_total + pattern_total
    overall_rate = (overall_success / overall_total) * 100 if overall_total > 0 else 0

    print(f"Overall success rate: {overall_rate:.1f}%")

    if overall_rate > 70:
        print("✅ SIGNIFICANT IMPROVEMENT ACHIEVED!")
    elif overall_rate > 55:
        print("⚠️ MODERATE IMPROVEMENT")
    else:
        print("❌ NEEDS MORE WORK")

    return overall_rate > 70

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)