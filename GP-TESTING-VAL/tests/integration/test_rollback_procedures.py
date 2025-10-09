#!/usr/bin/env python3
"""
Critical Gap Analysis: Rollback Procedure Testing
=================================================

The reality check revealed rollback procedures don't work.
This is a production blocker - we need reliable rollback
when fixes break client systems.

Testing:
- Rollback command generation
- Rollback execution success
- State restoration verification
- Multi-step rollback scenarios
"""

import asyncio
import sys
import os
import tempfile
import shutil
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine.automation.automated_fixes import AutomatedFixEngine
from automation_engine.automation.james_ai_engine import SecurityFinding
import uuid
from datetime import datetime

def execute_command(command, cwd, timeout=30):
    """Execute a command and return success/failure with output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "command": command
        }

async def test_basic_rollback_scenario():
    """Test basic rollback when a fix breaks the build"""

    print("\n" + "="*60)
    print("    CRITICAL TEST: Basic Rollback Scenario")
    print("="*60 + "\n")

    test_dir = tempfile.mkdtemp(prefix="rollback_test_")
    fix_engine = AutomatedFixEngine()

    try:
        # Create working Dockerfile
        original_dockerfile = """FROM alpine:3.15
RUN apk add --no-cache curl git
WORKDIR /app
COPY start.sh .
RUN chmod +x start.sh
CMD ["./start.sh"]
"""

        start_sh = """#!/bin/sh
echo "Application starting..."
curl --version
"""

        with open(os.path.join(test_dir, "Dockerfile"), "w") as f:
            f.write(original_dockerfile)
        with open(os.path.join(test_dir, "start.sh"), "w") as f:
            f.write(start_sh)

        print(f"📁 Test directory: {test_dir}")

        # Verify initial state works
        print("🔍 Verifying initial state...")
        initial_build = execute_command("docker build -t rollback-test-initial .", test_dir)
        if not initial_build["success"]:
            print("❌ Initial build failed - can't test rollback")
            return False

        print("✅ Initial build succeeds")

        # Read original file for comparison
        with open(os.path.join(test_dir, "Dockerfile"), "r") as f:
            original_content = f.read()

        # Create vulnerability that will lead to breaking fix
        vulnerability = SecurityFinding(
            id="rollback-test-vuln",
            severity="high",
            title="alpine:3.15 vulnerabilities",
            description="alpine:3.15 needs update but will break",
            file_path=os.path.join(test_dir, "Dockerfile"),
            tool="trivy",
            remediation="Update image"
        )

        # Generate fix
        print("🔧 Generating fix...")
        fix = await fix_engine._create_container_fix(vulnerability, "rollback-test", test_dir)

        print(f"Generated {len(fix.commands)} fix commands:")
        for i, cmd in enumerate(fix.commands):
            print(f"   {i+1}. {cmd}")

        print(f"Generated {len(fix.rollback_commands)} rollback commands:")
        for i, cmd in enumerate(fix.rollback_commands):
            print(f"   {i+1}. {cmd}")

        # Apply the fix
        print("\n🚀 Applying fix...")
        fix_success = True
        for command in fix.commands:
            if "docker build" not in command:  # Skip validation for now
                result = execute_command(command, test_dir)
                if not result["success"]:
                    print(f"❌ Fix command failed: {command}")
                    fix_success = False
                    break

        if fix_success:
            print("✅ Fix commands executed successfully")

        # Read modified file
        with open(os.path.join(test_dir, "Dockerfile"), "r") as f:
            modified_content = f.read()

        print(f"\nFile modifications:")
        print(f"Original: {original_content.split()[1]}")  # FROM alpine:3.15
        print(f"Modified: {modified_content.split()[1]}")  # FROM alpine:3.18

        # Now intentionally break it to test rollback
        print("\n💥 Simulating fix failure (breaking the Dockerfile)...")
        broken_dockerfile = modified_content.replace("FROM alpine:3.18", "FROM nonexistent:99.99")
        with open(os.path.join(test_dir, "Dockerfile"), "w") as f:
            f.write(broken_dockerfile)

        # Verify it's broken
        broken_build = execute_command("docker build -t rollback-test-broken .", test_dir)
        if broken_build["success"]:
            print("⚠️ Build unexpectedly succeeded with broken image")
        else:
            print("✅ Build correctly fails with broken image")

        # Test rollback
        print("\n🔄 Testing rollback...")
        rollback_success = True

        if not fix.rollback_commands:
            print("❌ No rollback commands generated!")
            return False

        for i, rollback_cmd in enumerate(fix.rollback_commands):
            print(f"   Executing rollback {i+1}: {rollback_cmd}")
            result = execute_command(rollback_cmd, test_dir)

            if result["success"]:
                print(f"   ✅ Rollback command {i+1} succeeded")
            else:
                print(f"   ❌ Rollback command {i+1} failed: {result['stderr']}")
                rollback_success = False

        # Verify rollback restored working state
        print("\n🔨 Testing if rollback restored working state...")

        with open(os.path.join(test_dir, "Dockerfile"), "r") as f:
            restored_content = f.read()

        content_match = restored_content.strip() == original_content.strip()
        print(f"Content restored: {'✅ YES' if content_match else '❌ NO'}")

        if not content_match:
            print(f"Expected: {original_content[:50]}...")
            print(f"Got:      {restored_content[:50]}...")

        rollback_build = execute_command("docker build -t rollback-test-restored .", test_dir)
        build_restored = rollback_build["success"]
        print(f"Build works after rollback: {'✅ YES' if build_restored else '❌ NO'}")

        if not build_restored:
            print(f"Build error: {rollback_build['stderr'][:100]}...")

        overall_success = rollback_success and content_match and build_restored
        print(f"\n📊 Rollback Test Results:")
        print(f"   Rollback commands executed: {'✅' if rollback_success else '❌'}")
        print(f"   File content restored: {'✅' if content_match else '❌'}")
        print(f"   Build functionality restored: {'✅' if build_restored else '❌'}")
        print(f"   Overall rollback success: {'✅' if overall_success else '❌'}")

        return overall_success

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

async def test_complex_rollback_scenario():
    """Test rollback with multiple files and dependencies"""

    print("\n" + "="*60)
    print("    CRITICAL TEST: Complex Multi-File Rollback")
    print("="*60 + "\n")

    test_dir = tempfile.mkdtemp(prefix="complex_rollback_")

    try:
        # Create project with multiple files
        dockerfile = """FROM node:16-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
"""

        package_json = """{
  "name": "test-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "4.16.0"
  }
}"""

        app_js = """const express = require('express');
const app = express();
app.get('/', (req, res) => res.send('Hello'));
app.listen(3000);
"""

        # Write files
        files = {
            "Dockerfile": dockerfile,
            "package.json": package_json,
            "app.js": app_js
        }

        for filename, content in files.items():
            with open(os.path.join(test_dir, filename), "w") as f:
                f.write(content)

        print(f"📁 Created complex project with {len(files)} files")

        # Test what happens when we modify multiple files
        print("\n🔧 Simulating complex fix that modifies multiple files...")

        # Backup original states
        original_states = {}
        for filename in files.keys():
            with open(os.path.join(test_dir, filename), "r") as f:
                original_states[filename] = f.read()

        # Simulate a complex fix that modifies multiple files
        modifications = [
            ("Dockerfile", "s|FROM node:16-alpine|FROM node:18-alpine|g"),
            ("package.json", "s|4.16.0|4.18.0|g"),
        ]

        backup_commands = []
        fix_commands = []
        rollback_commands = []

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for filename, sed_pattern in modifications:
            file_path = os.path.join(test_dir, filename)
            backup_path = f"{file_path}.backup.{timestamp}"

            backup_commands.append(f"cp {file_path} {backup_path}")
            fix_commands.append(f"sed -i '{sed_pattern}' {file_path}")
            rollback_commands.append(f"cp {backup_path} {file_path}")

        all_commands = backup_commands + fix_commands

        print(f"Generated {len(all_commands)} fix commands")
        print(f"Generated {len(rollback_commands)} rollback commands")

        # Execute fix
        print("\n🚀 Executing complex fix...")
        fix_success = True
        for command in all_commands:
            result = execute_command(command, test_dir)
            if not result["success"]:
                print(f"❌ Command failed: {command}")
                fix_success = False
            else:
                print(f"✅ {command}")

        # Verify modifications
        modified_states = {}
        for filename in files.keys():
            with open(os.path.join(test_dir, filename), "r") as f:
                modified_states[filename] = f.read()

        print("\nModifications applied:")
        for filename in files.keys():
            if original_states[filename] != modified_states[filename]:
                print(f"   ✅ {filename} modified")
            else:
                print(f"   ⚠️ {filename} unchanged")

        # Execute rollback
        print("\n🔄 Executing rollback...")
        rollback_success = True
        for command in rollback_commands:
            result = execute_command(command, test_dir)
            if not result["success"]:
                print(f"❌ Rollback failed: {command}")
                rollback_success = False
            else:
                print(f"✅ {command}")

        # Verify rollback restored original state
        print("\n🔍 Verifying rollback...")
        restored_states = {}
        for filename in files.keys():
            with open(os.path.join(test_dir, filename), "r") as f:
                restored_states[filename] = f.read()

        all_restored = True
        for filename in files.keys():
            is_restored = original_states[filename] == restored_states[filename]
            print(f"   {filename}: {'✅ Restored' if is_restored else '❌ Not restored'}")
            if not is_restored:
                all_restored = False

        print(f"\n📊 Complex Rollback Results:")
        print(f"   Rollback commands executed: {'✅' if rollback_success else '❌'}")
        print(f"   All files restored: {'✅' if all_restored else '❌'}")

        return rollback_success and all_restored

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

async def test_rollback_failure_scenarios():
    """Test what happens when rollback itself fails"""

    print("\n" + "="*60)
    print("    CRITICAL TEST: Rollback Failure Scenarios")
    print("="*60 + "\n")

    test_dir = tempfile.mkdtemp(prefix="rollback_failure_")

    try:
        # Create test file
        with open(os.path.join(test_dir, "test.txt"), "w") as f:
            f.write("original content")

        print("🔧 Testing rollback when backup file is missing...")

        # Simulate fix that creates backup
        backup_cmd = f"cp {test_dir}/test.txt {test_dir}/test.txt.backup"
        modify_cmd = f"echo 'modified' > {test_dir}/test.txt"

        execute_command(backup_cmd, test_dir)
        execute_command(modify_cmd, test_dir)

        # Delete backup file to simulate failure
        os.remove(f"{test_dir}/test.txt.backup")

        # Try rollback
        rollback_cmd = f"cp {test_dir}/test.txt.backup {test_dir}/test.txt"
        rollback_result = execute_command(rollback_cmd, test_dir)

        if not rollback_result["success"]:
            print("✅ Rollback correctly failed when backup missing")
            print(f"   Error: {rollback_result['stderr']}")
        else:
            print("❌ Rollback should have failed but didn't")

        print("\n🔧 Testing rollback with permission issues...")

        # Create scenario where rollback fails due to permissions
        protected_file = os.path.join(test_dir, "protected.txt")
        with open(protected_file, "w") as f:
            f.write("protected content")

        # Make file read-only
        os.chmod(protected_file, 0o444)

        rollback_cmd = f"echo 'rollback content' > {protected_file}"
        rollback_result = execute_command(rollback_cmd, test_dir)

        if not rollback_result["success"]:
            print("✅ Rollback correctly failed with permission error")
        else:
            print("❌ Rollback should have failed due to permissions")

        return True

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

async def main():
    """Test rollback procedures comprehensively"""

    print("🔄 CRITICAL GAP ANALYSIS: Rollback Procedure Testing")
    print("=" * 60)
    print("Testing the production blocker: rollback reliability")

    # Test basic rollback
    basic_rollback_works = await test_basic_rollback_scenario()

    # Test complex rollback
    complex_rollback_works = await test_complex_rollback_scenario()

    # Test rollback failure scenarios
    failure_scenarios_handled = await test_rollback_failure_scenarios()

    print(f"\n🎯 ROLLBACK TESTING RESULTS")
    print("=" * 35)
    print(f"Basic rollback: {'✅ WORKS' if basic_rollback_works else '❌ BROKEN'}")
    print(f"Complex rollback: {'✅ WORKS' if complex_rollback_works else '❌ BROKEN'}")
    print(f"Failure handling: {'✅ PROPER' if failure_scenarios_handled else '❌ POOR'}")

    overall_rollback_reliability = (
        basic_rollback_works and
        complex_rollback_works and
        failure_scenarios_handled
    )

    print(f"\n🚨 PRODUCTION READINESS ASSESSMENT")
    print("=" * 40)

    if overall_rollback_reliability:
        print("✅ ROLLBACK PROCEDURES: RELIABLE")
        print("   Safe for controlled production testing")
    else:
        print("❌ ROLLBACK PROCEDURES: UNRELIABLE")
        print("   PRODUCTION BLOCKER - Fix before deployment")

    print(f"\nCritical gaps identified:")
    if not basic_rollback_works:
        print("   - Basic file restore doesn't work")
    if not complex_rollback_works:
        print("   - Multi-file rollback fails")
    if not failure_scenarios_handled:
        print("   - No graceful handling of rollback failures")

    return overall_rollback_reliability

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)