#!/usr/bin/env python3
"""
Run All Scans - Clean, Simple, Working
Orchestrates all scanners in one place
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import scanners from current directory
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from checkov_scanner import CheckovScanner
from trivy_scanner import TrivyScanner
from gitleaks_scanner import GitleaksScanner
from bandit_scanner import BanditScanner
from semgrep_scanner import SemgrepScanner
from npm_audit_scanner import NpmAuditScanner
from opa_scanner import OpaScanner
from tfsec_scanner import TfsecScanner
from kubernetes_scanner import KubernetesSecurityScanner

def run_all_scans(target_path: str) -> dict:
    """Run all security scans and consolidate results"""
    target = Path(target_path)
    if not target.exists():
        raise ValueError(f"Target does not exist: {target_path}")

    print(f"🔍 Starting security scans on: {target_path}")

    all_results = {
        "scan_info": {
            "target": target_path,
            "start_time": datetime.now().isoformat(),
            "scanners": []
        },
        "results": {}
    }

    scanners = [
        ("Checkov", CheckovScanner),
        ("Trivy", TrivyScanner),
        ("Gitleaks", GitleaksScanner),
        ("Bandit", BanditScanner),
        ("Semgrep", SemgrepScanner),
        ("NPM Audit", NpmAuditScanner),
        ("OPA", OpaScanner),
        ("TFSec", TfsecScanner)
    ]

    # Run Kubernetes scanner separately (different output format)
    try:
        print("Running Kubernetes Security Suite...")
        k8s_scanner = KubernetesSecurityScanner(target_path)
        k8s_results = k8s_scanner.run_complete_scan()
        all_results["results"]["kubernetes"] = k8s_results
        all_results["scan_info"]["scanners"].append("kubernetes")
        issues = k8s_results.get('total_issues', 0)
        print(f"✅ Kubernetes Security: {issues} issues")
    except Exception as e:
        print(f"⚠️ Kubernetes Security scan failed: {e}")
        all_results["results"]["kubernetes"] = {"error": str(e)}

    # Run all scanners dynamically
    for scanner_name, scanner_class in scanners:
        try:
            print(f"Running {scanner_name}...")
            scanner = scanner_class()
            scanner_results = scanner.scan(target_path)
            scanner_key = scanner_name.lower().replace(" ", "_")
            all_results["results"][scanner_key] = scanner_results
            all_results["scan_info"]["scanners"].append(scanner_key)

            total_count = scanner_results['summary']['total']
            if scanner_name == "Checkov":
                print(f"✅ {scanner_name}: {total_count} issues")
            elif scanner_name == "Trivy":
                print(f"✅ {scanner_name}: {total_count} vulnerabilities")
            elif scanner_name == "Gitleaks":
                print(f"✅ {scanner_name}: {total_count} secrets")
            elif scanner_name == "Bandit":
                print(f"✅ {scanner_name}: {total_count} security issues")
            elif scanner_name == "Semgrep":
                print(f"✅ {scanner_name}: {total_count} code issues")
            elif scanner_name == "NPM Audit":
                print(f"✅ {scanner_name}: {total_count} vulnerabilities")
            elif scanner_name == "OPA":
                print(f"✅ {scanner_name}: {total_count} policy violations")

        except Exception as e:
            print(f"❌ {scanner_name} failed: {e}")
            scanner_key = scanner_name.lower().replace(" ", "_")
            all_results["results"][scanner_key] = {"error": str(e)}

    all_results["scan_info"]["end_time"] = datetime.now().isoformat()

    # Save results
    results_file = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/scans") / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"📁 Results saved to: {results_file}")

    return all_results

def print_summary(results: dict):
    """Print clean summary of all results"""
    print("\n" + "="*60)
    print("🎯 SECURITY SCAN SUMMARY")
    print("="*60)

    total_issues = 0
    for scanner, data in results["results"].items():
        if "error" in data:
            print(f"❌ {scanner.upper()}: Error - {data['error']}")
        else:
            count = data.get("summary", {}).get("total", 0)
            total_issues += count
            print(f"✅ {scanner.upper()}: {count} issues found")

    print(f"\n🔢 TOTAL SECURITY ISSUES: {total_issues}")
    print(f"📊 Scanners run: {', '.join(results['scan_info']['scanners'])}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_all_scans.py <target_path>")
        sys.exit(1)

    try:
        results = run_all_scans(sys.argv[1])
        print_summary(results)
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        sys.exit(1)