#!/usr/bin/env python3
"""
🎯 JAMES TESTING REAL TERRAFORM_CICD_SETUP PROJECT
Direct test from guidepoint directory
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

from simple_guidepoint import JamesWorkingScanner

def test_real_terraform():
    """Test James on the actual moved project"""

    print("🎯 JAMES SCANNING REAL TERRAFORM_CICD_SETUP PROJECT")
    print("=" * 55)

    # Project should be at this location after move
    project_dir = "/home/jimmie/linkops-industries/James-OS/guidepoint/GP-Projects/Terraform_CICD_Setup"

    print(f"📂 Project Location: {project_dir}")

    # Check if directory exists
    if not os.path.exists(project_dir):
        print(f"❌ Project not found at: {project_dir}")
        print("📁 Checking alternative locations...")

        alt_locations = [
            "/home/jimmie/linkops-industries/GP-Projects/Terraform_CICD_Setup",
            "/home/jimmie/linkops-industries/Terraform_CICD_Setup",
            "/home/jimmie/GP-Projects/Terraform_CICD_Setup"
        ]

        for location in alt_locations:
            print(f"   Checking: {location}")
            if os.path.exists(location):
                project_dir = location
                print(f"   ✅ Found at: {location}")
                break
        else:
            print("❌ Project not found at any expected location")
            return False

    print(f"✅ Found project at: {project_dir}")

    # Check terraform files
    tf_files = list(Path(project_dir).glob("**/*.tf"))
    print(f"📁 Found {len(tf_files)} Terraform files:")
    for tf_file in tf_files[:5]:  # Show first 5
        print(f"   - {tf_file.name}")
    if len(tf_files) > 5:
        print(f"   ... and {len(tf_files) - 5} more")

    if not tf_files:
        print("❌ No .tf files found")
        return False

    # Initialize James scanner
    print("\n🔍 INITIALIZING JAMES SCANNER...")
    scanner = JamesWorkingScanner()

    print("✅ James scanner ready")
    print("\n🔍 SCANNING YOUR REAL PROJECT...")
    print("=" * 40)

    try:
        # Scan the actual project
        results = scanner.scan_directory(project_dir, "Terraform_CICD_Setup")

        print("✅ SCAN COMPLETE!")
        print("=" * 20)

        # Display results
        print(f"📊 REAL PROJECT SCAN RESULTS:")
        print(f"   📂 Project: {results['project']}")
        print(f"   📁 Files scanned: {results['files_scanned']}")
        print(f"   🔍 Issues found: {results['james_analysis']['total_findings']}")

        if results['findings']:
            print(f"\n🚨 SECURITY ISSUES IN YOUR REAL PROJECT:")
            for i, finding in enumerate(results['findings'], 1):
                severity_icon = "🚨" if finding['severity'] == "HIGH" else "⚠️" if finding['severity'] == "MEDIUM" else "📝"
                fix_icon = "✅" if finding['remediation_type'] == "automated" else "🤝" if finding['remediation_type'] == "assisted" else "🚨"

                print(f"{i}. {severity_icon} {finding['check_id']}: {finding['description']}")
                print(f"   📁 File: {Path(finding['file']).name}")
                print(f"   🧠 James Confidence: {finding['james_confidence']:.2f}")
                print(f"   {fix_icon} Remediation: {finding['remediation_type']}")
                print()

            james_analysis = results['james_analysis']
            print("🧠 JAMES INTELLIGENCE ON YOUR REAL PROJECT:")
            print(f"   ✅ Automated fixes: {james_analysis['automated_fixes']}")
            print(f"   🤝 Assisted fixes: {james_analysis['assisted_fixes']}")
            print(f"   🚨 Escalated issues: {james_analysis['escalated_issues']}")
            print(f"   📈 Automation rate: {james_analysis['automation_rate']:.1%}")
            print(f"   💼 Business impact: {james_analysis['business_impact']}")

            # Apply fixes
            print(f"\n🔧 APPLYING JAMES FIXES TO YOUR REAL PROJECT...")
            fixes_applied = scanner.apply_fixes(project_dir, results)

            if fixes_applied:
                print("✅ FIXES APPLIED TO YOUR REAL FILES:")
                for fix in fixes_applied:
                    print(f"   {fix}")

                # Rescan to verify
                print(f"\n🔍 RESCANNING TO VERIFY IMPROVEMENTS...")
                rescan_results = scanner.scan_directory(project_dir, "Terraform_CICD_Setup")

                original_count = len(results['findings'])
                remaining_count = len(rescan_results['findings'])
                improvement = ((original_count - remaining_count) / original_count * 100) if original_count > 0 else 0

                print("📊 VERIFICATION RESULTS:")
                print(f"   🎯 Original issues: {original_count}")
                print(f"   ✅ Issues fixed: {original_count - remaining_count}")
                print(f"   🚨 Remaining: {remaining_count}")
                print(f"   📈 Security improvement: {improvement:.1f}%")
            else:
                print("ℹ️  No automated fixes were applied")
        else:
            print("✅ NO SECURITY ISSUES FOUND!")
            print("🎉 Your Terraform_CICD_Setup is already secure!")

        # Save results
        import json
        results_file = f"{project_dir}/james_real_scan_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {results_file}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_terraform()

    if success:
        print(f"\n🎉 SUCCESS!")
        print("✅ James successfully scanned your real Terraform_CICD_Setup")
        print("✅ Applied intelligence to actual infrastructure code")
        print("✅ Ready to fix real security issues in your project")
    else:
        print(f"\n❌ Test failed - check project location and scanner")