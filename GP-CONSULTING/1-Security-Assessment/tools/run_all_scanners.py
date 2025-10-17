#!/usr/bin/env python3
"""
Master Scanner Runner
Runs all security scanners (CI, CD, Runtime) with proper error handling
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime


def run_scanner(script_path: Path) -> tuple:
    """Run a scanner script and return (name, success)"""
    import subprocess

    name = script_path.stem.replace('scan_', '').replace('_', ' ').title()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300
        )

        success = result.returncode == 0

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr and not success:
            print(result.stderr, file=sys.stderr)

        return (name, 'SUCCESS' if success else 'FAILED')

    except subprocess.TimeoutExpired:
        print(f"❌ {name} timeout after 300s")
        return (name, 'TIMEOUT')
    except Exception as e:
        print(f"❌ {name} crashed: {e}")
        return (name, 'CRASHED')


def main():
    parser = argparse.ArgumentParser(description='Run all security scanners')
    parser.add_argument('--ci-only', action='store_true', help='Run only CI scanners')
    parser.add_argument('--cd-only', action='store_true', help='Run only CD scanners')
    parser.add_argument('--runtime-only', action='store_true', help='Run only Runtime scanners')
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║              SECOPS MASTER SCANNER SUITE                     ║
║                                                              ║
║  Comprehensive security scanning across CI/CD/Runtime       ║
╚══════════════════════════════════════════════════════════════╝
""")

    scanner_dir = Path(__file__).parent
    results = {}

    # CI Scanners
    if not args.cd_only and not args.runtime_only:
        print("\n" + "="*60)
        print("CI SCANNERS (Pre-Commit, Git Push)")
        print("="*60 + "\n")

        ci_scanners = [
            scanner_dir / 'ci' / 'scan_code_sast.py',
            scanner_dir / 'ci' / 'scan_secrets.py',
            scanner_dir / 'ci' / 'scan_containers.py',
            scanner_dir / 'ci' / 'scan_dependencies.py'
        ]

        for scanner in ci_scanners:
            if scanner.exists():
                name, status = run_scanner(scanner)
                results[name] = status

    # CD Scanners
    if not args.ci_only and not args.runtime_only:
        print("\n" + "="*60)
        print("CD SCANNERS (Pre-Deployment)")
        print("="*60 + "\n")

        cd_scanners = [
            scanner_dir / 'cd' / 'scan_iac.py',
            scanner_dir / 'cd' / 'scan_kubernetes.py'
        ]

        for scanner in cd_scanners:
            if scanner.exists():
                name, status = run_scanner(scanner)
                results[name] = status

    # Runtime Scanners (bash for now - AWS API calls)
    if not args.ci_only and not args.cd_only:
        print("\n" + "="*60)
        print("RUNTIME SCANNERS (Production Monitoring)")
        print("="*60 + "\n")

        print("⏭️  Runtime scanners use AWS APIs (requires cluster access)")
        print("   Run manually: cd secops/1-scanners/runtime && ./query-*.sh")

    # Final Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60 + "\n")

    for name, status in results.items():
        emoji = {
            'SUCCESS': '✅',
            'FAILED': '❌',
            'TIMEOUT': '⏱️',
            'CRASHED': '💥',
            'SKIPPED': '⏭️'
        }.get(status, '❓')

        print(f"{emoji} {name}: {status}")

    # Statistics
    total = len(results)
    success = sum(1 for s in results.values() if s == 'SUCCESS')
    failed = sum(1 for s in results.values() if s == 'FAILED')

    print(f"\n📊 Statistics:")
    print(f"   Total Scanners: {total}")
    print(f"   ✅ Success: {success}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {(success/total*100) if total > 0 else 0:.1f}%")

    print(f"\n📁 Results saved to: secops/2-findings/raw/")
    print(f"   View with: ls -lh secops/2-findings/raw/")

    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
