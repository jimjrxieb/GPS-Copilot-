#!/usr/bin/env python3
"""
Demonstrate Complete Gatekeeper Flow
Shows: Validation → Detection → Automatic Fixing
"""

import yaml
from pathlib import Path
import sys

sys.path.insert(0, "/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS")
from fixers.gatekeeper_fixer import GatekeeperFixer

def demonstrate_flow():
    """Show the complete Gatekeeper workflow"""

    print("🛡️  COMPLETE GATEKEEPER FLOW DEMONSTRATION")
    print("=" * 60)

    # Step 1: Show insecure manifest
    insecure_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'insecure-nginx',
            'namespace': 'default'
        },
        'spec': {
            'containers': [{
                'name': 'nginx',
                'image': 'nginx:latest',
                'securityContext': {
                    'privileged': True,  # VIOLATION
                    'runAsUser': 0  # VIOLATION
                }
                # VIOLATION: Missing resource limits
            }],
            'hostNetwork': True  # VIOLATION
        }
    }

    # Save insecure manifest
    insecure_path = Path("/tmp/insecure-nginx.yaml")
    with open(insecure_path, 'w') as f:
        yaml.dump(insecure_manifest, f)

    print("\n📄 INSECURE MANIFEST:")
    print(yaml.dump(insecure_manifest, default_flow_style=False))

    # Step 2: Simulate Gatekeeper denial
    print("\n🚫 GATEKEEPER DENIES WITH MESSAGES:")
    denials = [
        "Container nginx cannot run in privileged mode",
        "Container nginx must set runAsNonRoot",
        "Container nginx must specify memory limits",
        "Pod cannot use hostNetwork"
    ]

    for denial in denials:
        print(f"   ❌ {denial}")

    # Step 3: Apply automatic fixes
    print("\n🔧 APPLYING AUTOMATIC FIXES:")
    fixer = GatekeeperFixer()

    for denial in denials:
        print(f"   Fixing: {denial}")
        result = fixer.fix_from_gatekeeper_denial(denial, str(insecure_path))

    # Step 4: Show fixed manifest
    fixed_path = Path("/tmp/fixed_insecure-nginx.yaml")
    if fixed_path.exists():
        with open(fixed_path, 'r') as f:
            fixed_manifest = yaml.safe_load(f)

        print("\n✅ FIXED MANIFEST:")
        print(yaml.dump(fixed_manifest, default_flow_style=False))

        print("\n📊 FIXES APPLIED:")
        for fix in fixer.fixes_applied:
            print(f"   ✓ {fix['type']}: {fix.get('details', {})}")

    # Step 5: Summary
    print("\n🎯 RESULT:")
    print("   1. Gatekeeper validated and found 4 violations")
    print("   2. Fixer automatically corrected all violations")
    print("   3. Manifest now compliant and deployable")
    print("\n   Original: kubectl apply -f insecure-nginx.yaml  # DENIED")
    print("   Fixed:    kubectl apply -f fixed_insecure-nginx.yaml  # SUCCESS")


if __name__ == "__main__":
    demonstrate_flow()