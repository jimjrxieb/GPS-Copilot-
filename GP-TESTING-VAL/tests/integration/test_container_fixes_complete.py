#!/usr/bin/env python3
"""
Test Complete Container Fix Implementation
"""

import asyncio
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine.automation.automated_fixes import AutomatedFixEngine
from automation_engine.automation.james_ai_engine import SecurityFinding
import uuid
from datetime import datetime

async def test_container_fixes_with_real_dockerfiles():
    """Test container fixes with actual Dockerfiles"""

    print("\n" + "="*60)
    print("    Testing Container Fixes with Real Dockerfiles")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    # Create temporary project directories
    test_projects = {}

    try:
        # Project 1: Alpine container
        alpine_dir = tempfile.mkdtemp(prefix="test_alpine_")
        dockerfile_alpine = """FROM alpine:3.15
RUN apk add --no-cache curl git
WORKDIR /app
COPY . .
CMD ["./start.sh"]
"""
        with open(os.path.join(alpine_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_alpine)

        test_projects["alpine"] = alpine_dir

        # Project 2: Node container
        node_dir = tempfile.mkdtemp(prefix="test_node_")
        dockerfile_node = """FROM node:16-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
"""
        with open(os.path.join(node_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_node)

        test_projects["node"] = node_dir

        # Project 3: Ubuntu container
        ubuntu_dir = tempfile.mkdtemp(prefix="test_ubuntu_")
        dockerfile_ubuntu = """FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "app.py"]
"""
        with open(os.path.join(ubuntu_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_ubuntu)

        test_projects["ubuntu"] = ubuntu_dir

        print("📝 Created test projects with actual Dockerfiles")

        # Test container vulnerabilities
        container_findings = [
            SecurityFinding(
                id="alpine-vuln",
                severity="critical",
                title="alpine:3.15 has security vulnerabilities",
                description="alpine:3.15 base image contains CVE-2023-1234 and other vulnerabilities",
                file_path=os.path.join(alpine_dir, "Dockerfile"),
                tool="trivy",
                remediation="Update to alpine:3.18"
            ),
            SecurityFinding(
                id="node-vuln",
                severity="high",
                title="node:16-alpine vulnerabilities",
                description="node:16-alpine container image has outdated packages",
                file_path=os.path.join(node_dir, "Dockerfile"),
                tool="trivy",
                remediation="Update to node:18-alpine"
            ),
            SecurityFinding(
                id="ubuntu-vuln",
                severity="medium",
                title="ubuntu:20.04 package vulnerabilities",
                description="ubuntu:20.04 has security updates available",
                file_path=os.path.join(ubuntu_dir, "Dockerfile"),
                tool="trivy",
                remediation="Update to ubuntu:22.04"
            )
        ]

        successful_fixes = 0
        total_fixes = 0

        for finding in container_findings:
            print(f"\n🔍 Testing: {finding.title}")

            # Get the appropriate project directory
            if "alpine" in finding.id:
                project_path = alpine_dir
            elif "node" in finding.id:
                project_path = node_dir
            else:
                project_path = ubuntu_dir

            try:
                # Test image extraction
                image_info = fix_engine._extract_image_from_finding(finding)
                if image_info:
                    image_name, version = image_info
                    print(f"   ✅ Extracted: {image_name}:{version}")

                    # Test version upgrade
                    target_version = fix_engine._determine_safe_image_version(image_name, version)
                    if target_version:
                        print(f"   ✅ Upgrade path: {version} → {target_version}")
                    else:
                        print(f"   ⚠️ No upgrade path for {image_name}:{version}")

                # Generate fix
                fix = await fix_engine._create_container_fix(finding, f"fix-{finding.id}", project_path)
                total_fixes += 1

                if fix.commands and len(fix.commands) > 0:
                    # Check if commands are real (not placeholder)
                    real_commands = [cmd for cmd in fix.commands if not cmd.startswith("echo")]

                    if real_commands:
                        successful_fixes += 1
                        print(f"   ✅ Generated {len(real_commands)} real commands:")
                        for cmd in real_commands[:3]:  # Show first 3
                            print(f"      → {cmd}")

                        # Test Dockerfile finding
                        dockerfiles = await fix_engine._find_dockerfiles(project_path, image_name, version)
                        print(f"   ✅ Found {len(dockerfiles)} Dockerfiles")

                    else:
                        print(f"   ❌ Only placeholder commands generated")
                        print(f"      Status: {fix.status.value}")
                else:
                    print(f"   ❌ No commands generated")

            except Exception as e:
                print(f"   💥 Error: {e}")
                total_fixes += 1

        # Test complete pipeline with vulnerabilities
        print(f"\n🔧 Testing complete pipeline...")

        vulns_as_dicts = []
        for finding in container_findings:
            vulns_as_dicts.append({
                "check_id": f"CONTAINER-{finding.id}",
                "check_name": finding.title,
                "file_path": finding.file_path,
                "resource": "Dockerfile",
                "severity": finding.severity
            })

        # Test with first project
        fix_job = await fix_engine.generate_fixes_for_vulnerabilities(
            vulns_as_dicts[:1],  # Test with alpine first
            alpine_dir
        )

        print(f"✅ Pipeline generated {fix_job.total_fixes} fixes")

        # Results
        success_rate = (successful_fixes / total_fixes) * 100 if total_fixes > 0 else 0

        print(f"\n📊 Container Fix Test Results:")
        print(f"=" * 40)
        print(f"Total container tests: {total_fixes}")
        print(f"Successful fixes: {successful_fixes}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Pipeline fixes: {fix_job.total_fixes}")

        return successful_fixes, total_fixes, success_rate

    finally:
        # Cleanup
        for project_dir in test_projects.values():
            shutil.rmtree(project_dir, ignore_errors=True)

async def test_dockerfile_creation_logic():
    """Test Dockerfile creation when none exists"""

    print("\n" + "="*60)
    print("    Testing Dockerfile Creation Logic")
    print("="*60 + "\n")

    fix_engine = AutomatedFixEngine()

    # Create empty project directory
    empty_dir = tempfile.mkdtemp(prefix="test_empty_")

    try:
        # Test finding without existing Dockerfile
        finding = SecurityFinding(
            id="no-dockerfile",
            severity="high",
            title="alpine:3.15 vulnerabilities",
            description="alpine:3.15 container has security issues",
            file_path=os.path.join(empty_dir, "src", "main.py"),  # Non-dockerfile path
            tool="trivy",
            remediation="Update container"
        )

        print("📝 Testing with empty project directory...")

        # Test Dockerfile creation/finding logic
        dockerfiles = await fix_engine._create_or_find_dockerfiles(
            finding, empty_dir, "alpine", "3.15"
        )

        if dockerfiles:
            print(f"✅ Created/found {len(dockerfiles)} Dockerfiles:")
            for dockerfile in dockerfiles:
                print(f"   → {dockerfile}")
                if os.path.exists(dockerfile):
                    print(f"     ✅ File exists")
                    with open(dockerfile, 'r') as f:
                        content = f.read()
                        if "FROM alpine:3.15" in content:
                            print(f"     ✅ Contains correct base image")
        else:
            print("❌ No Dockerfiles created/found")

        return len(dockerfiles) > 0

    finally:
        shutil.rmtree(empty_dir, ignore_errors=True)

async def main():
    """Run complete container fix tests"""

    print("🚀 Complete Container Fix Implementation Test")
    print("=" * 60)

    # Test with real Dockerfiles
    successful, total, success_rate = await test_container_fixes_with_real_dockerfiles()

    # Test Dockerfile creation
    creation_success = await test_dockerfile_creation_logic()

    print(f"\n🎯 COMPLETE CONTAINER FIX RESULTS")
    print(f"=" * 60)
    print(f"Container fix success rate: {success_rate:.1f}%")
    print(f"Dockerfile creation: {'✅ WORKING' if creation_success else '❌ FAILED'}")

    # Overall assessment
    overall_success = success_rate >= 80 and creation_success

    if overall_success:
        print("✅ CONTAINER FIX HANDLER IS PRODUCTION READY!")
    elif success_rate >= 60:
        print("⚠️ GOOD PROGRESS - minor issues to resolve")
    else:
        print("❌ CONTAINER FIX HANDLER NEEDS MORE WORK")

    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)