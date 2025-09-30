#!/usr/bin/env python3
"""
Apply All Fixes - Clean, Simple, Working
Orchestrates all fixers based on scan results
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add subdirectories to Python path for imports
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / "IaC-sec"),
    str(current_dir / "Runtime-sec"),
    str(current_dir / "Compliance"),
    str(current_dir / "SAST"),
    str(current_dir / "CKS"),
    str(current_dir)  # For main directory files
])

# Import our production fixers from their organized directories
from unified_terraform_fixer import UnifiedTerraformFixer
from python_fixer import PythonFixer
from npm_audit_fixer import NPMAuditFixer
from trivy_fixer import TrivyFixer
from architectural_escalation_engine import ArchitecturalEscalationEngine

def apply_all_fixes(scan_results_file: str, target_path: str) -> dict:
    """Apply all available fixes based on scan results"""

    with open(scan_results_file, 'r') as f:
        scan_results = json.load(f)

    print(f"🔧 Starting automated fixes for: {target_path}")

    all_fixes = {
        "fix_info": {
            "target": target_path,
            "scan_results_file": scan_results_file,
            "start_time": datetime.now().isoformat(),
            "fixers": []
        },
        "results": {}
    }

    fixers = [
        ("Terraform", UnifiedTerraformFixer),
        ("Python", PythonFixer),
        ("NPM_Audit", NPMAuditFixer),
        ("Trivy", TrivyFixer)
    ]

    total_fixes_applied = 0

    # Run all fixers
    for fixer_name, fixer_class in fixers:
        try:
            print(f"Running {fixer_name} fixer...")
            fixer = fixer_class()
            fixer_results = fixer.apply_fixes(scan_results, target_path)

            fixer_key = fixer_name.lower()
            all_fixes["results"][fixer_key] = fixer_results
            all_fixes["fix_info"]["fixers"].append(fixer_key)

            fixes_count = fixer_results["summary"]["total_fixes"]
            total_fixes_applied += fixes_count
            print(f"✅ {fixer_name}: {fixes_count} fixes applied")

        except Exception as e:
            print(f"❌ {fixer_name} fixer failed: {e}")
            fixer_key = fixer_name.lower()
            all_fixes["results"][fixer_key] = {"error": str(e)}

    # Process escalations for complex architectural findings
    try:
        print("Processing architectural escalations...")
        escalation_engine = ArchitecturalEscalationEngine()
        escalation_results = escalation_engine.process_escalation_findings(scan_results, target_path)

        all_fixes["escalations"] = escalation_results
        if escalation_results["escalation_info"]["total_escalations"] > 0:
            print(f"📋 {escalation_results['escalation_info']['total_escalations']} escalations created for senior team review")
        else:
            print("✅ No architectural escalations required")

    except Exception as e:
        print(f"⚠️ Escalation processing failed: {e}")
        all_fixes["escalations"] = {"error": str(e)}

    all_fixes["fix_info"]["end_time"] = datetime.now().isoformat()

    # Save fix results
    results_file = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/fixes") / f"fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump(all_fixes, f, indent=2)

    print(f"📁 Fix results saved to: {results_file}")

    return all_fixes

def print_summary(results: dict):
    """Print clean summary of all fixes"""
    print("\n" + "="*60)
    print("🔧 AUTOMATED FIX SUMMARY")
    print("="*60)

    total_fixes = 0
    for fixer, data in results["results"].items():
        if "error" in data:
            print(f"❌ {fixer.upper()}: Error - {data['error']}")
        else:
            count = data.get("summary", {}).get("total_fixes", 0)
            total_fixes += count
            print(f"✅ {fixer.upper()}: {count} fixes applied")

    print(f"\n🔧 TOTAL FIXES APPLIED: {total_fixes}")
    print(f"🛠️ Fixers run: {', '.join(results['fix_info']['fixers'])}")

    # Show escalation summary
    if "escalations" in results and results["escalations"].get("escalation_info", {}).get("total_escalations", 0) > 0:
        escalation_count = results["escalations"]["escalation_info"]["total_escalations"]
        print(f"\n📋 ESCALATIONS CREATED: {escalation_count}")
        print("📧 Stakeholder notifications sent for architectural review")
    else:
        print(f"\n📋 ESCALATIONS CREATED: 0")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python apply_all_fixes.py <scan_results.json> <target_path>")
        sys.exit(1)

    try:
        results = apply_all_fixes(sys.argv[1], sys.argv[2])
        print_summary(results)
    except Exception as e:
        print(f"❌ Fix application failed: {e}")
        sys.exit(1)