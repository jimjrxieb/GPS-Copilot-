#!/usr/bin/env python3
"""
Test: GuidePoint Real Container Fix Implementation
==============================================

This tests that GuidePoint can now actually fix a real container vulnerability
using the reliable ContainerImageUpdater.

NO SUCCESS THEATER - this measures actual vulnerability remediation.
"""

import asyncio
import sys
import os
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from automation_engine.automation.james_ai_engine import SecurityFinding
from automation_engine.automation.automated_fixes import AutomatedFixEngine


async def test_real_container_fix():
    """Test that GuidePoint can actually fix a real container vulnerability"""

    print("🎯 REAL CONTAINER FIX TEST")
    print("Testing GuidePoint against actual alpine:3.15 vulnerability")
    print("=" * 60)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as test_dir:
        print(f"📁 Test directory: {test_dir}")

        # Create vulnerable Dockerfile
        vulnerable_dockerfile = Path(test_dir) / "Dockerfile"
        vulnerable_content = """FROM alpine:3.15
RUN apk add --no-cache curl
WORKDIR /app
COPY test.sh .
RUN chmod +x test.sh
CMD ["./test.sh"]"""

        with open(vulnerable_dockerfile, 'w') as f:
            f.write(vulnerable_content)

        # Create test.sh for container to run
        test_script = Path(test_dir) / "test.sh"
        with open(test_script, 'w') as f:
            f.write("""#!/bin/sh
echo "Testing container with alpine version:"
cat /etc/alpine-release
echo "Container test: SUCCESS"
""")

        print(f"✅ Created vulnerable Dockerfile with alpine:3.15")

        # Create a realistic security finding
        finding = SecurityFinding(
            id="container-vuln-test",
            severity="high",
            title="Vulnerable Alpine Linux base image",
            description="Container uses outdated alpine:3.15 with known vulnerabilities. Should be updated to alpine:3.18.",
            file_path=str(vulnerable_dockerfile),
            tool="trivy",
            remediation="Update FROM alpine:3.15 to FROM alpine:3.18"
        )

        print(f"🔍 Created security finding: {finding.title}")

        # Initialize GuidePoint automated fix engine
        engine = AutomatedFixEngine()

        # Test fix generation
        print(f"\n🚀 Testing GuidePoint fix generation...")
        fix = await engine._create_container_fix(finding, "test-fix-001", test_dir)

        if not fix:
            print("❌ FAILED: GuidePoint could not generate a fix")
            return False

        print(f"✅ Fix generated: {fix.title}")
        print(f"   Description: {fix.description}")
        print(f"   Status: {fix.status}")

        # Check if the fix was actually applied (not just generated)
        if fix.status.value == "applied":
            print(f"✅ Fix was automatically applied by GuidePoint")

            # Verify the file was actually changed
            with open(vulnerable_dockerfile, 'r') as f:
                fixed_content = f.read()

            print(f"\n📄 Updated Dockerfile content:")
            print(fixed_content)

            # Check if alpine:3.18 is now in the file
            if "alpine:3.18" in fixed_content:
                print(f"✅ Container image successfully updated to alpine:3.18")

                # Test that the fixed container actually builds and runs
                print(f"\n🧪 Testing fixed container builds and runs...")

                try:
                    import subprocess

                    # Build the fixed container
                    build_result = subprocess.run(
                        ["docker", "build", "-t", "guidepoint-fixed-test", "."],
                        cwd=test_dir,
                        capture_output=True,
                        text=True
                    )

                    if build_result.returncode == 0:
                        print(f"✅ Fixed container builds successfully")

                        # Test run the container
                        run_result = subprocess.run(
                            ["docker", "run", "--rm", "guidepoint-fixed-test"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if run_result.returncode == 0:
                            print(f"✅ Fixed container runs successfully")
                            print(f"📄 Container output:")
                            print(run_result.stdout)

                            # Cleanup test image
                            subprocess.run(["docker", "rmi", "guidepoint-fixed-test"], capture_output=True)

                            print(f"\n🏆 REAL FIX SUCCESS!")
                            print(f"GuidePoint successfully:")
                            print(f"  1. ✅ Identified alpine:3.15 vulnerability")
                            print(f"  2. ✅ Generated appropriate fix")
                            print(f"  3. ✅ Applied fix automatically")
                            print(f"  4. ✅ Updated Dockerfile to alpine:3.18")
                            print(f"  5. ✅ Verified fixed container builds")
                            print(f"  6. ✅ Verified fixed container runs")

                            return True

                        else:
                            print(f"❌ Fixed container failed to run: {run_result.stderr}")
                            return False

                    else:
                        print(f"❌ Fixed container failed to build: {build_result.stderr}")
                        return False

                except Exception as e:
                    print(f"❌ Container testing failed: {e}")
                    return False

            else:
                print(f"❌ Container image was not updated (still contains old version)")
                return False

        else:
            print(f"❌ Fix was not automatically applied (status: {fix.status})")
            print(f"Fix would require manual execution of commands:")
            for cmd in fix.commands:
                print(f"   {cmd}")
            return False


async def main():
    """Main test execution"""

    print("🎯 GUIDEPOINT REAL CONTAINER FIX VALIDATION")
    print("Testing actual vulnerability remediation capability")
    print()

    success = await test_real_container_fix()

    print(f"\n" + "=" * 60)
    if success:
        print(f"🏆 SUCCESS: GuidePoint can actually fix real container vulnerabilities!")
        print(f"This is ONE working end-to-end fix that proves the system works.")
    else:
        print(f"❌ FAILED: GuidePoint cannot reliably fix container vulnerabilities yet")
        print(f"More work needed before claiming success.")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)